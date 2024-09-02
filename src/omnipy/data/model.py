from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from contextlib import contextmanager, suppress
import functools
import inspect
import json
import os
import shutil
from textwrap import dedent
from types import GenericAlias, ModuleType, NoneType, UnionType
from typing import (Annotated,
                    Any,
                    Callable,
                    cast,
                    ContextManager,
                    ForwardRef,
                    Generator,
                    Generic,
                    get_args,
                    get_origin,
                    Hashable,
                    Iterator,
                    Literal,
                    Optional,
                    SupportsIndex,
                    Union)

from devtools import debug, PrettyFormat
from pydantic import NoneIsNotAllowedError
from pydantic import Protocol as PydanticProtocol
from pydantic import root_validator, ValidationError
from pydantic.fields import DeferredType, ModelField, Undefined, UndefinedType
from pydantic.generics import GenericModel
from pydantic.main import BaseModel, ModelMetaclass, validate_model
from pydantic.typing import display_as_type, is_none_type
from pydantic.utils import lenient_isinstance, lenient_issubclass, sequence_like
from typing_extensions import TypeVar

from omnipy.api.exceptions import ParamException
from omnipy.api.protocols.private.util import IsSnapshotWrapper
from omnipy.api.typedefs import TypeForm
from omnipy.data.data_class_creator import DataClassBase, DataClassBaseMeta
from omnipy.data.helpers import get_special_methods_info_dict, MethodInfo, YesNoMaybe
from omnipy.util.contexts import (hold_and_reset_prev_attrib_value,
                                  LastErrorHolder,
                                  nothing,
                                  setup_and_teardown_callback_context)
from omnipy.util.decorators import add_callback_after_call, no_context
from omnipy.util.helpers import (all_equals,
                                 all_type_variants,
                                 ensure_plain_type,
                                 evaluate_any_forward_refs_if_possible,
                                 generate_qualname,
                                 get_calling_module_name,
                                 get_default_if_typevar,
                                 get_first_item,
                                 has_items,
                                 is_annotated_plus_optional,
                                 is_non_omnipy_pydantic_model,
                                 is_non_str_byte_iterable,
                                 is_optional,
                                 is_union,
                                 remove_annotated_plus_optional_if_present,
                                 remove_forward_ref_notation,
                                 remove_optional_if_present)
from omnipy.util.setdeque import SetDeque
from omnipy.util.tabulate import tabulate

_KeyT = TypeVar('_KeyT', bound=Hashable)
_ValT = TypeVar('_ValT')
_IterT = TypeVar('_IterT')
_ReturnT = TypeVar('_ReturnT')
_IdxT = TypeVar('_IdxT', bound=SupportsIndex)
_RootT = TypeVar('_RootT', bound=object | None, default=object)
_ModelT = TypeVar('_ModelT')

ROOT_KEY = '__root__'

# TODO: Refactor Dataset and Model using mixins (including below functions)
INTERACTIVE_MODULES = [
    '__main__',
    'IPython.lib.pretty',
    'IPython.core.interactiveshell',
    '_pydevd_bundle.pydevd_asyncio_utils',
    '_pydevd_bundle.pydevd_exec2',
]

_validate_cls_counts: defaultdict[str, int] = defaultdict(int)


def debug_get_sorted_validate_counts() -> dict[str, int]:
    return dict(reversed(sorted(_validate_cls_counts.items(), key=lambda item: item[1])))


def debug_get_total_validate_count() -> int:
    return sum(val for key, val in _validate_cls_counts.items())


def _cleanup_name_qualname_and_module(cls, created_model_or_dataset, model, orig_model):
    if isinstance(model, str):  # ForwardRef
        created_model_or_dataset.__name__ = f'{cls.__name__}[{model}]'
        created_model_or_dataset.__qualname__ = created_model_or_dataset.__name__
    else:
        if created_model_or_dataset.__name__.startswith(f'{cls.__name__}[') \
                and get_origin(model) is Annotated:
            created_model_or_dataset.__name__ = f'{cls.__name__}[{display_as_type(orig_model)}]'
            created_model_or_dataset.__qualname__ = generate_qualname(cls.__qualname__, orig_model)
        else:
            created_model_or_dataset.__qualname__ = generate_qualname(cls.__qualname__, model)

    created_model_or_dataset.__module__ = cls.__module__


def _get_terminal_size() -> os.terminal_size:
    from omnipy.hub.runtime import runtime

    shutil_terminal_size = shutil.get_terminal_size()
    columns = runtime.config.data.terminal_size_columns if runtime else shutil_terminal_size.columns
    lines = runtime.config.data.terminal_size_lines if runtime else shutil_terminal_size.lines

    return os.terminal_size((columns, lines))


def _waiting_for_terminal_repr(new_value: bool | None = None) -> bool:
    from omnipy.hub.runtime import runtime
    if runtime is None:
        return False

    if new_value is not None:
        runtime.objects.waiting_for_terminal_repr = new_value
        return new_value
    else:
        return runtime.objects.waiting_for_terminal_repr


def is_model_instance(__obj: object) -> bool:
    return lenient_isinstance(__obj, Model) \
        and not is_none_type(__obj)  # Consequence of _ModelMetaclass hack


def obj_or_model_contents_isinstance(__obj: object, __class_or_tuple: type) -> bool:
    return isinstance(__obj.contents if is_model_instance(__obj) else __obj, __class_or_tuple)


# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()


class _ModelMetaclass(ModelMetaclass, DataClassBaseMeta):
    # Hack to overcome bug in pydantic/fields.py (v1.10.13), lines 636-641:
    #
    # if origin is None or origin is CollectionsHashable:
    #     # field is not "typing" object eg. Union, dict, list etc.
    #     # allow None for virtual superclasses of NoneType, e.g. Hashable
    #     if isinstance(self.type_, type) and isinstance(None, self.type_):
    #         self.allow_none = True
    #     return
    #
    # This hinders models (including pure pydantic BaseModels) to be properly considered as
    # subfields, e.g. in `list[MyModel]` as `get_origin(MyModel) is None`. Here, we want allow_none
    # to be set to True so that Model is allowed to validate a None value.
    #
    # TODO: Revisit the need for _ModelMetaclass hack in pydantic v2
    def __instancecheck__(self, instance: Any) -> bool:
        if instance is None:
            return True
        return super().__instancecheck__(instance)


class Model(GenericModel, Generic[_RootT], DataClassBase, metaclass=_ModelMetaclass):
    """
    A data model containing a value parsed according to the model.

    If no value is provided, the value is set to the default value of the data model, found by
    calling the model class without parameters, e.g. `int()`.

    Model is a generic class that cannot be instantiated directly. Instead, a Model class needs
    to be specialized with a data type before Model objects can be instantiated. A data model
    functions as a data parser and guarantees that the parsed data follows the specified model.

    Example data model specialized as a class alias::

        MyNumberList = Model[list[int]]

    ... alternatively as a Model subclass::

        class MyNumberList(Model[list[int]]):
            pass

    Once instantiated, a Model object functions as a parser, e.g.::

        my_number_list = MyNumberList([2,3,4])

        my_number_list.contents = ['3', 4, True]
        assert my_number_list.contents == [3,4,1]

    While the following should raise a `ValidationError`::

        my_number_list.contents = ['abc', 'def']

    The Model class is a wrapper class around the powerful `GenericModel` class from pydantic.

    See also docs of the Dataset class for more usage examples.
    """

    __root__: _RootT | None

    class Config:
        arbitrary_types_allowed = True
        validate_all = True
        # validate_assignment = True
        smart_union = True
        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

    @classmethod
    def _get_default_factory_from_model(
            cls, model: type[_RootT] | TypeForm | TypeVar) -> Callable[[], _RootT]:
        default_val = cls._get_default_value_from_model(model)

        def default_factory() -> _RootT:
            return default_val

        return default_factory

    @classmethod
    def _get_default_value_from_model(cls, model: type[_RootT] | TypeForm | TypeVar) -> _RootT:
        model = get_default_if_typevar(model)
        origin_type = get_origin(model)
        args = get_args(model)

        if origin_type is Annotated:
            model = remove_annotated_plus_optional_if_present(model)
            return cls._get_default_value_from_model(model)

        if origin_type in (None, ()):
            origin_type = model

        if origin_type is None:
            origin_type = NoneType

        if origin_type in [Union, UnionType]:
            if any(is_none_type(arg) for arg in args):
                return cast(_RootT, None)

            last_error_holder = LastErrorHolder()
            for arg in args:
                if callable(arg) or isinstance(arg, TypeVar):
                    with last_error_holder:
                        return cls._get_default_value_from_model(arg)
            last_error_holder.raise_derived(TypeError(f'Cannot instantiate model "{model}".'))

        if origin_type is tuple and args and Ellipsis not in args:
            return cast(_RootT, tuple(cls._get_default_value_from_model(arg) for arg in args))

        if origin_type is Literal:
            return args[0]

        if origin_type is ForwardRef or type(origin_type) is ForwardRef:
            raise TypeError(f'Cannot instantiate model "{model}". ')

        return cast(_RootT, origin_type())

    @classmethod
    def _populate_root_field(cls, model: type[_RootT] | TypeVar) -> type[_RootT]:

        default_factory = cls._get_default_factory_from_model(model)

        if ROOT_KEY in cls.__config__.fields:
            cls.__config__.fields[ROOT_KEY]['default_factory'] = default_factory  # type: ignore
        else:
            cls.__config__.fields[ROOT_KEY] = {'default_factory': default_factory}  # type: ignore

        if not get_origin(model) == Annotated and not is_optional(model):
            model = cast(type[_RootT], Annotated[Optional[model], 'Fake Optional from Model'])
        model = cast(type[_RootT], model)  # casting away fake optionals and TypeVar

        data_field = ModelField.infer(
            name=ROOT_KEY,
            value=Undefined,
            annotation=model,
            class_validators=None,
            config=cls.__config__)

        cls.__fields__[ROOT_KEY] = data_field
        cls.__annotations__[ROOT_KEY] = model

        return model

    @classmethod
    def _depopulate_root_field(cls):
        del cls.__config__.fields[ROOT_KEY]
        del cls.__fields__[ROOT_KEY]
        del cls.__annotations__[ROOT_KEY]

    @classmethod
    def _prepare_cls_members_to_mimic_model(cls, created_model: 'Model[type[_RootT]]') -> None:
        outer_type = created_model._get_root_type(outer=True, with_args=True)
        outer_type_plain = created_model._get_root_type(outer=True, with_args=False)

        # TODO: See if it is possible to type Model mimicking of root type, e.g. with Protocol
        if not lenient_issubclass(outer_type_plain, TypeVar):
            if is_union(outer_type) or outer_type_plain is Literal:
                outer_types = get_args(outer_type)
            else:
                outer_types = (outer_type_plain,)

            for name, method_info in get_special_methods_info_dict().items():
                names_to_check = (name, '__add__') if name in ('__iadd__', '__radd__') else (name,)
                for type_to_support in outer_types:
                    for name_to_check in names_to_check:
                        if hasattr(type_to_support, name_to_check):
                            setattr(created_model,
                                    name,
                                    functools.partialmethod(cls._special_method, name, method_info))
                            break
                    else:
                        continue
                    # To let the inner break, also break the outer for loop
                    break

    def __class_getitem__(  # type: ignore[override]
        cls,
        model: type[_RootT] | tuple[type[_RootT]] | tuple[type[_RootT], Any] | TypeVar
    ) -> 'Model[type[_RootT]]':

        # For now, only singular model types are allowed. These lines are needed for
        # interoperability with pydantic GenericModel, which internally stores the model
        # as a tuple:
        if isinstance(model, tuple) and len(model) == 1:
            model = model[0]

        orig_model: type[_RootT] | tuple[type[_RootT], Any] | TypeVar = model

        # Populating the root field at runtime instead of providing a __root__ Field explicitly
        # is needed due to the inability of typing/pydantic to provide a dynamic default based on
        # the actual type. The following issue in mypy seems relevant:
        # https://github.com/python/mypy/issues/3737 (as well as linked issues)
        if cls == Model:  # Only for the base Model class
            model = cls._populate_root_field(cast(type[_RootT], model))
        else:
            # Other subtypes do not support TypeVar anyway
            model = cast(type[_RootT] | tuple[type[_RootT], Any], model)

        created_model = cast(Model, super().__class_getitem__(model))

        if cls != Model:
            with suppress(TypeError):  # E.g. if model type is ForwardRef
                full_type = created_model.full_type()
                root_field = created_model._get_root_field()
                root_field.default_factory = cls._get_default_factory_from_model(full_type)

        # As long as models are not created concurrently, setting the class members temporarily
        # should not have averse effects
        # TODO: Check if we can move to explicit definition of __root__ field at the object
        #       level in pydantic 2.0 (when it is released)
        if cls == Model:
            cls._depopulate_root_field()

        _cleanup_name_qualname_and_module(cls, created_model, model, orig_model)
        cls._prepare_cls_members_to_mimic_model(created_model)

        return created_model

    @classmethod
    def _wrap_with_annotated_optional(cls, model):
        if not get_origin(model) == Annotated \
                and not is_optional(model) \
                and not is_none_type(model):
            prepared_model = cast(type[_RootT],
                                  Annotated[Optional[model], 'Fake Optional from Model'])
        else:
            prepared_model = cast(type[_RootT], model)
        return prepared_model

    @classmethod
    def _add_annotated_optional_hack_to_model(cls, model: 'Model'):
        root_field = model._get_root_field()
        if root_field:
            model = root_field.outer_type_
            if not get_origin(model) == Annotated \
                    and not is_optional(model) \
                    and not is_none_type(model):
                # if not get_origin(model) == Annotated and not is_optional(model):
                root_field.outer_type_ = Annotated[Optional[model], 'Fake Optional from Model']
                root_field.type_ = Optional[model]
                root_field.annotation = root_field.outer_type_
                cls.__annotations__[ROOT_KEY] = root_field.outer_type_

    @classmethod
    def _remove_annotated_optional_hack_from_model(cls, model: 'Model', recursive: bool = False):
        root_field = model._get_root_field()
        if root_field:
            cls._remove_annotated_optional_hack_from_field(root_field, recursive=recursive)
            model.__annotations__[ROOT_KEY] = root_field.outer_type_

    @classmethod
    def _remove_annotated_optional_hack_from_field(cls, field: ModelField, recursive: bool = False):
        if is_annotated_plus_optional(field.outer_type_):
            field.outer_type_ = remove_annotated_plus_optional_if_present(field.outer_type_)
            field.type_ = remove_optional_if_present(field.type_)
            if not isinstance(field.annotation, DeferredType):
                field.annotation = field.outer_type_
        if field.sub_fields and recursive:
            for sub_field in field.sub_fields:
                if sub_field:
                    cls._remove_annotated_optional_hack_from_field(sub_field, recursive=recursive)

    def __new__(cls, value: Any | UndefinedType = Undefined, **kwargs):
        model_not_specified = ROOT_KEY not in cls.__fields__
        if model_not_specified:
            cls._raise_no_model_exception()
        return super().__new__(cls)

    # TODO: Allow e.g. Model[str](Model[int](5)) == Model[str](Model[int](5).contents).
    #       Should then work the same as dataset
    def __init__(
        self,
        value: Any | UndefinedType = Undefined,
        *,
        __root__: Any | UndefinedType = Undefined,
        **kwargs: Any,
    ) -> None:
        super_kwargs: dict[str, _RootT] = {}
        num_root_vals = 0

        if value is not Undefined:
            super_kwargs[ROOT_KEY] = cast(_RootT, value)
            num_root_vals += 1

        if __root__ is not Undefined:
            super_kwargs[ROOT_KEY] = cast(_RootT, __root__)
            num_root_vals += 1

        if kwargs:
            if num_root_vals == 0 or not self.is_param_model():
                super_kwargs[ROOT_KEY] = cast(_RootT, kwargs)
                kwargs = {}
                num_root_vals += 1

        assert num_root_vals <= 1, 'Not allowed to provide root data in more than one argument'

        omnipy_or_pydantic_model_as_input = False
        if ROOT_KEY in super_kwargs:
            omnipy_or_pydantic_model_as_input, value = \
                self._prepare_value_for_validation_if_model(super_kwargs[ROOT_KEY])
            if omnipy_or_pydantic_model_as_input:
                super_kwargs[ROOT_KEY] = cast(_RootT, value)

        self._init(super_kwargs, **kwargs)

        try:
            self._primary_validation(super_kwargs)
        except ValidationError:
            if omnipy_or_pydantic_model_as_input:
                self._secondary_validation_from_data(super_kwargs)
            else:
                raise

        # self._take_snapshot_of_validated_contents()

        if not self.__class__.__doc__:
            self._set_standard_field_description()

    def _primary_validation(self, super_kwargs):
        # Pydantic validation of super_kwargs
        _validate_cls_counts[self.__class__.__name__] += 1
        super().__init__(**super_kwargs)

    def _secondary_validation_from_data(self, super_kwargs):
        super().__init__()
        self.from_data(super_kwargs[ROOT_KEY])

    def _prepare_value_for_validation_if_model(self, value: object) -> tuple[bool, object]:
        if is_model_instance(value):
            return True, cast(Model[_RootT], value).to_data()
        elif is_non_omnipy_pydantic_model(value):
            return True, cast(BaseModel, value).dict(by_alias=True)
        return False, value

    def _init(self, super_kwargs: dict[str, Any], **kwargs: Any) -> None:
        ...

    def __del__(self):
        contents_id = id(self.contents)
        # self.contents = Undefined
        self.snapshot_holder.schedule_deepcopy_content_ids_for_deletion(contents_id)

    @classmethod
    def clone_model_cls(cls: type[_ModelT], model_name: str) -> type[_ModelT]:
        new_model: type[_ModelT] = type(model_name, (cls,), {})
        return new_model

    @staticmethod
    def _raise_no_model_exception() -> None:
        raise TypeError('Note: The Model class requires a concrete model to be specified as '
                        'a type hierarchy within brackets either directly, e.g.:\n\n'
                        '\tmodel = Model[list[int]]([1,2,3])\n\n'
                        'or indirectly in a subclass definition, e.g.:\n\n'
                        '\tclass MyNumberList(Model[list[int]]): ...\n\n')

    def _set_standard_field_description(self) -> None:
        self.__fields__[ROOT_KEY].field_info.description = self._get_standard_field_description()

    @classmethod
    def _get_standard_field_description(cls) -> str:
        return ('This class represents a concrete model for data items in the `omnipy` Python '
                'package. It is a statically typed specialization of the Model class, '
                'which is itself wrapping the excellent Python package named `pydantic`.')

    @classmethod
    def validate(cls: type['Model'], value: Any) -> 'Model':
        """
        Hack to allow overwriting of __iter__ method without compromising pydantic validation. Part
        of the pydantic API and not the Omnipy API.
        """
        # TODO: Doublecheck if validate() method is still needed for pydantic v2

        _validate_cls_counts[cls.__name__] += 1
        if is_model_instance(value):

            @contextmanager
            def temporary_set_value_iter_to_pydantic_method() -> Iterator[None]:
                prev_iter = value.__class__.__iter__
                value.__class__.__iter__ = GenericModel.__iter__

                try:
                    yield
                finally:
                    value.__class__.__iter__ = prev_iter

            with temporary_set_value_iter_to_pydantic_method():
                return super().validate(value)
        else:
            return super().validate(value)

    @classmethod
    def update_forward_refs(cls, **localns: Any) -> None:
        """
        Try to update ForwardRefs on fields based on this Model, globalns and localns.
        """
        super().update_forward_refs(**localns)
        cls.__name__ = remove_forward_ref_notation(cls.__name__)
        cls.__qualname__ = remove_forward_ref_notation(cls.__qualname__)

    def validate_contents(self, restore_snapshot_if_interactive_and_invalid: bool = False) -> None:
        reset_solution = self._prepare_validation_reset_solution_take_snapshot_if_needed()
        with reset_solution:
            self._validate_and_set_value(self.contents, reset_solution=reset_solution)

    def _validate_and_set_value(
            self,
            new_contents: object,
            reset_solution: ContextManager[None] | UndefinedType = Undefined) -> None:

        old_contents_id = id(self.contents)

        def _set_new_contents(contents: object) -> None:
            if id(contents) != old_contents_id:
                self.contents = contents

        self._generic_validate_contents(
            new_contents=new_contents,
            reset_solution=reset_solution,
            post_validation_func=_set_new_contents,
        )

    def _prepare_validation_reset_solution_take_snapshot_if_needed(
        self,
        /,
    ) -> ContextManager[None]:
        if self.config.interactive_mode:
            # TODO: Lazy snapshotting causes unneeded double validation for data that is later
            #       validated for snapshot. Perhaps add a dirty flag to snapshot that can be used to
            #       determine if re-validation is needed? This can also help avoid equality tests, which
            #       might be expensive for large data structures.
            needs_pre_validation = (not self.has_snapshot()
                                    or not self.contents_validated_according_to_snapshot())
            if needs_pre_validation:
                reset_solution = self._get_reset_solution()
                with reset_solution:
                    validated_content = self._validate_contents_from_value(self.contents)
                    if id(validated_content) != id(self.contents):
                        self.contents = validated_content
                    self._take_snapshot_of_validated_contents()

        return self._get_reset_solution()

    def _get_reset_solution(self) -> ContextManager[None]:
        if self.config.interactive_mode and self.has_snapshot():
            return self._get_revert_to_snapshot_reset_solution()
        else:
            return nothing()

    def _get_revert_to_snapshot_reset_solution(self) -> ContextManager[None]:
        prev_deepcopy_content_ids = SetDeque[int]()

        def _setup():
            prev_deepcopy_content_ids.extend(self.snapshot_holder.get_deepcopy_content_ids())

        def _handle_exception():
            new_deepcopy_content_ids = SetDeque[int](
                self.snapshot_holder.get_deepcopy_content_ids())
            new_deepcopy_content_ids.extend(prev_deepcopy_content_ids)
            self.snapshot_holder.schedule_deepcopy_content_ids_for_deletion(
                *new_deepcopy_content_ids)
            # self.contents = self.snapshot_holder.get_snapshot_deepcopy(self)
            from copy import deepcopy
            self.contents = deepcopy(self.snapshot)

        return setup_and_teardown_callback_context(
            setup_func=_setup,
            exception_func=_handle_exception,
        )

    def _generic_validate_contents(
        self,
        /,
        new_contents: object | UndefinedType = Undefined,
        reset_solution: ContextManager[None] | UndefinedType = Undefined,
        post_validation_func: Callable[[_RootT], None] | None = None,
    ) -> None:
        keep_alive_old_contents = self.contents  # To ensure old content ids are not reused

        if reset_solution is Undefined:
            reset_solution = self._prepare_validation_reset_solution_take_snapshot_if_needed()
            with (reset_solution):
                # if pre_validation_func:
                #     return_val = pre_validation_func(*pre_validation_func_args,
                #                                      **pre_validation_func_kwargs)

                # if self.config.interactive_mode and self.has_snapshot() \
                #
                # Following is incorrect, must compare new_contents with snapshot, as self.contents is not
                # yet set
                #         and self.contents_validated_according_to_snapshot():
                #     return return_val

                # if new_contents is Undefined and pre_validation_func:
                #     new_contents = self.contents

                if new_contents is not Undefined:
                    validated_content = self._validate_contents_from_value(new_contents)
                else:
                    validated_content = new_contents
            del reset_solution
        else:
            if new_contents is not Undefined:
                validated_content = self._validate_contents_from_value(new_contents)
            else:
                validated_content = new_contents

        if post_validation_func:
            post_validation_func(validated_content)

        if new_contents is not Undefined:
            del new_contents
            self._take_snapshot_of_validated_contents()

        del keep_alive_old_contents

    def _validate_contents_from_value(
        self,
        value: object,
    ) -> _RootT:
        _is_model, value = self._prepare_value_for_validation_if_model(value)

        values, fields_set, validation_error = validate_model(self.__class__, {ROOT_KEY: value})
        if validation_error:
            raise validation_error

        return values[ROOT_KEY]

    @property
    def snapshot(self) -> _RootT:
        snapshot_wrapper = self._get_snapshot_wrapper()
        assert snapshot_wrapper.id == id(self)
        return snapshot_wrapper.snapshot

    def has_snapshot(self) -> bool:
        return self in self.snapshot_holder

    def _get_snapshot_wrapper(self) -> IsSnapshotWrapper['Model', _RootT]:
        assert self.has_snapshot(), 'No snapshot taken yet'
        return self.snapshot_holder[self]

    def snapshot_taken_of_same_model(self, model: 'Model') -> bool:
        snapshot_wrapper = self._get_snapshot_wrapper()
        return snapshot_wrapper.taken_of_same_obj(model)

    def snapshot_differs_from_model(self, model: 'Model') -> bool:
        snapshot_wrapper = self._get_snapshot_wrapper()
        return snapshot_wrapper.differs_from(model.contents)

    def contents_validated_according_to_snapshot(self) -> bool:
        needs_validation = self.snapshot_differs_from_model(self) \
                           or not self.snapshot_taken_of_same_model(self)
        return not needs_validation

    def _take_snapshot_of_validated_contents(self) -> None:
        if self.config.interactive_mode:
            with self.deepcopy_context(self.snapshot_holder.take_snapshot_setup,
                                       self.snapshot_holder.take_snapshot_teardown):
                self.snapshot_holder.take_snapshot(self)

    @classmethod
    def _parse_data(cls, data: Any) -> _RootT:
        return data

    # TODO: Expand _generous_sequence_support to support iterators, such as dict_keys. Also see if
    #       it is possible to support general mappings in a similar way
    @root_validator(pre=True)
    def _generous_sequence_support(cls, root_obj: dict[str, _RootT | None]) -> Any:
        if ROOT_KEY in root_obj:
            value = root_obj[ROOT_KEY]
            outer_type = cls.outer_type()
            if lenient_issubclass(outer_type, Sequence) \
                    and not lenient_isinstance(value, outer_type) \
                    and isinstance(value, Sequence) \
                    and not sequence_like(value) \
                    and not any(isinstance(value, typ) for typ in (str, bytes)):
                return {ROOT_KEY: [_ for _ in value]}
        return root_obj

    @root_validator
    def _parse_root_object(cls, root_obj: dict[str, _RootT | None]) -> Any:
        assert ROOT_KEY in root_obj
        value = root_obj[ROOT_KEY]
        value = cls._parse_none_value_with_root_type_if_model(value)

        config = cls.data_class_creator.config
        with hold_and_reset_prev_attrib_value(config, 'dynamically_convert_elements_to_models'):
            config.dynamically_convert_elements_to_models = False
            return {ROOT_KEY: cls._parse_data(value)}

    # Partial workaround of https://github.com/pydantic/pydantic/issues/3836, together with
    # fake optional type hack.  See series of relevant tests in test_model.py
    # starting with test_nested_model_classes_none_as_default().
    @classmethod
    def _parse_none_value_with_root_type_if_model(cls, value: _RootT | None) -> _RootT:
        root_field: ModelField = cls._get_root_field()
        root_type = cast(TypeForm, root_field.type_)
        value = cls._parse_with_root_type_if_model(value, root_field, root_type)
        return value

    @classmethod
    def _parse_with_root_type_if_model(cls,
                                       value: _RootT | None,
                                       root_field: ModelField,
                                       root_type: TypeForm) -> _RootT:
        if get_origin(root_type) is Annotated:
            root_type = remove_annotated_plus_optional_if_present(root_type)

        if get_origin(root_type) is Union:
            last_error_holder = LastErrorHolder()
            for arg in get_args(root_type):
                with last_error_holder:
                    return cls._parse_with_root_type_if_model(value, root_field, arg)
            last_error_holder.raise_derived(NoneIsNotAllowedError())

        if lenient_issubclass(root_type, Model):
            root_type = cast(Model[_RootT], root_type)
            if root_field.outer_type_ != root_type:
                outer_type = get_origin(root_field.outer_type_)
                if lenient_issubclass(outer_type, Sequence) and lenient_isinstance(value, Sequence):
                    seq_value = cast(Sequence, value)
                    return outer_type(
                        val if is_model_instance(val) else root_type.parse_obj(val)
                        for val in seq_value)
                elif lenient_issubclass(outer_type, Mapping) and lenient_isinstance(value, Mapping):
                    map_value = cast(Mapping, value)

                    return outer_type({
                        key: val if is_model_instance(val) else root_type.parse_obj(val)
                        for (key, val) in map_value.items()
                    })
            else:
                return cast(_RootT,
                            value if is_model_instance(value) else root_type.parse_obj(value))
        if value is None:
            none_default = root_field.default_factory() is None if root_field.default_factory \
                else root_field.default is None
            root_type_is_none = is_none_type(root_type)
            root_type_is_optional = get_origin(root_type) is Union \
                and any(is_none_type(arg) for arg in get_args(root_type))
            supports_none = none_default or root_type_is_none or root_type_is_optional
            if not supports_none:
                raise NoneIsNotAllowedError()
            value = cast(_RootT, value)

        return value

    @property
    def contents(self) -> _RootT:
        return cast(_RootT, self.__dict__.get(ROOT_KEY))

    @contents.setter
    def contents(self, value: _RootT) -> None:
        super().__setattr__(ROOT_KEY, value)

    def dict(self, *args, **kwargs) -> dict[str, object]:
        return {ROOT_KEY: self.to_data()}

    # TODO: Improve typing of to_data/from_data. Should be limited to JSON types at least, but also
    #       `_RootT` for simple models (without submodels). Handling Submodels is tricky, and may
    #       not be possible, e.g. `Model[list[Model[int]]().to_data()` should be type `list[int]`.
    #       A possibility is to support manually providing proper to_data, e.g. through
    #       Generic Mixin class, e.g.:
    #       ```python
    #       class MyModel(Model[list[Model[int]]], ModelData[list[int]]):
    #          ...
    #       ```
    def to_data(self) -> object:
        return super().dict(by_alias=True)[ROOT_KEY]

    def _empty_from_data(self, value: object) -> None:

        from contextlib import contextmanager

        @contextmanager
        def _reset_to_default(*args, **kwds):
            self.contents = self._get_default_value_from_model(self.full_type())
            yield

        self._validate_and_set_value(value, reset_solution=_reset_to_default())

    def from_data(self, value: object) -> None:
        if self.contents == self._get_default_value_from_model(self.full_type()):
            self._empty_from_data(value)
        else:
            self._validate_and_set_value(value)

    def absorb_and_replace(self, other: 'Model'):
        self.from_data(other.to_data())

    def to_json(self, pretty=True) -> str:
        json_content = self.json()
        if pretty:
            return self._pretty_print_json(json.loads(json_content))
        else:
            return json_content

    def from_json(self, json_contents: str) -> None:
        new_model = self.parse_raw(json_contents, proto=PydanticProtocol.json)
        self.contents = new_model.contents

    @classmethod
    def inner_type(cls, with_args: bool = False) -> TypeForm | None:
        return evaluate_any_forward_refs_if_possible(
            cls._get_root_type(outer=False, with_args=with_args), cls.__module__)

    @classmethod
    def outer_type(cls, with_args: bool = False) -> TypeForm | None:
        return evaluate_any_forward_refs_if_possible(
            cls._get_root_type(outer=True, with_args=with_args), cls.__module__)

    @classmethod
    def full_type(cls) -> TypeForm | None:
        return cls.outer_type(with_args=True)

    @classmethod
    def is_nested_type(cls) -> bool:
        return not cls.inner_type(with_args=True) == cls.outer_type(with_args=True)

    @classmethod
    def is_param_model(cls) -> bool:
        if cls.outer_type() is list:
            type_to_check = cls.inner_type(with_args=True)
        else:
            type_to_check = cls.outer_type(with_args=True)
        args = get_args(type_to_check)
        return is_union(type_to_check) \
            and len(args) >= 2 \
            and lenient_issubclass(args[-1], DataWithParams)

    @classmethod
    def _get_root_field(cls) -> ModelField:
        return cast(ModelField, cls.__fields__.get(ROOT_KEY))

    @classmethod
    def _get_root_type(cls, outer: bool, with_args: bool) -> TypeForm | None:
        root_field = cls._get_root_field()
        root_type = root_field.outer_type_ if outer else root_field.type_
        root_type = remove_annotated_plus_optional_if_present(root_type)
        return root_type if with_args else ensure_plain_type(root_type)

    # @classmethod
    # def create_from_json(cls, data: str | tuple[str]):
    #     if isinstance(data, tuple):
    #         data = data[0]
    #
    #     obj = cls()
    #     obj.from_json(data)
    #     return obj
    #
    # def __reduce__(self):
    #     return self.__class__.create_from_json, (self.to_json(),)

    @classmethod
    def to_json_schema(cls, pretty=True) -> str:
        schema = cls.schema()

        if pretty:
            return cls._pretty_print_json(schema)
        else:
            return json.dumps(schema)

    @staticmethod
    def _pretty_print_json(json_content: Any) -> str:
        return json.dumps(json_content, indent=2)

    def _check_for_root_key(self) -> None:
        if ROOT_KEY not in self.__dict__:
            raise TypeError('The Model class requires the specific model to be specified in as '
                            'a type hierarchy within brackets either directly, e.g.:\n'
                            '\t"model = Model[list[int]]([1,2,3])"\n'
                            'or indirectly in a subclass definition, e.g.:\n'
                            '\t"class MyNumberList(Model[list[int]]): ..."')

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in ['__module__'] + list(self.__dict__.keys()) and attr not in [ROOT_KEY]:
            super().__setattr__(attr, value)
        else:
            if attr in ['contents']:
                contents_prop = getattr(self.__class__, attr)
                old_contents_id = id(contents_prop.__get__(self))
                is_new_contents = id(value) != old_contents_id

                if is_new_contents:
                    contents_prop.__set__(self, value)

                    if self.config.interactive_mode and self.has_snapshot():
                        self.snapshot_holder.schedule_deepcopy_content_ids_for_deletion(
                            old_contents_id)
            else:
                if self._is_non_omnipy_pydantic_model():
                    self._special_method(
                        '__setattr__',
                        MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
                        attr,
                        value)
                else:
                    raise RuntimeError('Model does not allow setting of extra attributes')

    def _special_method(  # noqa: C901
            self, name: str, info: MethodInfo, *args: object, **kwargs: object) -> object:

        if info.state_changing and self.config.interactive_mode:
            # if not self.has_snapshot() or not self.contents_validated_according_to_snapshot():
            #     # self.validate_contents(restore_snapshot_if_interactive_and_invalid=True)
            #     self.validate_contents()

            def _call_special_method_and_return_self_if_inplace(*inner_args: object,
                                                                **inner_kwargs: object) -> object:
                return_val = self._call_special_method(name, *inner_args, **inner_kwargs)

                if id(return_val) == id(self.contents):  # in-place operator, e.g. model += 1
                    return_val = self

                return return_val

            def _set_new_contents(contents: object) -> None:
                self.contents = contents

            reset_solution = self._prepare_validation_reset_solution_take_snapshot_if_needed()
            with reset_solution:
                ret = _call_special_method_and_return_self_if_inplace(*args, **kwargs)
                if ret is NotImplemented:
                    return ret

                self._generic_validate_contents(
                    new_contents=self.contents,
                    reset_solution=reset_solution,
                    post_validation_func=_set_new_contents,
                )

        elif name == '__iter__' and isinstance(self, Iterable):
            _per_element_model_generator = self._get_convert_full_element_model_generator(
                cast(Iterable, self.contents),
                level_up_type_arg_idx=0,
            )
            return _per_element_model_generator()
        else:
            ret = self._call_special_method(name, *args, **kwargs)
            if ret is NotImplemented:
                return ret

            if info.state_changing:
                self.validate_contents()

        if id(ret) != id(self) and info.returns_same_type:
            level_up = False
            if name == '__getitem__':
                assert len(args) == 1
                if not isinstance(args[0], slice):
                    level_up = True

            # We can do this with some ease of mind as all the methods except '__getitem__' with
            # integer argument are supposed to possibly return a result of the same type.
            ret = self._convert_to_model_if_reasonable(
                ret,
                level_up=level_up,
                level_up_arg_idx=-1,
                raise_validation_errors=(info.returns_same_type == YesNoMaybe.YES),
            )

        return ret

    def _call_special_method(self, name: str, *args: object, **kwargs: object) -> object:
        contents = self._get_real_contents()
        has_add_method = hasattr(contents, '__add__')
        has_radd_method = hasattr(contents, '__radd__')
        has_iadd_method = hasattr(contents, '__iadd__')

        if name == '__add__' and has_add_method:

            def _add(other):
                # try:
                #     return contents.__add__(self.__class__(other).contents)
                # except ValidationError:
                return contents.__add__(other)

            # return _add_new_other_model(*args, **kwargs)
            method = _add
            return self._call_single_arg_method_with_model_converted_other_first(
                name, method, *args, **kwargs)

        elif name == '__radd__' and (has_radd_method or has_add_method):

            def _radd(other):
                if has_radd_method:
                    return contents.__radd__(other)
                else:
                    return contents.__add__(other)

            def _radd_model_converted_other(other):
                if has_radd_method:
                    return contents.__radd__(self.__class__(other).contents)
                else:
                    return self.__class__(other).contents.__add__(self.contents)

            method = _radd
            model_converted_other_method = _radd_model_converted_other
            return self._call_single_arg_method_with_model_converted_other_first(
                name,
                method,
                *args,
                model_converted_other_method=model_converted_other_method,
                **kwargs,
            )

        elif name == '__iadd__' and (has_iadd_method or has_add_method):

            def _iadd(other):
                # try:
                #     other_model_contents = self.__class__(other).contents
                #     if has_iadd_method:
                #         return contents.__iadd__(other_model_contents)
                #     else:
                #         self.contents = contents.__add__(other_model_contents)
                #         return self.contents
                # except ValidationError:
                if has_iadd_method:
                    return contents.__iadd__(other)
                else:
                    return contents.__add__(other)

            # return _iadd_new_other_model(*args, **kwargs)
            method = _iadd
            return self._call_single_arg_method_with_model_converted_other_first(
                name, method, *args, **kwargs)
        else:
            try:
                method = cast(Callable, self._getattr_from_contents_obj(name))
            except AttributeError as e:
                if name in ('__int__', '__bool__', '__float__', '__complex__'):
                    raise ValueError from e
                if name == '__len__':
                    raise TypeError(f"object of type '{self.__class__.__name__}' has no len()")
                else:
                    return NotImplemented

            return self._call_method_with_unconverted_args_first(method, *args, **kwargs)

    def _call_single_arg_method_with_model_converted_other_first(
        self,
        name: str,
        method: Callable,
        *args: object,
        model_converted_other_method: Callable | None = None,
        **kwargs: object,
    ):
        if len(args) != 1:
            raise TypeError(f'expected 1 argument, got {len(args)}')

        if len(kwargs) > 0:
            raise TypeError(f'method {name} takes no keyword arguments')

        arg = args[0]

        try:
            try:
                if model_converted_other_method:
                    return model_converted_other_method(arg)
                else:
                    return method(self.__class__(arg).contents, **kwargs)
            except ValidationError:
                # TODO: Add debug logging for hidden validation and other exceptions e.g. when
                #       concatenating `Model[int](123) + '234.'` (gives TypeError:
                #       unsupported operand type(s) for +: 'Model[int]' and 'str'). ?
                #       `Model[int](123) + '234'` works fine, returns `Model[int]('357')`.
                return method(arg)
        except TypeError:
            return NotImplemented

    def _call_method_with_unconverted_args_first(
        self,
        method: Callable,
        *args: object,
        **kwargs: object,
    ):
        try:
            with hold_and_reset_prev_attrib_value(
                    self.config,
                    'dynamically_convert_elements_to_models',
            ):
                self.config.dynamically_convert_elements_to_models = False
                ret = method(*args, **kwargs)
        except TypeError as type_exc:
            try:
                ret = self._call_method_with_model_converted_args(method, *args, **kwargs)
            except ValidationError:
                raise type_exc
        if ret is NotImplemented:
            try:
                ret = self._call_method_with_model_converted_args(method, *args, **kwargs)
            except ValidationError:
                pass
        return ret

    def _call_method_with_model_converted_args(
        self,
        method: Callable,
        *args: object,
        **kwargs: object,
    ):
        model_args = [self.__class__(arg).contents for arg in args]
        return method(*model_args, **kwargs)

    def _get_convert_full_element_model_generator(
            self, elements: Iterable | None,
            level_up_type_arg_idx: int | slice) -> Callable[..., Generator]:
        def _convert_full_element_model_generator(elements=elements):
            for el in elements:
                yield self._convert_to_model_if_reasonable(
                    el,
                    level_up=True,
                    level_up_arg_idx=level_up_type_arg_idx,
                )

        return _convert_full_element_model_generator

    def _get_convert_element_value_model_generator(
            self, elements: Iterable | None) -> Callable[..., Generator]:
        def _convert_element_value_model_generator(elements=elements):
            for el in elements:
                yield (el[0],
                       self._convert_to_model_if_reasonable(
                           el[1],
                           level_up=True,
                           level_up_arg_idx=1,
                       ))

        return _convert_element_value_model_generator

    def _convert_to_model_if_reasonable(  # noqa: C901
        self,
        ret: Mapping[_KeyT, _ValT] | Iterable[_ValT] | _ReturnT | _RootT,
        level_up: bool = False,
        level_up_arg_idx: int = 1,
        raise_validation_errors: bool = False,
    ) -> ('Model[_KeyT] | Model[_ValT] | Model[tuple[_KeyT, _ValT]] '
          '| Model[_ReturnT] | Model[_RootT] | _ReturnT'):

        if level_up and not self.config.dynamically_convert_elements_to_models:
            ...
        elif is_model_instance(ret):
            ...
        else:
            outer_type = self.outer_type(with_args=True)
            # For double Models, e.g. Model[Model[int]], where _get_real_contents() have already
            # skipped the outer Model to get the `ret`, we need to do the same to compare the value
            # with the corresponding type.
            if lenient_issubclass(ensure_plain_type(outer_type), Model):
                outer_type = cast(Model, outer_type).outer_type(with_args=True)

            for type_to_check in all_type_variants(outer_type):
                # TODO: Remove inner_type_to_check loop when Annotated hack is removed with
                #       pydantic v2
                type_to_check = cast(type | GenericAlias,
                                     remove_annotated_plus_optional_if_present(type_to_check))
                for inner_type_to_check in all_type_variants(type_to_check):
                    plain_inner_type_to_check = ensure_plain_type(inner_type_to_check)
                    # if plain_inner_type_to_check in (ForwardRef, TypeVar, Literal, None):
                    if plain_inner_type_to_check in (ForwardRef, TypeVar, None):
                        continue

                    if level_up:
                        inner_type_args = get_args(inner_type_to_check)
                        if len(inner_type_args) == 0:
                            inner_type_args = (inner_type_to_check,)
                        if inner_type_args:
                            for level_up_type_to_check in all_type_variants(
                                    inner_type_args[level_up_arg_idx]):
                                level_up_type_to_check = self._fix_tuple_type_from_args(
                                    level_up_type_to_check)
                                if self._is_instance_or_literal(
                                        ret,
                                        ensure_plain_type(level_up_type_to_check),
                                        level_up_type_to_check,
                                ):
                                    try:
                                        return Model[level_up_type_to_check](ret)  # type: ignore
                                    except ValidationError:
                                        if raise_validation_errors:
                                            raise
                                    except TypeError:
                                        pass

                    else:
                        if self._is_instance_or_literal(
                                ret,
                                plain_inner_type_to_check,
                                inner_type_to_check,
                        ):
                            try:
                                return self.__class__(ret)
                            except ValidationError:
                                if raise_validation_errors:
                                    raise
                            except TypeError:
                                pass

        return cast(_ReturnT, ret)

    @staticmethod
    def _is_instance_or_literal(obj: object, plain_type: type, raw_type: type | GenericAlias):
        if plain_type is Literal:
            args = get_args(raw_type)
            for arg in args:
                if obj == arg:
                    return True
            return False
        else:
            return lenient_isinstance(obj, plain_type)

    def _fix_tuple_type_from_args(
        self, level_up_type_to_check: type | GenericAlias | tuple[type | GenericAlias, ...]
    ) -> type | GenericAlias:
        if isinstance(level_up_type_to_check, tuple):
            match len(level_up_type_to_check):
                case 1:
                    return level_up_type_to_check[0]
                case _:
                    return tuple[level_up_type_to_check]  # type: ignore[valid-type]
        else:
            return level_up_type_to_check

    def __getattr__(self, attr: str) -> Any:
        contents_attr = self._getattr_from_contents_obj(attr)

        reset_solution = self._prepare_validation_reset_solution_take_snapshot_if_needed()

        if self._is_non_omnipy_pydantic_model():
            if self._contents_obj_hasattr(attr):
                self._validate_and_set_value(self.contents, reset_solution=reset_solution)

        is_property = False
        with suppress(AttributeError):
            contents_cls_attr = self._getattr_from_contents_cls(attr)
            is_property = isinstance(contents_cls_attr, property)

        reset_solution = self._prepare_validation_reset_solution_take_snapshot_if_needed()
        contents_attr = self._getattr_from_contents_obj(attr)

        if callable(contents_attr) and not is_property:

            def _validate_contents(ret: Any):
                self._validate_and_set_value(self.contents, reset_solution=reset_solution)
                return ret

            contents_attr = add_callback_after_call(contents_attr,
                                                    _validate_contents,
                                                    reset_solution)

        if attr in ('values', 'items'):
            level_up_arg_idx: int | slice
            match attr:
                case 'values':
                    _model_generator = self._get_convert_full_element_model_generator(
                        None,
                        level_up_type_arg_idx=1,
                    )
                case 'items':
                    _model_generator = self._get_convert_element_value_model_generator(None,)

            contents_attr = add_callback_after_call(contents_attr, _model_generator, no_context)

        return contents_attr

    def _is_non_omnipy_pydantic_model(self) -> bool:
        return is_non_omnipy_pydantic_model(self._get_real_contents())

    def _contents_obj_hasattr(self, attr) -> object:
        return hasattr(self._get_real_contents(), attr)

    def _getattr_from_contents_obj(self, attr) -> object:
        return getattr(self._get_real_contents(), attr)

    def _getattr_from_contents_cls(self, attr) -> object:
        return getattr(self._get_real_contents().__class__, attr)

    def _get_real_contents(self) -> object:
        if is_model_instance(self.contents):
            return self.contents.contents
        else:
            return self.contents

    def __eq__(self, other: object) -> bool:
        return is_model_instance(other) \
            and self.__class__ == other.__class__ \
            and all_equals(self.contents, cast(Model, other).contents)
        # and self.to_data() == cast(Model, other).to_data()  # last line is just in case

    def __repr__(self) -> str:
        if self.config.interactive_mode and not _waiting_for_terminal_repr():
            if get_calling_module_name() in INTERACTIVE_MODULES:
                _waiting_for_terminal_repr(True)
                return self._table_repr()
        return self._trad_repr()

    def __hash__(self) -> int:
        return self._special_method(
            '__hash__', MethodInfo(state_changing=False, returns_same_type=YesNoMaybe.NO))

    def view(self):
        from omnipy.modules.pandas.models import PandasModel
        return PandasModel(self).contents

    def _trad_repr(self) -> str:
        return super().__repr__()

    def __repr_args__(self):
        return [(None, self.contents)]

    def _table_repr(self) -> str:
        from omnipy.data.dataset import Dataset

        outer_type = self.outer_type()
        if inspect.isclass(outer_type) and issubclass(outer_type, Dataset):
            return cast(Dataset, self.contents)._table_repr()

        # tabulate.PRESERVE_WHITESPACE = True  # Does not seem to work together with 'maxcolwidths'

        terminal_size = _get_terminal_size()
        header_column_width = len('(bottom')
        num_columns = 2
        table_chars_width = 3 * num_columns + 1
        data_column_width = terminal_size.columns - table_chars_width - header_column_width

        data_indent = 2
        extra_space_due_to_escaped_chars = 12

        debug_module = cast(ModuleType, inspect.getmodule(debug))
        debug_module.pformat = PrettyFormat(  # type: ignore[attr-defined]
            indent_step=data_indent,
            simple_cutoff=20,
            width=data_column_width - data_indent - extra_space_due_to_escaped_chars,
            yield_from_generators=True,
        )

        structure = str(debug.format(self))
        structure_lines = structure.splitlines()
        new_structure_lines = dedent(os.linesep.join(structure_lines[1:])).splitlines()
        if new_structure_lines[0].startswith('self: '):
            new_structure_lines[0] = new_structure_lines[0][5:]
        max_section_height = (terminal_size.lines - 8) // 2
        structure_len = len(new_structure_lines)

        def _is_table():
            data = self.to_data()
            if is_non_str_byte_iterable(data) and has_items(data):
                first_level_item = get_first_item(data)
                if is_non_str_byte_iterable(first_level_item) and has_items(first_level_item):
                    second_level_item = get_first_item(first_level_item)
                    if not is_non_str_byte_iterable(second_level_item):
                        return True
            return False

        if structure_len > max_section_height * 2 + 1:
            top_structure_end = max_section_height
            bottom_structure_start = structure_len - max_section_height

            top_structure = os.linesep.join(new_structure_lines[:top_structure_end])
            bottom_structure = os.linesep.join(new_structure_lines[bottom_structure_start:])

            out = tabulate(
                (
                    ('#', self.__class__.__name__),
                    (os.linesep.join(str(i) for i in range(top_structure_end)), top_structure),
                    (os.linesep.join(str(i) for i in range(bottom_structure_start, structure_len)),
                     bottom_structure),
                ),
                maxcolwidths=[header_column_width, data_column_width],
                tablefmt='rounded_grid',
            )
        else:
            out = tabulate(
                (
                    ('#', self.__class__.__name__),
                    (os.linesep.join(str(i) for i in range(structure_len)),
                     os.linesep.join(new_structure_lines)),
                ),
                maxcolwidths=[header_column_width, data_column_width],
                tablefmt='rounded_grid',
            )

        _waiting_for_terminal_repr(False)

        return out


_ParamRootT = TypeVar('_ParamRootT', default=object | None)
_KwargValT = TypeVar('_KwargValT', default=object)


class DataWithParams(GenericModel, Generic[_ParamRootT, _KwargValT]):
    data: _ParamRootT
    params: dict[str, _KwargValT]


class ParamModel(Model[_ParamRootT | DataWithParams[_ParamRootT, _KwargValT]],
                 Generic[_ParamRootT, _KwargValT]):
    def _init(self,
              super_kwargs: dict[str, _ParamRootT | DataWithParams[_ParamRootT, _KwargValT]],
              **kwargs: _KwargValT) -> None:
        if kwargs and ROOT_KEY in super_kwargs:
            assert not isinstance(super_kwargs[ROOT_KEY], DataWithParams)
            super_kwargs[ROOT_KEY] = DataWithParams(
                data=cast(_ParamRootT, super_kwargs[ROOT_KEY]), params=kwargs)

    @root_validator
    def _parse_root_object(
            cls, root_obj: dict[str, _ParamRootT | DataWithParams[_ParamRootT, _KwargValT]]) -> Any:
        assert ROOT_KEY in root_obj
        root_val = root_obj[ROOT_KEY]

        params: dict[str, _KwargValT] = {}

        if isinstance(root_val, DataWithParams):
            data = root_val.data
            params = root_val.params
        else:
            data = root_val

        # data = cls._parse_none_value_with_root_type_if_model(data)
        try:
            return {ROOT_KEY: cls._parse_data(data, **params)}
        except TypeError as exc:
            import inspect
            for key in params.keys():
                if key not in inspect.signature(cls._parse_data).parameters:
                    raise ParamException(exc) from None
            raise exc

    @classmethod
    def _parse_data(cls, data: _ParamRootT, **params: _KwargValT) -> _ParamRootT:
        return data

    def from_data(self, value: object, **kwargs: _KwargValT) -> None:
        super().from_data(value)
        if kwargs:
            self._validate_and_set_contents_with_params(cast(_ParamRootT, self.contents), **kwargs)

    def from_json(self, json_contents: str, **kwargs: _KwargValT) -> None:
        super().from_json(json_contents)
        if kwargs:
            self._validate_and_set_contents_with_params(cast(_ParamRootT, self.contents), **kwargs)

    def _validate_and_set_contents_with_params(self, contents: _ParamRootT, **kwargs: _KwargValT):
        self._validate_and_set_value(DataWithParams(data=contents, params=kwargs))


_ParamModelT = TypeVar('_ParamModelT', bound='ParamModel')


class ListOfParamModel(ParamModel[list[_ParamModelT
                                       | DataWithParams[_ParamModelT, _KwargValT]],
                                  _KwargValT],
                       Generic[_ParamModelT, _KwargValT]):
    def _init(
            self,
            super_kwargs: dict[  # type: ignore[override]
                str,
                list[_ParamModelT
                     | DataWithParams[_ParamModelT, _KwargValT]]],
            **kwargs: _KwargValT) -> None:
        if kwargs and ROOT_KEY in super_kwargs:

            def _convert_if_model(data: _ParamModelT) -> _ParamModelT:
                if is_model_instance(data):
                    # Casting to _ParamModelT now, will be validated in super()__init__()
                    return cast(_ParamModelT, cast(Model, data).to_data())
                else:
                    return data

            root_val = cast(list[_ParamModelT], super_kwargs[ROOT_KEY])
            super_kwargs[ROOT_KEY] = [
                DataWithParams(data=_convert_if_model(el), params=kwargs) for el in root_val
            ]

    def _validate_and_set_contents_with_params(
            self,
            contents: list[_ParamModelT | DataWithParams[_ParamModelT, _KwargValT]],
            **kwargs: _KwargValT):
        self._validate_and_set_value([
            DataWithParams(data=cast(_ParamModelT, model).contents, params=kwargs)
            for model in contents
        ])
