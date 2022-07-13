from collections import UserDict
import json
from typing import Any, Dict, Generic, Iterator, Tuple, Type, TypeVar, Union

from pydantic import Field, Protocol
from pydantic.generics import GenericModel

from unifair.dataset.model import Model

ModelT = TypeVar('ModelT', bound=Model)
Undefined = object()
DATA_KEY = 'data'


class Dataset(GenericModel, Generic[ModelT], UserDict):
    """
    Dataset is a generic class. Subclasses of Dataset need to specify the type of the contents
    that is accepted according to its model.

    This can be done directly, e.g.:

    class MyDataset(Dataset[Dict[str, List[int]]):
        pass

    or indirectly through the use of Model, e.g.:

    class MyModel(Model[Dict[str, List[int]]):
        pass

    class MyDataset(Dataset[MyModel]):
        pass

    This can also be done in a more deeply nested structure, e.g.:

    class MyNumberList(Model[List[int]]):
        pass

    class MyToplevelDict(Model[Dict[str, MyNumberList]]):
        pass

    class MyDataset(Dataset[MyToplevelDict]):
        pass

    Note: the naming of the classes in the examples are for illustrative purposes only and should
    not read as a naming standard.
    """
    class Config:
        validate_assignment = True

    data: Dict[str, ModelT] = Field(default={})

    def __class_getitem__(cls, model: Type[Any]) -> Type[Any]:
        if not issubclass(model, Model):
            raise TypeError('Invalid model: {}! '.format(model)
                            + 'uniFAIR Dataset models must be a specialization of the uniFAIR '
                            'Model class.')
        return super().__class_getitem__(model)

    def __init__(self,
                 value: Union[Dict[str, Any], Iterator[Tuple[str, Any]]] = Undefined,
                 **input_data: Any) -> None:
        if value != Undefined:
            input_data[DATA_KEY] = value

        if self._get_model_class() == ModelT:
            self._raise_no_model_exception()

        GenericModel.__init__(self, **input_data)
        UserDict.__init__(self, self.data)  # noqa
        if not self.__doc__:
            self._set_standard_field_description()

    def _get_model_class(self) -> ModelT:
        return self.__fields__.get(DATA_KEY).type_

    @staticmethod
    def _raise_no_model_exception() -> None:
        raise TypeError(
            'Note: The Dataset class requires a concrete model to be specified as '
            'a type hierarchy within brackets either directly, e.g.:\n\n'
            '\tmodel = Dataset[List[int]]()\n\n'
            'or indirectly in a subclass definition, e.g.:\n\n'
            '\tclass MyNumberListDataset(Dataset[List[int]]): ...\n\n'
            'In both cases, the use of the Model class or a subclass is encouraged if anything '
            'other than the simplest cases, e.g.:\n\n'
            '\tclass MyNumberListModel(Model[List[int]]): ...\n'
            '\tclass MyDataset(Dataset[MyNumberListModel]): ...\n\n'
            'Usage of Dataset without a type specification results in this exception. '
            'Similar use of the Model class do not currently result in an exception, only '
            'a warning message the first time this is done. However, this is just a '
            '"poor man\'s exception" due to complex technicalities in that class. Please '
            'explicitly specify types in both cases. ')

    def _set_standard_field_description(self) -> None:
        self.__fields__[DATA_KEY].field_info.description = self._get_standard_field_description()

    @classmethod
    def _get_standard_field_description(cls) -> str:
        return ('This class represents a dataset in the `uniFAIR` Python package and contains '
                'a set of named data items that follows the same data model. '
                'It is a statically typed specialization of the Dataset class according to a '
                'particular specialization of the Model class. Both main classes are wrapping '
                'the excellent Python package named `pydantic`.')

    def __setitem__(self, obj_type: str, data_obj: Any) -> None:
        try:
            self.data[obj_type] = data_obj
            self._validate()
        except:  # noqa
            del self.data[obj_type]
            raise

    def __getitem__(self, obj_type: str) -> Any:
        if obj_type in self.data:
            return self.data[obj_type].contents
        else:
            return self.data[obj_type]

    def _validate(self) -> None:
        self.data = self.data  # Triggers pydantic validation, as validate_assignment=True

    def __iter__(self) -> Iterator:
        return UserDict.__iter__(self)

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in self.__dict__ or attr == DATA_KEY or attr.startswith('__'):
            super().__setattr__(attr, value)
        else:
            raise RuntimeError('Model does not allow setting of extra attributes')

    def to_data(self) -> Dict[str, Any]:
        return GenericModel.dict(self).get(DATA_KEY)

    def from_data(self,
                  data: Union[Dict[str, Any], Iterator[Tuple[str, Any]]],
                  update: bool = True) -> None:
        if update:
            self.update(data)
        else:
            self.data = data

    def to_json(self, pretty=False) -> Dict[str, str]:
        result = {}
        json_content = self.json()
        contents = json.loads(json_content)
        assert len(contents.keys()) == 1 and next(iter(contents.keys())) == DATA_KEY
        for key, val in contents[DATA_KEY].items():
            result[key] = self._pretty_print_json(val) if pretty else json.dumps(val)
        return result

    def from_json(self,
                  data: Union[Dict[str, str], Iterator[Tuple[str, str]]],
                  update: bool = True) -> None:
        parsed_data = {}
        for key, json_contents in dict(data).items():
            print(self.__fields__)
            new_model = self._get_model_class().parse_raw(json_contents, proto=Protocol.json)
            parsed_data[key] = new_model.to_data()

        self.from_data(parsed_data, update=update)

    @classmethod
    def to_json_schema(cls, pretty=False) -> Union[str, Dict[str, str]]:
        result = {}
        schema = cls.schema()
        for key, val in schema['properties']['data'].items():
            result[key] = val
        result['title'] = schema['title']
        result['definitions'] = schema['definitions']
        if pretty:
            return cls._pretty_print_json(result)
        else:
            return json.dumps(result)

    @staticmethod
    def _pretty_print_json(json_content: Any) -> str:
        return json.dumps(json_content, indent=4)
