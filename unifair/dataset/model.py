from copy import copy
import json
from typing import Any, Dict, Generic, get_origin, Type, TypeVar, Union

from pydantic import Protocol, root_validator
from pydantic.fields import ModelField
from pydantic.generics import GenericModel

RootT = TypeVar('RootT')
ROOT_KEY = '__root__'
Undefined = object()


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
        validate_all = True
        validate_assignment = True

    @classmethod
    def _get_default_value_from_model(cls, model: Type[Any]) -> Any:
        cur_model = model
        if isinstance(cur_model, TypeVar):
            if model.__bound__ is None:  # noqa
                raise TypeError('The TypeVar "{}" needs to be bound to a '.format(model.__name__)
                                + 'type that provides a default value when called')
            else:
                cur_model = model.__bound__  # noqa
        origin_type = get_origin(cur_model)
        if origin_type is None:
            origin_type = cur_model
        return origin_type()

    @classmethod
    def _populate_root_field(cls, model: Type[Any]) -> None:
        data_field = ModelField.infer(
            name=ROOT_KEY,
            value=cls._get_default_value_from_model(model),
            annotation=copy(model),
            class_validators=None,
            config=cls.__config__)

        cls.__fields__[ROOT_KEY] = data_field
        cls.__annotations__[ROOT_KEY] = model

    def __class_getitem__(cls, model: Type[Any]) -> Type[Any]:
        # Fix of a bug somewhere in pydantic, possibly?
        # test_complex_models in test_database fails without these lines.
        if isinstance(model, tuple) and len(model) == 1:
            model = model[0]

        # Populating the root field at runtime instead of providing a __root__ Field explicitly
        # is needed due to the inability of typing/pydantic to provide a dynamic default based on
        # the actual type. The following issue in mypy seems relevant:
        # https://github.com/python/mypy/issues/3737 (as well as linked issues)
        cls._populate_root_field(model)
        return super().__class_getitem__(model)

    def __new__(cls, value=Undefined, **kwargs):
        model_not_specified = ROOT_KEY not in cls.__fields__
        if model_not_specified:
            cls._populate_root_field(str)
            cls._print_warning_message()
        return super().__new__(cls)

    def __init__(self, value=Undefined, /, **data: Any) -> None:
        if value != Undefined:
            data[ROOT_KEY] = value

        super().__init__(**data)

        if not self.__class__.__doc__:
            self._set_standard_field_description()

    @staticmethod
    def _print_warning_message() -> None:
        # This should have been a TypeError in the __init__ method or similar, like in the
        # Database class, but due to complex interactions with pydantic and the state of the
        # Model class, a solution for raising an exception consistently for the cases where
        # __class_getitem__ has not been touched and which also leaves Model in a consistent
        # state for later code (e.g. in test runs) , has proved to be out of grasp.
        #
        # As a compromise, the following text is printed the first time a user tries to use
        # Model without specializing it with specific types.
        print('Note: The Model class requires a concrete model to be specified as '
              'a type hierarchy within brackets either directly, e.g.:\n\n'
              '\tmodel = Model[List[int]]([1,2,3])\n\n'
              'or indirectly in a subclass definition, e.g.:\n\n'
              '\tclass MyNumberList(Model[List[int]]): ...\n\n'
              'Usage without the specification of a concrete model defaults to Model[str], '
              'in a unstable and unsupported state, and is highly discouraged.\n\n'
              'This is the current mode; please fix your code!')

    def _set_standard_field_description(self) -> None:
        self.__fields__[ROOT_KEY].field_info.description = self._get_standard_field_description()

    @classmethod
    def _get_standard_field_description(cls) -> str:
        return ('This class represents a concrete model for dataset items in the `uniFAIR` Python '
                'package. It is a statically typed specialization of the Model class, '
                'which is itself wrapping the excellent Python package named `pydantic`.')

    @classmethod
    def _parse_data(cls, data: Any) -> Any:
        return data

    @root_validator
    def _parse_root_object(cls, root_obj: Any) -> Any:
        if ROOT_KEY not in root_obj:
            return root_obj
        else:
            return {ROOT_KEY: cls._parse_data(root_obj[ROOT_KEY])}

    def to_data(self) -> Any:
        return self.dict()[ROOT_KEY]

    def from_data(self, value: Any) -> None:
        super().__setattr__(ROOT_KEY, value)

    def to_json(self, pretty=False) -> str:
        json_content = self.json()
        if pretty:
            return self._pretty_print_json(json.loads(json_content))
        else:
            return json_content

    def from_json(self, json_contents: str) -> None:
        new_model = self.parse_raw(json_contents, proto=Protocol.json)
        self.from_data(new_model.to_data())

    @classmethod
    def to_json_schema(self, pretty=False) -> Union[str, Dict[str, Any]]:
        schema = self.schema()
        if pretty:
            return self._pretty_print_json(schema)
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
        if attr in self.__dict__ and attr != ROOT_KEY:
            super().__setattr__(attr, value)
        else:
            raise RuntimeError('Model does not allow setting of extra attributes')
        super().__setattr__(attr, value)
