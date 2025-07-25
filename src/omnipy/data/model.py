from collections.abc import Callable, Iterable, Mapping, Sequence
from contextlib import contextmanager
from copy import copy, deepcopy
import functools
import inspect
import json
from types import GenericAlias, NoneType, UnionType
from typing import (Annotated,
                    Any,
                    cast,
                    ContextManager,
                    ForwardRef,
                    Generator,
                    Generic,
                    get_args,
                    get_origin,
                    Iterator,
                    Literal,
                    Optional,
                    overload,
                    TYPE_CHECKING,
                    Union)

from typing_extensions import get_original_bases, Self, TypeVar

from omnipy.data._data_class_creator import DataClassBase, DataClassBaseMeta
from omnipy.data._missing import parse_none_according_to_model
from omnipy.data._mixins.display import ModelDisplayMixin
from omnipy.data._typedefs import _KeyT, _ValT, _ValT2
from omnipy.data.helpers import (cleanup_name_qualname_and_module,
                                 get_special_methods_info_dict,
                                 MethodInfo,
                                 ResetSolutionTuple,
                                 validate_cls_counts,
                                 YesNoMaybe)
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.constants import ROOT_KEY
from omnipy.shared.protocols.data import IsModel, IsSnapshotWrapper
from omnipy.shared.typedefs import TypeForm
from omnipy.util._pydantic import (is_none_type,
                                   lenient_isinstance,
                                   lenient_issubclass,
                                   Undefined,
                                   UndefinedType,
                                   ValidationError)
# from orjson import orjson
import omnipy.util._pydantic as pyd
from omnipy.util.contexts import (hold_and_reset_prev_attrib_value,
                                  LastErrorHolder,
                                  nothing,
                                  setup_and_teardown_callback_context)
from omnipy.util.decorators import add_callback_after_call, no_context
from omnipy.util.helpers import (all_equals,
                                 all_type_variants,
                                 ensure_plain_type,
                                 evaluate_any_forward_refs_if_possible,
                                 get_calling_module_name,
                                 get_default_if_typevar,
                                 is_non_omnipy_pydantic_model,
                                 is_non_str_byte_iterable,
                                 is_optional,
                                 is_union,
                                 remove_forward_ref_notation)
from omnipy.util.setdeque import SetDeque

_ReturnT = TypeVar('_ReturnT')
_RootT = TypeVar('_RootT')
_ModelT = TypeVar('_ModelT', bound=IsModel)

# TODO: Refactor Dataset and Model using mixins (including below functions)


class _ModelMetaclass(DataClassBaseMeta, pyd.ModelMetaclass):
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


class Model(
        ModelDisplayMixin,
        DataClassBase,
        pyd.GenericModel,
        Generic[_RootT],
        metaclass=_ModelMetaclass,
):
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

        my_number_list.content = ['3', 4, True]
        assert my_number_list.content == [3,4,1]

    While the following should raise a `ValidationError`::

        my_number_list.content = ['abc', 'def']

    The Model class is a wrapper class around the powerful `GenericModel` class from pydantic.

    See also docs of the Dataset class for more usage examples.
    """

    __root__: _RootT = pyd.Field(default_factory=lambda: Undefined)

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
    def _get_default_value_from_model(  # noqa: C901
            cls,
            model: type[_RootT] | TypeForm | TypeVar,
    ) -> _RootT:
        model = get_default_if_typevar(model)
        origin_type = get_origin(model)
        args = get_args(model)

        if origin_type is Annotated:
            model = args[0]
            origin_type = get_origin(model)
            args = get_args(model)

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

        if origin_type is Callable:
            return cast(_RootT, lambda: None)

        if origin_type is ForwardRef or type(origin_type) is ForwardRef:
            raise TypeError(f'Cannot instantiate model "{model}". ')

        return cast(_RootT, origin_type())

    @classmethod
    def _prepare_cls_members_to_mimic_model(cls, created_model: 'Model[type[_RootT]]') -> None:
        outer_type = created_model.outer_type(with_args=True)
        outer_type_plain = created_model.outer_type(with_args=False)

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
        params: type[_RootT] | tuple[type[_RootT]] | tuple[type[_RootT], Any] | TypeVar
        | tuple[TypeVar, ...],
    ) -> 'Model[type[_RootT]]':

        model = cls._prepare_params(params)

        orig_model: type[_RootT] | tuple[type[_RootT], Any] | TypeVar = model

        # Populating the root field at runtime instead of providing a __root__ Field explicitly
        # is needed due to the inability of typing/pydantic to provide a dynamic default based on
        # the actual type. The following issue in mypy seems relevant:
        # https://github.com/python/mypy/issues/3737 (as well as linked issues)

        created_model = cast(Model, super().__class_getitem__(model if cls == Model else params))

        created_model._get_root_field().field_info = deepcopy(
            created_model._get_root_field().field_info)

        if cls is Model and orig_model is not _RootT:
            created_model._get_root_field().field_info.extra = {'orig_model': orig_model}

        created_model._inherit_first_orig_model_in_bases_if_missing()

        cls._recursively_set_allow_none(created_model._get_root_field())

        # As long as models are not created concurrently, setting the class members temporarily
        # should not have averse effects
        # TODO: Check if we can move to explicit definition of __root__ field at the object
        #       level in pydantic 2.0 (when it is released)

        if created_model is not cls:
            cleanup_name_qualname_and_module(cls, created_model, orig_model)

        if not isinstance(model, TypeVar):
            cls._prepare_cls_members_to_mimic_model(created_model)

        return created_model

    @classmethod
    def _inherit_first_orig_model_in_bases_if_missing(cls):
        if cls is not Model:
            for orig_base in get_original_bases(cls):
                if isinstance(orig_base, _ModelMetaclass) and orig_base.__concrete__:
                    orig_base._inherit_first_orig_model_in_bases_if_missing()
                    orig_model = orig_base.get_orig_model()
                    if orig_model is not Undefined:
                        cls.set_orig_model(orig_model)
                        break

            cls._clean_type_caches()

    # TODO: Add TYPE_CHECKING override for __iter__ method, as BaseModel.__iter__() iterates over
    #       tuples. E.g. `for item in Model[list[int]]([1,2,3]): reveal_type(item)` should reveal
    #       type `int` instead of `tuple[str, Any]`.
    if TYPE_CHECKING:  # noqa: C901
        from ._mimic_models import (Model_bool,
                                    Model_dict,
                                    Model_float,
                                    Model_int,
                                    Model_list,
                                    Model_str,
                                    Model_tuple_all_same,
                                    Model_tuple_pair)

        @overload
        def __new__(
            cls: 'type[Model[float]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_float:
            ...

        @overload
        def __new__(
            cls: 'type[Model[int]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_int:
            ...

        @overload
        def __new__(
            cls: 'type[Model[bool]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_bool:
            ...

        @overload
        def __new__(
            cls: 'type[Model[str]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_str:
            ...

        @overload
        def __new__(
            cls: 'type[Model[list[_ValT]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_list[_ValT]:
            ...

        @overload
        def __new__(
            cls: 'type[Model[tuple[_ValT, _ValT2]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_tuple_pair[_ValT, _ValT2]:
            ...

        @overload
        def __new__(
            cls: 'type[Model[tuple[_ValT, ...]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_tuple_all_same[_ValT]:
            ...

        @overload
        def __new__(
            cls: 'type[Model[dict[_KeyT, _ValT]]]',
            *args: Any,
            **kwargs: Any,
        ) -> Model_dict[_KeyT, _ValT]:
            ...

        @overload
        def __new__(
            cls: 'type[_ModelT]',
            *args: Any,
            **kwargs: Any,
        ) -> '_ModelT':
            ...

        @overload
        def __new__(
            cls: 'type[Model[_RootT]]',
            *args: Any,
            **kwargs: Any,
        ) -> 'Model[_RootT]':
            ...

        def __new__(
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> 'Model':
            ...
    else:

        def __new__(
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> Self:
            model_not_specified = ROOT_KEY not in cls.__fields__
            if model_not_specified:
                cls._raise_no_model_exception()

            return super().__new__(cls)

    @classmethod
    def get_orig_model(cls) -> type[_RootT] | UndefinedType:
        if cls.__fields__[ROOT_KEY].field_info and cls.__fields__[ROOT_KEY].field_info.extra:
            return cls.__fields__[ROOT_KEY].field_info.extra.get('orig_model', Undefined)
        return Undefined

    @classmethod
    def set_orig_model(cls, orig_model: type[_RootT]) -> None:
        cls.__fields__[ROOT_KEY].field_info.extra['orig_model'] = orig_model

    def __init__(  # noqa: C901
        self,
        value: _RootT | object | UndefinedType = Undefined,
        *,
        __root__: _RootT | object | UndefinedType = Undefined,
        **kwargs: _RootT | object,
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
            super_kwargs[ROOT_KEY] = cast(_RootT, kwargs)
            kwargs = {}
            num_root_vals += 1

        assert num_root_vals <= 1, 'Not allowed to provide root data in more than one argument'

        if self._get_root_field().default_factory() is Undefined:
            self._get_root_field().default_factory = self._get_default_factory()

        omnipy_or_pydantic_model_as_input = False
        if ROOT_KEY in super_kwargs:
            try:
                omnipy_or_pydantic_model_as_input, value = \
                    self._prepare_value_for_validation_if_model(super_kwargs[ROOT_KEY])
            except Exception as exc:
                val_exc = ValueError(f'Failed to prepare value for validation: {exc}')
                raise ValidationError(
                    [pyd.ErrorWrapper(exc, loc=ROOT_KEY), pyd.ErrorWrapper(val_exc, loc=ROOT_KEY)],
                    self.__class__)
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

        if not self.__class__.__doc__:
            self._set_standard_field_description()

    def _get_default_factory(self) -> Callable[[], _RootT]:
        return self.__class__._get_default_factory_from_model(self.full_type())

    def _primary_validation(self, super_kwargs):
        # Pydantic validation of super_kwargs
        validate_cls_counts[self.__class__.__name__] += 1
        super().__init__(**super_kwargs)

    def _secondary_validation_from_data(self, super_kwargs):
        super().__init__()
        self.from_data(super_kwargs[ROOT_KEY])

    def _prepare_value_for_validation_if_model(self, value: object) -> tuple[bool, object]:
        if is_model_instance(value):
            return True, cast(Model[_RootT], value).to_data()
        elif is_non_omnipy_pydantic_model(value):
            return True, cast(pyd.BaseModel, value).dict(by_alias=True)
        return False, value

    def _init(self, super_kwargs: dict[str, Any], **kwargs: Any) -> None:
        ...

    def __del__(self):
        content_id = id(self.content)
        self.snapshot_holder.schedule_deepcopy_content_ids_for_deletion(content_id)

    def __copy__(self) -> Self:
        return self.copy(deep=False)

    def copy(self, *, deep: bool = False, **kwargs) -> Self:
        pydantic_copy = pyd.GenericModel.copy(self, deep=deep, **kwargs)
        if not deep:
            pydantic_copy.__dict__[ROOT_KEY] = pydantic_copy.__dict__[ROOT_KEY].copy()
        return cast(Self, pydantic_copy)

    @classmethod
    def clone_model_cls(cls, new_model_cls_name: str) -> Self:
        new_model_cls = type(new_model_cls_name, (cls,), {})
        return cast(Self, new_model_cls)

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

        validate_cls_counts[cls.__name__] += 1
        if is_model_instance(value):

            @contextmanager
            def temporary_set_value_iter_to_pydantic_method() -> Iterator[None]:
                prev_iter = value.__class__.__iter__
                value.__class__.__iter__ = pyd.GenericModel.__iter__

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
        prev_outer_type = cls._get_root_field().outer_type_
        prev_type = cls._get_root_field().type_

        super().update_forward_refs(**localns)

        calling_module = get_calling_module_name()
        cls._get_root_field().outer_type_ = evaluate_any_forward_refs_if_possible(
            prev_outer_type, calling_module, **localns)
        cls._get_root_field().type_ = evaluate_any_forward_refs_if_possible(
            prev_type, calling_module, **localns)
        cls.set_orig_model(
            evaluate_any_forward_refs_if_possible(cls.get_orig_model(), calling_module, **localns))
        cls.__annotations__[ROOT_KEY] = evaluate_any_forward_refs_if_possible(
            cls.__annotations__[ROOT_KEY], calling_module, **localns)

        cls._recursively_set_allow_none(cls._get_root_field())

        cls.__name__ = remove_forward_ref_notation(cls.__name__)
        cls.__qualname__ = remove_forward_ref_notation(cls.__qualname__)

        cls._clean_type_caches()

    def validate_content(self) -> None:
        self._validate_and_set_value(self.content)

    def _validate_and_set_value(
        self,
        new_content: object,
        reset_solution: ContextManager[None] | None = None,
    ) -> None:

        old_content_id = id(self.content)

        def _set_new_content(content: object) -> None:
            if id(content) != old_content_id:
                self.content = content

        self._generic_validate_content(
            new_content=new_content,
            outer_reset_solution=reset_solution,
            post_validation_func=_set_new_content,
        )

    def _prepare_reset_solution_take_snapshot_if_needed(
        self,
        /,
    ) -> ResetSolutionTuple:
        snapshot_taken = False
        if self.config.model.interactive:
            # TODO: Lazy snapshotting causes unneeded double validation for data that is later
            #       validated for snapshot. Perhaps add a dirty flag to snapshot that can be used
            #       to determine if re-validation is needed? This can also help avoid equality
            #       tests, which might be expensive for large data structures.
            needs_pre_validation = (not self.has_snapshot()
                                    or not self.content_validated_according_to_snapshot())
            if needs_pre_validation:
                internal_reset_solution = self._get_reset_solution()
                with internal_reset_solution:
                    self._validate_and_set_value(
                        self.content, reset_solution=internal_reset_solution)
                    snapshot_taken = True

        return ResetSolutionTuple(
            reset_solution=self._get_reset_solution(),
            snapshot_taken=snapshot_taken,
        )

    def _get_reset_solution(self) -> ContextManager[None]:
        if self.config.model.interactive and self.has_snapshot():
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
            # self.content = self.snapshot_holder.get_snapshot_deepcopy(self)
            from copy import deepcopy
            self.content = deepcopy(self.snapshot)

        return setup_and_teardown_callback_context(
            setup_func=_setup,
            exception_func=_handle_exception,
        )

    def _generic_validate_content(
        self,
        /,
        new_content: object,
        outer_reset_solution: ContextManager[None] | None = None,
        post_validation_func: Callable[[_RootT], None] | None = None,
    ) -> None:
        keep_alive_old_content = self.content  # To ensure old content ids are not reused

        inner_reset_solution: ContextManager[None]
        if outer_reset_solution:
            inner_reset_solution = nothing()
        else:
            validating_self = new_content is self.content
            reset_solution_tuple = self._prepare_reset_solution_take_snapshot_if_needed()
            if validating_self and reset_solution_tuple.snapshot_taken:
                return
            inner_reset_solution = reset_solution_tuple.reset_solution

        with (inner_reset_solution):
            validated_content = self._validate_content_from_value(new_content)

            if validated_content is new_content:
                validated_content = copy(validated_content)

            if post_validation_func:
                post_validation_func(validated_content)
        del inner_reset_solution

        del new_content
        self._take_snapshot_of_validated_content()

        del keep_alive_old_content

    def _validate_content_from_value(
        self,
        value: object,
    ) -> _RootT:
        _, value = self._prepare_value_for_validation_if_model(value)

        values, _, validation_error = pyd.validate_model(self.__class__, {ROOT_KEY: value})
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
        return snapshot_wrapper.differs_from(model.content)

    def content_validated_according_to_snapshot(self) -> bool:
        needs_validation = self.snapshot_differs_from_model(self) \
            or not self.snapshot_taken_of_same_model(self)
        return not needs_validation

    def _take_snapshot_of_validated_content(self) -> None:
        if self.config.model.interactive:
            with self.deepcopy_context(self.snapshot_holder.take_snapshot_setup,
                                       self.snapshot_holder.take_snapshot_teardown):
                self.snapshot_holder.take_snapshot(self)

    @classmethod
    def _parse_data(cls, data: Any) -> _RootT:
        return data

    # TODO: Expand _generous_sequence_support to support iterators, such as dict_keys. Also see if
    #       it is possible to support general mappings in a similar way
    @pyd.root_validator(pre=True)
    def _generous_sequence_support(cls, root_obj: dict[str, _RootT | None]) -> Any:
        if ROOT_KEY in root_obj:
            value = root_obj[ROOT_KEY]
            outer_type = cls.outer_type()
            if lenient_issubclass(outer_type, Sequence) \
                    and not lenient_isinstance(value, outer_type) \
                    and isinstance(value, Sequence) \
                    and not pyd.sequence_like(value) \
                    and not any(isinstance(value, typ) for typ in (str, bytes)):
                return {ROOT_KEY: [_ for _ in value]}
        return root_obj

    @pyd.root_validator
    def _parse_root_object(cls, root_obj: dict[str, _RootT | None]) -> Any:
        assert ROOT_KEY in root_obj
        value = root_obj[ROOT_KEY]
        value = parse_none_according_to_model(value, root_model=cls)

        config = cls.data_class_creator.config
        with hold_and_reset_prev_attrib_value(config.model,
                                              'dynamically_convert_elements_to_models'):
            config.model.dynamically_convert_elements_to_models = False
            return {ROOT_KEY: cls._parse_data(value)}

    # TODO: Rename Model.content to Model.content as it may be a single value, while "content"
    #       implies a countable collection of values
    @property
    def content(self) -> _RootT:
        return cast(_RootT, self.__dict__.get(ROOT_KEY))

    @content.setter
    def content(self, value: _RootT) -> None:
        """
        Sets the content of the model. Note: in contrast to the `__init__()`, `from_data()` and
        `from_json()` methods, the content are not validated automatically. To validate the
        content, call the `validate_content()` method explicitly.
        """
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
            self.content = self._get_default_value_from_model(self.full_type())
            yield

        self._validate_and_set_value(value, reset_solution=_reset_to_default())

    def from_data(self, data: Any) -> None:
        if self.content == self._get_default_value_from_model(self.full_type()):
            self._empty_from_data(data)
        else:
            self._validate_and_set_value(data)

    def absorb_and_replace(self, other: 'Model'):
        self.from_data(other.to_data())

    def to_json(self, pretty=True) -> str:
        json_content = self.json()
        if pretty:
            return self._pretty_print_json(json.loads(json_content))
        else:
            return json_content

    def from_json(self, json_content: str) -> None:
        new_model = self.parse_raw(json_content, proto=pyd.Protocol.json)
        self.content = new_model.content

    @classmethod
    @functools.cache
    def inner_type(cls, with_args: bool = False) -> TypeForm:
        return cls._get_root_type(outer=False, with_args=with_args)

    @classmethod
    @functools.cache
    def outer_type(cls, with_args: bool = False) -> TypeForm:
        return cls._get_root_type(outer=True, with_args=with_args)

    @classmethod
    @functools.cache
    def full_type(cls) -> type[_RootT]:
        return cast(type[_RootT], cls.outer_type(with_args=True))

    @classmethod
    @functools.cache
    def is_nested_type(cls) -> bool:
        return not cls.inner_type(with_args=True) == cls.outer_type(with_args=True)

    @classmethod
    def _clean_type_caches(cls):
        cls.outer_type.cache_clear()
        cls.inner_type.cache_clear()
        cls.full_type.cache_clear()
        cls.is_nested_type.cache_clear()

    @classmethod
    def _get_root_field(cls) -> pyd.ModelField:
        return cast(pyd.ModelField, cls.__fields__.get(ROOT_KEY))

    @classmethod
    def _get_root_type(cls, outer: bool, with_args: bool) -> TypeForm:
        root_field = cls._get_root_field()
        root_type = root_field.outer_type_ if outer else root_field.type_

        orig_model = cls.get_orig_model()
        if orig_model != Undefined:
            if not is_optional(root_type) and is_optional(orig_model):
                if outer:
                    root_type = Optional[root_type]
                else:
                    root_type = Optional[root_field.outer_type_]

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
        if 'orig_model' in schema:
            del schema['orig_model']

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
            match (attr):
                case 'content':
                    content_prop = getattr(self.__class__, attr)
                    old_content_id = id(content_prop.__get__(self))
                    is_new_content = id(value) != old_content_id

                    if is_new_content:
                        content_prop.__set__(self, value)

                        if self.config.model.interactive and self.has_snapshot():
                            self.snapshot_holder.schedule_deepcopy_content_ids_for_deletion(
                                old_content_id)
                case 'repr_state':
                    prop = getattr(self.__class__, attr)
                    prop.__set__(self, value)
                case _:
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

        if info.state_changing and self.config.model.interactive:

            def _call_special_method_and_return_self_if_inplace(*inner_args: object,
                                                                **inner_kwargs: object) -> object:
                return_val = self._call_special_method(name, *inner_args, **inner_kwargs)

                if id(return_val) == id(self.content):  # in-place operator, e.g. model += 1
                    return_val = self

                return return_val

            reset_solution = self._prepare_reset_solution_take_snapshot_if_needed().reset_solution
            with reset_solution:
                ret = _call_special_method_and_return_self_if_inplace(*args, **kwargs)
                if ret is NotImplemented:
                    return ret

                self._validate_and_set_value(
                    new_content=self.content,
                    reset_solution=reset_solution,
                )

        elif name == '__iter__' and isinstance(self, Iterable):
            _per_element_model_generator = self._get_convert_full_element_model_generator(
                cast(Iterable, self.content),
                level_up_type_arg_idx=0,
            )
            return _per_element_model_generator()
        else:
            ret = self._call_special_method(name, *args, **kwargs)
            if ret is NotImplemented:
                return ret

            if info.state_changing:
                self.validate_content()

        if id(ret) != id(self) and info.returns_same_type:
            level_up = False
            if name == '__getitem__':
                assert len(args) == 1
                if not isinstance(args[0], slice) and not is_non_str_byte_iterable(args[0]):
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

    def _call_special_method(  # noqa: C901
            self,
            name: str,
            *args: object,
            **kwargs: object,
    ) -> object:
        content = self._get_real_content()
        has_add_method = hasattr(content, '__add__')
        has_radd_method = hasattr(content, '__radd__')
        has_iadd_method = hasattr(content, '__iadd__')

        if name == '__add__' and has_add_method:

            def _add(other):
                # try:
                #     return content.__add__(self.__class__(other).content)
                # except ValidationError:
                return content.__add__(other)

            # return _add_new_other_model(*args, **kwargs)
            method = _add
            return self._call_single_arg_method_with_model_converted_other_first(
                name, method, *args, **kwargs)

        elif name == '__radd__' and (has_radd_method or has_add_method):

            def _radd(other):
                if has_radd_method:
                    return content.__radd__(other)
                else:
                    return content.__add__(other)

            def _radd_model_converted_other(other):
                if has_radd_method:
                    return content.__radd__(self.__class__(other).content)
                else:
                    return self.__class__(other).content.__add__(self.content)

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
                if has_iadd_method:
                    return content.__iadd__(other)
                else:
                    return content.__add__(other)

            method = _iadd
            return self._call_single_arg_method_with_model_converted_other_first(
                name, method, *args, **kwargs)
        else:
            try:
                method = cast(Callable, self._getattr_from_content_obj(name))
            except AttributeError as e:
                if name in ('__int__', '__float__', '__complex__'):
                    raise ValueError from e
                if name == '__len__':
                    raise TypeError(f"object of type '{self.__class__.__name__}' has no len()")
                else:
                    return NotImplemented

            if name == '__hash__' and method is None:
                raise TypeError(f'unhashable type: {self.__class__.__name__}')

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
                    return method(self.__class__(arg).content, **kwargs)
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
                    self.config.model,
                    'dynamically_convert_elements_to_models',
            ):
                self.config.model.dynamically_convert_elements_to_models = False
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
        model_args = [self.__class__(arg).content for arg in args]
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
                yield (
                    el[0],
                    self._convert_to_model_if_reasonable(
                        el[1],
                        level_up=True,
                        level_up_arg_idx=1,
                    ),
                )

        return _convert_element_value_model_generator

    def _convert_to_model_if_reasonable(  # noqa: C901
        self,
        ret: Mapping[_KeyT, _ValT] | Iterable[_ValT] | _ReturnT | _RootT,
        level_up: bool = False,
        level_up_arg_idx: int = 1,
        raise_validation_errors: bool = False,
    ) -> ('Model[_KeyT] | Model[_ValT] | Model[tuple[_KeyT, _ValT]] '
          '| Model[_ReturnT] | Model[_RootT] | _ReturnT'):

        if level_up and not self.config.model.dynamically_convert_elements_to_models:
            ...
        elif is_model_instance(ret):
            ...
        else:
            outer_type = self.outer_type(with_args=True)
            # For double Models, e.g. Model[Model[int]], where _get_real_content() have already
            # skipped the outer Model to get the `ret`, we need to do the same to compare the value
            # with the corresponding type.
            if lenient_issubclass(ensure_plain_type(outer_type), Model):
                outer_type = cast(Model, outer_type).outer_type(with_args=True)

            for type_to_check in all_type_variants(outer_type):
                plain_type_to_check = ensure_plain_type(type_to_check)
                if plain_type_to_check in (ForwardRef, TypeVar, None):
                    continue

                if level_up:
                    type_args = get_args(type_to_check)
                    if len(type_args) == 0:
                        type_args = (type_to_check,)
                    if type_args:
                        for level_up_type_to_check in all_type_variants(
                                type_args[level_up_arg_idx]):
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
                            plain_type_to_check,
                            type_to_check,
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
        if self._is_non_omnipy_pydantic_model() and self._content_obj_hasattr(attr):
            self._validate_and_set_value(self.content)

        content_attr = self._getattr_from_content_obj(attr)

        if inspect.isroutine(content_attr):
            reset_solution = self._prepare_reset_solution_take_snapshot_if_needed().reset_solution
            new_content_attr = self._getattr_from_content_obj(attr)

            def _validate_content(ret: Any):
                self._validate_and_set_value(self.content, reset_solution=reset_solution)
                return self._convert_to_model_if_reasonable(
                    ret,
                    level_up=False,
                    raise_validation_errors=False,
                )

            content_attr = add_callback_after_call(new_content_attr,
                                                   _validate_content,
                                                   reset_solution)

        if attr in ('values', 'items'):
            match attr:
                case 'values':
                    _model_generator = self._get_convert_full_element_model_generator(
                        None,
                        level_up_type_arg_idx=1,
                    )
                case 'items':
                    _model_generator = self._get_convert_element_value_model_generator(None,)

            content_attr = add_callback_after_call(content_attr, _model_generator, no_context)

        return content_attr

    def _is_non_omnipy_pydantic_model(self) -> bool:
        return is_non_omnipy_pydantic_model(self._get_real_content())

    def _content_obj_hasattr(self, attr) -> object:
        return hasattr(self._get_real_content(), attr)

    def _getattr_from_content_obj(self, attr) -> object:
        return getattr(self._get_real_content(), attr)

    def _getattr_from_content_cls(self, attr) -> object:
        return getattr(self._get_real_content().__class__, attr)

    def _get_real_content(self) -> object:
        if is_model_instance(self.content):
            return self.content.content
        else:
            return self.content

    def __eq__(self, other: object) -> bool:
        return is_model_instance(other) \
            and self.__class__ == other.__class__ \
            and all_equals(self.content, cast(Model, other).content)
        # and self.to_data() == cast(Model, other).to_data()  # last line is just in case

    def __bool__(self):
        if self._get_real_content():
            return True
        else:
            return False

    def __call__(self, *args: object, **kwargs: object) -> object:
        if not hasattr(self._get_real_content(), '__call__'):
            raise TypeError(f"'{self.__class__.__name__}' object is not callable")
        return self._special_method(
            '__call__',
            MethodInfo(state_changing=True, returns_same_type=YesNoMaybe.NO),
            *args,
            **kwargs)

    def __repr_args__(self):
        return [(None, self.content)]
