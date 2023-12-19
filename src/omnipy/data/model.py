from collections.abc import Mapping, Sequence
import functools
import inspect
import json
import os
import shutil
from textwrap import dedent
from types import UnionType
from typing import (Annotated,
                    Any,
                    cast,
                    Generic,
                    get_args,
                    get_origin,
                    Optional,
                    SupportsIndex,
                    Type,
                    TypeVar,
                    Union)

from devtools import debug, PrettyFormat
from pydantic import NoneIsNotAllowedError
from pydantic import Protocol as PydanticProtocol
from pydantic import root_validator, ValidationError
from pydantic.fields import ModelField, Undefined, UndefinedType
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass, validate_model
from pydantic.typing import display_as_type, is_none_type
from pydantic.utils import lenient_isinstance, lenient_issubclass
from tabulate import tabulate

from omnipy.data.methodinfo import MethodInfo, SPECIAL_METHODS_INFO
from omnipy.util.contexts import AttribHolder, LastErrorHolder, nothing
from omnipy.util.decorators import add_callback_after_call
from omnipy.util.helpers import (all_equals,
                                 ensure_plain_type,
                                 generate_qualname,
                                 get_calling_module_name,
                                 is_optional,
                                 is_union,
                                 remove_annotated_plus_optional_if_present,
                                 remove_forward_ref_notation,
                                 RestorableContents)

_KeyT = TypeVar('_KeyT')
_ValT = TypeVar('_ValT')
_IdxT = TypeVar('_IdxT', bound=SupportsIndex)
RootT = TypeVar('RootT', covariant=True, bound=object)

ROOT_KEY = '__root__'

# TODO: Refactor Dataset and Model using mixins (including below functions)
INTERACTIVE_MODULES = ['__main__', 'IPython.lib.pretty', 'IPython.core.interactiveshell']


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


def _is_interactive_mode() -> bool:
    from omnipy.hub.runtime import runtime
    return runtime.config.data.interactive_mode if runtime else True


def _waiting_for_terminal_repr(new_value: bool | None = None) -> bool:
    from omnipy.hub.runtime import runtime
    if runtime is None:
        return False

    if new_value is not None:
        runtime.objects.waiting_for_terminal_repr = new_value
        return new_value
    else:
        return runtime.objects.waiting_for_terminal_repr


# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()

_restorable_content_cache: dict[int, RestorableContents] = {}


class MyModelMetaclass(ModelMetaclass):
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
    # TODO: Revisit the need for MyModelMetaclass hack in pydantic v2

    def __instancecheck__(self, instance: Any) -> bool:
        if instance is None:
            return True
        return super().__instancecheck__(instance)


class Model(GenericModel, Generic[RootT], metaclass=MyModelMetaclass):
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

    __root__: RootT | None

    class Config:
        arbitrary_types_allowed = True
        validate_all = True
        # validate_assignment = True
        smart_union = True
        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

    @classmethod
    def _get_default_value_from_model(cls, model: Type[RootT]) -> RootT:  # noqa: C901
        if isinstance(model, TypeVar):
            if model.__bound__ is None:  # noqa
                raise TypeError('The TypeVar "{}" needs to be bound to a '.format(model.__name__)
                                + 'type that provides a default value when called')
            else:
                model = model.__bound__  # noqa
        origin_type = get_origin(model)
        args = get_args(model)

        if origin_type is Annotated:
            model = args[0]
            origin_type = get_origin(model)
            args = get_args(model)

        if origin_type in (None, ()):
            origin_type = model

        if origin_type in [Union, UnionType]:
            if any(is_none_type(arg) for arg in args):
                return None

            last_error_holder = LastErrorHolder()
            for arg in args:
                if callable(arg):
                    with last_error_holder:
                        return cls._get_default_value_from_model(arg)
            last_error_holder.raise_derived(TypeError(f'Cannot instantiate model "{model}".'))

        if origin_type is tuple:
            if args and Ellipsis not in args:
                return tuple(cls._get_default_value_from_model(arg) for arg in args)

        return origin_type()

    @classmethod
    def _populate_root_field(cls, model: Type[RootT]) -> None:
        default_val = cls._get_default_value_from_model(model)

        def get_default_val() -> RootT:
            return default_val

        if ROOT_KEY in cls.__config__.fields:
            cls.__config__.fields[ROOT_KEY]['default_factory'] = get_default_val
        else:
            cls.__config__.fields[ROOT_KEY] = {'default_factory': get_default_val}

        if not get_origin(model) == Annotated and not is_optional(model):
            model = Annotated[Optional[model], 'Fake Optional from Model']

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

    def __class_getitem__(cls, model: Type[RootT] | TypeVar) -> Type[RootT] | TypeVar:
        # TODO: change model type to params: Type[Any], tuple[Type[Any], ...]]
        #       as in GenericModel

        # For now, only singular model types are allowed. These lines are needed for
        # interoperability with pydantic GenericModel, which internally stores the model
        # as a tuple:
        if isinstance(model, tuple) and len(model) == 1:
            model = model[0]

        orig_model = model

        # Populating the root field at runtime instead of providing a __root__ Field explicitly
        # is needed due to the inability of typing/pydantic to provide a dynamic default based on
        # the actual type. The following issue in mypy seems relevant:
        # https://github.com/python/mypy/issues/3737 (as well as linked issues)
        if cls == Model:  # Only for the base Model class
            model = cls._populate_root_field(model)

        created_model = super().__class_getitem__(model)

        # As long as models are not created concurrently, setting the class members temporarily
        # should not have averse effects
        # TODO: Check if we can move to explicit definition of __root__ field at the object
        #       level in pydantic 2.0 (when it is released)
        if cls == Model:
            cls._depopulate_root_field()

        _cleanup_name_qualname_and_module(cls, created_model, model, orig_model)

        outer_type = created_model._get_root_type(outer=True, with_args=True)
        outer_type_plain = created_model._get_root_type(outer=True, with_args=False)

        if inspect.isclass(outer_type_plain) or is_union(outer_type):
            for name, method_info in SPECIAL_METHODS_INFO.items():
                outer_types = get_args(outer_type) if is_union(outer_type) else [outer_type_plain]
                for type_to_support in outer_types:
                    if hasattr(type_to_support, name):
                        setattr(created_model,
                                name,
                                functools.partialmethod(cls._special_method, name, method_info))
                        break

        return created_model

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
        **data: Any,
    ) -> None:
        super_data: dict[str, RootT] = {}
        num_root_vals = 0

        if value is not Undefined:
            super_data[ROOT_KEY] = cast(RootT, value)
            num_root_vals += 1

        if __root__ is not Undefined:
            super_data[ROOT_KEY] = cast(RootT, __root__)
            num_root_vals += 1

        if data:
            super_data[ROOT_KEY] = cast(RootT, data)
            num_root_vals += 1

        assert num_root_vals <= 1, 'Not allowed to provide root data in more than one argument'

        if ROOT_KEY in super_data \
                and isinstance(super_data[ROOT_KEY], Model) \
                and not is_none_type(super_data[ROOT_KEY]):  # Consequence of MyModelMetaclass hack
            super_data[ROOT_KEY] = super_data[ROOT_KEY].to_data()

        super().__init__(**super_data)

        self._take_snapshot_of_validated_contents()  # initial snapshot

        if not self.__class__.__doc__:
            self._set_standard_field_description()

    def __del__(self):
        if id(self) in _restorable_content_cache:
            del _restorable_content_cache[id(self)]

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
    def validate(cls: Type['Model'], value: Any) -> 'Model':
        """
        Hack to allow overwriting of __iter__ method without compromising pydantic validation. Part
        of the pydantic API and not the Omnipy API.
        """
        if isinstance(value, Model):
            with AttribHolder(
                    value, '__iter__', GenericModel.__iter__, switch_to_other=True, on_class=True):
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

    def validate_contents(self) -> None:
        self._validate_and_set_contents(self.contents)

    def _validate_and_set_contents(self, new_contents: RootT) -> None:
        self.contents = self._validate_contents_from_value(new_contents)
        self._take_snapshot_of_validated_contents()

    def _validate_contents_from_value(self, value: RootT) -> RootT:
        if isinstance(value, Model) and not is_none_type(value):
            value = value.to_data()
        values, fields_set, validation_error = validate_model(self.__class__, {ROOT_KEY: value})
        if validation_error:
            raise validation_error
        return values[ROOT_KEY]

    def _get_restorable_contents(self):
        if not id(self) in _restorable_content_cache:
            _restorable_content_cache[id(self)] = RestorableContents()
        return _restorable_content_cache.get(id(self))

    def _take_snapshot_of_validated_contents(self):
        interactive_mode = _is_interactive_mode()
        if interactive_mode:
            self._get_restorable_contents().take_snapshot(self.contents)

    @classmethod
    def _parse_data(cls, data: RootT) -> Any:
        return data

    @root_validator
    def _parse_root_object(cls, root_obj: dict[str, RootT]) -> Any:  # noqa
        assert ROOT_KEY in root_obj
        value = root_obj[ROOT_KEY]
        value = cls._parse_none_value_with_root_type_if_model(value)
        return {ROOT_KEY: cls._parse_data(value)}

    # Partial workaround of https://github.com/pydantic/pydantic/issues/3836, together with
    # _propagate_allow_none_from_model().  See series of relevant tests in test_model.py
    # starting with test_nested_model_classes_none_as_default().
    @classmethod
    def _parse_none_value_with_root_type_if_model(cls, value):
        root_field = cls.__fields__.get(ROOT_KEY)
        root_type = root_field.type_
        value = cls._parse_with_root_type_if_model(value, root_field, root_type)
        return value

    @classmethod
    def _parse_with_root_type_if_model(cls, value: Any, root_field: ModelField,
                                       root_type: Type) -> Any:
        if get_origin(root_type) is Annotated:
            root_type = get_args(root_type)[0]

        if get_origin(root_type) is Union:
            last_error_holder = LastErrorHolder()
            for arg in get_args(root_type):
                with last_error_holder:
                    return cls._parse_with_root_type_if_model(value, root_field, arg)
            last_error_holder.raise_derived(NoneIsNotAllowedError())

        if lenient_issubclass(root_type, Model):
            if root_field.outer_type_ != root_type:
                outer_type = get_origin(root_field.outer_type_)
                if lenient_issubclass(outer_type, Sequence) and lenient_isinstance(value, Sequence):
                    return outer_type(
                        root_type.parse_obj(val)
                        if is_none_type(val) or not lenient_isinstance(val, Model) else val
                        for val in value)
                elif lenient_issubclass(outer_type, Mapping) and lenient_isinstance(value, Mapping):
                    return outer_type({
                        key:
                            root_type.parse_obj(val)
                            if is_none_type(val) or not lenient_isinstance(val, Model) else val
                        for (key, val) in value.items()
                    })
            else:
                return root_type.parse_obj(
                    value) if is_none_type(value) or not lenient_isinstance(value, Model) else value
        if value is None:
            none_default = root_field.default_factory() is None if root_field.default_factory \
                else root_field.default is None
            root_type_is_none = is_none_type(root_type)
            root_type_is_optional = get_origin(root_type) is Union \
                and any(is_none_type(arg) for arg in get_args(root_type))
            supports_none = none_default or root_type_is_none or root_type_is_optional
            if not supports_none:
                raise NoneIsNotAllowedError()

        return value

    @property
    def contents(self) -> RootT:
        return self.__dict__.get(ROOT_KEY)

    @contents.setter
    def contents(self, value: RootT) -> None:
        super().__setattr__(ROOT_KEY, value)

    def to_data(self) -> Any:
        return self.dict()[ROOT_KEY]

    def from_data(self, value: object) -> None:
        self._validate_and_set_contents(value)

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

    def inner_type(self, with_args: bool = False) -> type | None:
        return self.__class__._get_root_type(outer=False, with_args=with_args)

    def outer_type(self, with_args: bool = False) -> type | None:
        return self.__class__._get_root_type(outer=True, with_args=with_args)

    def is_nested_type(self) -> bool:
        return not self.inner_type(with_args=True) == self.outer_type(with_args=True)

    @classmethod
    def _get_root_type(cls, outer: bool, with_args: bool) -> type | None:
        root_field = cast(ModelField, cls.__fields__.get(ROOT_KEY))
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
                contents_prop.__set__(self, value)
            else:
                raise RuntimeError('Model does not allow setting of extra attributes')

    def _special_method(self, name: str, info: MethodInfo, *args: object,
                        **kwargs: object) -> object:
        method = self._getattr_from_contents(name)

        if info.state_changing:
            restorable = self._get_restorable_contents()
            if _is_interactive_mode():
                if restorable.has_snapshot() \
                        and restorable.last_snapshot_taken_of_same_obj(self.contents) \
                        and restorable.differs_from_last_snapshot(self.contents):

                    # Current contents not validated
                    reset_contents_to_last_snapshot = AttribHolder(
                        self, 'contents', restorable.get_last_snapshot(), reset_to_other=True)
                    with reset_contents_to_last_snapshot:
                        validated_contents = self._validate_contents_from_value(self.contents)

                    reset_contents_to_validated_prev = AttribHolder(
                        self, 'contents', validated_contents, reset_to_other=True)
                    reset_solution = reset_contents_to_validated_prev
                else:
                    reset_contents_to_prev = AttribHolder(self, 'contents', copy_attr=True)
                    reset_solution = reset_contents_to_prev
            else:
                reset_solution = nothing()

            with reset_solution:
                ret = method(*args, **kwargs)
                if _is_interactive_mode():
                    needs_validation = restorable.differs_from_last_snapshot(self.contents) \
                        if restorable.has_snapshot() else True
                else:
                    needs_validation = True
                if needs_validation:
                    self.validate_contents()
        else:
            ret = method(*args, **kwargs)

        if info.maybe_returns_same_type:
            ret = self._convert_to_model_if_reasonable(args, name, ret)

        return ret

    def _convert_to_model_if_reasonable(self, args, name, ret):
        if not isinstance(ret, self.__class__):
            if name == '__getitem__':
                assert len(args) == 1
                if not isinstance(args[0], slice):
                    # assert self.is_nested_type()
                    # TODO: With Python 3.13 and PEP 649, reconsider the choice to not automatically
                    #       generate nested models through '__getitem__'.
                    #
                    # Seems to work, but the consequences for this are big and requires thought
                    # and consideration.
                    #
                    # try:
                    #     ret = Model[self.inner_type(with_args=True)](ret)
                    # except ValidationError:
                    #     pass
                    return ret

            # We can do this with some ease of mind as all the methods except '__getitem__' with
            # integer argument are supposed to possibly return a result of the same type.
            outer_type = self.outer_type(with_args=True)
            outer_type_plain = self.outer_type()

            types_to_check = get_args(outer_type) if is_union(outer_type) else [outer_type_plain]
            for type_to_check in types_to_check:
                if type_to_check is not None and isinstance(ret, ensure_plain_type(type_to_check)):
                    try:
                        ret = self.__class__(ret)
                    except ValidationError:
                        pass
        return ret

    def __getattr__(self, attr: str) -> Any:
        ret = self._getattr_from_contents(attr)
        if callable(ret):
            contents_holder = AttribHolder(self, 'contents', copy_attr=True)
            context = contents_holder if _is_interactive_mode() else nothing()
            ret = add_callback_after_call(ret, self.validate_contents, with_context=context)
        return ret

    def _getattr_from_contents(self, attr):
        if isinstance(self.contents, Model):
            return getattr(self.contents.contents, attr)
        else:
            return getattr(self.contents, attr)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Model) \
            and self.__class__ == other.__class__ \
            and all_equals(self.contents, other.contents) \
            and self.to_data() == other.to_data()  # last is probably unnecessary, but just in case

    def __repr__(self) -> str:
        if _is_interactive_mode() and not _waiting_for_terminal_repr():
            if get_calling_module_name() in INTERACTIVE_MODULES:
                _waiting_for_terminal_repr(True)
                return self._table_repr
        return self._trad_repr()

    def _trad_repr(self) -> str:
        return super().__repr__()

    def __repr_args__(self):
        return [(None, self.contents)]

    def _table_repr(self) -> str:
        tabulate.PRESERVE_WHITESPACE = True  # Does not seem to work together with 'maxcolwidths'

        terminal_size = shutil.get_terminal_size()
        header_column_width = len('(bottom')
        num_columns = 2
        table_chars_width = 3 * num_columns + 1
        data_column_width = terminal_size.columns - table_chars_width - header_column_width

        data_indent = 2

        inspect.getmodule(debug).pformat = PrettyFormat(
            indent_step=data_indent,
            simple_cutoff=20,
            width=data_column_width - data_indent,
            yield_from_generators=True,
        )

        structure = str(debug.format(self))
        structure_lines = structure.splitlines()
        new_structure_lines = dedent(os.linesep.join(structure_lines[1:])).splitlines()
        if new_structure_lines[0].startswith('self: '):
            new_structure_lines[0] = new_structure_lines[0][5:]
        max_section_height = (terminal_size.lines - 8) // 2
        structure_len = len(new_structure_lines)

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
