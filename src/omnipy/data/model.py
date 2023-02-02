import json
from types import NoneType
from typing import Any, Dict, Generic, get_args, get_origin, Type, TypeVar, Union

# from orjson import orjson
from pydantic import Protocol, root_validator
from pydantic.fields import ModelField, Undefined, UndefinedType
from pydantic.generics import GenericModel

RootT = TypeVar('RootT')
ROOT_KEY = '__root__'

# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()


class Model(GenericModel, Generic[RootT]):
    """
    Model is a generic class. Subclasses of Model need to specify the type of
    contents that is accepted according to its model. Example:

    class MyNumberList(DatasetModel[List[int]]):
        pass

    See also docs of the Dataset class for more usage examples.
    """

    __root__: RootT

    class Config:
        arbitrary_types_allowed = True
        validate_all = True
        validate_assignment = True
        smart_union = True
        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

    @classmethod
    def _get_default_value_from_model(cls, model: Type[RootT]) -> RootT:
        if isinstance(model, TypeVar):
            if model.__bound__ is None:  # noqa
                raise TypeError('The TypeVar "{}" needs to be bound to a '.format(model.__name__)
                                + 'type that provides a default value when called')
            else:
                model = model.__bound__  # noqa
        origin_type = get_origin(model)
        args = get_args(model)

        if origin_type in (None, ()):
            origin_type = model

        if origin_type is Union:
            if NoneType in args:
                return None
            for arg in args:
                if callable(arg):
                    return cls._get_default_value_from_model(arg)
        elif origin_type is tuple:
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

        data_field = ModelField.infer(
            name=ROOT_KEY,
            value=Undefined,
            annotation=model,
            class_validators=None,
            config=cls.__config__)

        cls.__fields__[ROOT_KEY] = data_field
        cls.__annotations__[ROOT_KEY] = model

    @classmethod
    def _depopulate_root_field(cls):
        del cls.__config__.fields[ROOT_KEY]
        del cls.__fields__[ROOT_KEY]
        del cls.__annotations__[ROOT_KEY]

    def __class_getitem__(cls, model: Union[Type[RootT], TypeVar]) -> Union[Type[RootT], TypeVar]:
        # TODO: change model type to params: Union[Type[Any], Tuple[Type[Any], ...]]
        #       as in GenericModel

        # For now, only singular model types are allowed. These lines are needed for
        # interoperability with pydantic GenericModel, which internally stores the model
        # as a tuple:
        if isinstance(model, tuple) and len(model) == 1:
            model = model[0]

        # Populating the root field at runtime instead of providing a __root__ Field explicitly
        # is needed due to the inability of typing/pydantic to provide a dynamic default based on
        # the actual type. The following issue in mypy seems relevant:
        # https://github.com/python/mypy/issues/3737 (as well as linked issues)
        if cls == Model:  # Only for the base Model class
            cls._populate_root_field(model)

        created_model = super().__class_getitem__(model)

        # As long as models are not created concurrently, setting the class members temporarily
        # should not have averse effects
        # TODO: Check if we can move to explicit definition of __root__ field at the object
        #       level in pydantic 2.0 (when it is released)
        if cls == Model:
            cls._depopulate_root_field()

        return created_model

    def __new__(cls, value: Union[RootT, UndefinedType] = Undefined, **kwargs):
        model_not_specified = ROOT_KEY not in cls.__fields__
        if model_not_specified:
            cls._raise_no_model_exception()
        return super().__new__(cls)

    def __init__(
        self,
        value: Union[RootT, UndefinedType] = Undefined,
        /,
        __root__: Union[RootT, UndefinedType] = Undefined,
        **data: object,
    ) -> None:
        super_data: Dict[str, RootT] = {}
        num_root_vals = 0

        if value is not Undefined:
            super_data[ROOT_KEY] = value
            num_root_vals += 1

        if __root__ is not Undefined:
            super_data[ROOT_KEY] = __root__
            num_root_vals += 1

        if data:
            super_data[ROOT_KEY] = data
            num_root_vals += 1

        assert num_root_vals <= 1

        super().__init__(**super_data)

        if not self.__class__.__doc__:
            self._set_standard_field_description()

    @staticmethod
    def _raise_no_model_exception() -> None:
        raise TypeError('Note: The Model class requires a concrete model to be specified as '
                        'a type hierarchy within brackets either directly, e.g.:\n\n'
                        '\tmodel = Model[List[int]]([1,2,3])\n\n'
                        'or indirectly in a subclass definition, e.g.:\n\n'
                        '\tclass MyNumberList(Model[List[int]]): ...\n\n')

    def _set_standard_field_description(self) -> None:
        self.__fields__[ROOT_KEY].field_info.description = self._get_standard_field_description()

    @classmethod
    def _get_standard_field_description(cls) -> str:
        return ('This class represents a concrete model for data items in the `omnipy` Python '
                'package. It is a statically typed specialization of the Model class, '
                'which is itself wrapping the excellent Python package named `pydantic`.')

    @classmethod
    def _parse_data(cls, data: RootT) -> Any:
        return data

    @root_validator
    def _parse_root_object(cls, root_obj: RootT) -> Any:  # noqa
        if ROOT_KEY not in root_obj:
            return root_obj
        else:
            return {ROOT_KEY: cls._parse_data(root_obj[ROOT_KEY])}

    @property
    def contents(self) -> Any:
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
        new_model = self.parse_raw(json_contents, proto=Protocol.json)
        self._set_contents_without_validation(new_model)

    # @classmethod
    # def get_type_args(cls):
    #     return cls.__fields__.get(ROOT_KEY).type_
    #
    # @classmethod
    # def create_from_json(cls, data: Union[str, Tuple[str]]):
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
        return json.dumps(json_content, indent=4)

    def _check_for_root_key(self) -> None:
        if ROOT_KEY not in self.__dict__:
            raise TypeError('The Model class requires the specific model to be specified in as '
                            'a type hierarchy within brackets either directly, e.g.:\n'
                            '\t"model = Model[List[int]]([1,2,3])"\n'
                            'or indirectly in a subclass definition, e.g.:\n'
                            '\t"class MyNumberList(Model[List[int]]): ..."')

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in self.__dict__ and attr not in [ROOT_KEY]:
            super().__setattr__(attr, value)
        else:
            if attr in ['contents']:
                contents_prop = getattr(self.__class__, attr)
                contents_prop.__set__(self, value)
            else:
                raise RuntimeError('Model does not allow setting of extra attributes')

    # TODO: Update Dataset.__eq__ similarly, with tests
    def __eq__(self, other: object) -> bool:
        return self.__class__ == other.__class__ and super().__eq__(other)
