from collections.abc import Mapping, Sequence
import functools
import inspect
import json
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

from isort import place_module
from isort.sections import STDLIB
# from orjson import orjson
from pydantic import NoneIsNotAllowedError
from pydantic import Protocol as pydantic_protocol
from pydantic import root_validator, ValidationError
from pydantic.fields import ModelField, Undefined, UndefinedType
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass
from pydantic.typing import display_as_type, is_none_type
from pydantic.utils import lenient_isinstance, lenient_issubclass

from omnipy.data.methodinfo import MethodInfo, SPECIAL_METHODS_INFO
from omnipy.util.contexts import AttribHolder, LastErrorHolder
from omnipy.util.decorators import add_callback_after_call
from omnipy.util.helpers import is_optional, is_union, remove_annotated_plus_optional_if_present

_KeyT = TypeVar('_KeyT')
_ValT = TypeVar('_ValT')
_IdxT = TypeVar('_IdxT', bound=SupportsIndex)
RootT = TypeVar('RootT', covariant=True, bound=object)

ROOT_KEY = '__root__'

# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()


def generate_qualname(cls_name: str, model: Any) -> str:
    m_module = model.__module__ if hasattr(model, '__module__') else ''
    m_module_prefix = f'{m_module}.' \
        if m_module and place_module(m_module) != STDLIB else ''
    fully_qual_model_name = f'{m_module_prefix}{display_as_type(model)}'
    return f'{cls_name}[{fully_qual_model_name}]'


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
        validate_assignment = True
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

        # cls._propagate_allow_none_from_model(model, created_model)

        # As long as models are not created concurrently, setting the class members temporarily
        # should not have averse effects
        # TODO: Check if we can move to explicit definition of __root__ field at the object
        #       level in pydantic 2.0 (when it is released)
        if cls == Model:
            cls._depopulate_root_field()

        if created_model.__name__.startswith('Model[') and get_origin(model) is Annotated:
            created_model.__name__ = f'Model[{display_as_type(orig_model)}]'
        created_model.__qualname__ = generate_qualname(cls.__name__, model)

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

        super().__init__(**super_data)

        if not self.__class__.__doc__:
            self._set_standard_field_description()

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
            with AttribHolder(value, '__iter__', GenericModel.__iter__, on_class=True):
                return super().validate(value)
        else:
            return super().validate(value)

    def validate_contents(self):
        self.contents = self.contents

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
                    return outer_type(  # type: ignore
                        root_type.parse_obj(val)
                        if is_none_type(val) or not lenient_isinstance(val, Model) else val
                        for val in value)
                elif lenient_issubclass(outer_type, Mapping) and lenient_isinstance(value, Mapping):
                    return outer_type({  # type: ignore
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

    def from_data(self, value: Any) -> None:
        self.contents = value

    def to_json(self, pretty=False) -> str:
        json_content = self.json()
        if pretty:
            return self._pretty_print_json(json.loads(json_content))
        else:
            return json_content

    def from_json(self, json_contents: str) -> None:
        new_model = self.parse_raw(json_contents, proto=pydantic_protocol.json)
        self._set_contents_without_validation(new_model)

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
        if get_args(root_type):
            return root_type if with_args else get_origin(root_type)
        return root_type

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

    def _set_contents_without_validation(self, contents: RootT) -> None:
        validate_assignment = self.__config__.validate_assignment
        self.__config__.validate_assignment = False
        self.contents = contents.contents
        self.__config__.validate_assignment = validate_assignment

    @classmethod
    def to_json_schema(cls, pretty=False) -> str:
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
        if attr in self.__dict__ and attr not in [ROOT_KEY]:
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
            with AttribHolder(self, 'contents', copy_attr=True):
                ret = method(*args, **kwargs)
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
                if isinstance(args[0], int):
                    assert self.is_nested_type()
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
                if type_to_check is not None and isinstance(ret, type_to_check):
                    try:
                        ret = self.__class__(ret)
                    except ValidationError:
                        pass
        return ret

    def __getattr__(self, attr: str) -> Any:
        ret = self._getattr_from_contents(attr)
        if callable(ret):
            ret = add_callback_after_call(ret, self.validate_contents)
        return ret

    def _getattr_from_contents(self, attr):
        if isinstance(self.contents, Model):
            return getattr(self.contents.contents, attr)
        else:
            return getattr(self.contents, attr)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Model) \
            and self.__class__ == other.__class__ \
            and self.contents == other.contents \
            and self.to_data() == other.to_data()  # last is probably unnecessary, but just in case
