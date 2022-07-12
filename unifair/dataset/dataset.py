from collections import UserDict
import json
from typing import Any, Callable, Dict, Generic, Type, TypeVar, Union

from pydantic import Field
from pydantic.generics import GenericModel

from unifair.dataset.model import Model

_ContentsT = TypeVar('_ContentsT')
Undefined = object()
DATA_KEY = 'data'


class Dataset(GenericModel, Generic[_ContentsT], UserDict):
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

    data: Dict[str, _ContentsT] = Field(default={})

    def __class_getitem__(cls, model: Type[Any]) -> Type[Any]:
        if not issubclass(model, Model):
            raise TypeError('Invalid model: {}! '.format(model)
                            + 'uniFAIR Dataset models must be a specialization of the uniFAIR '
                            'Model class.')
        return super().__class_getitem__(model)

    def __init__(self, value: Dict[str, Any] = Undefined, **input_data: Any) -> None:
        if value != Undefined:
            input_data[DATA_KEY] = value

        if self.__fields__.get(DATA_KEY).type_ == _ContentsT:
            self._raise_no_model_exception()

        GenericModel.__init__(self, **input_data)
        UserDict.__init__(self, self.data)
        if not self.__doc__:
            self._set_standard_field_description()

    @staticmethod
    def _raise_no_model_exception():
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

    def _set_standard_field_description(self):
        self.__fields__[DATA_KEY].field_info.description = self._get_standard_field_description()

    @classmethod
    def _get_standard_field_description(cls):
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
            return self.data[obj_type].to_data()
        else:
            return self.data[obj_type]

    def _validate(self):
        self.data = self.data  # Triggers pydantic validation, as validate_assignment=True

    def __iter__(self):
        return UserDict.__iter__(self)

    def __setattr__(self, attr, value):
        if attr in self.__dict__ or attr == DATA_KEY or attr.strartswith('__'):
            super().__setattr__(attr, value)
        else:
            raise RuntimeError('Model does not allow setting of extra attributes')

    def to_data(self) -> Dict[str, Any]:
        return GenericModel.dict(self).get(DATA_KEY)

    def from_data(self, data: Dict[str, Any]) -> None:
        if isinstance(self, dict):
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

    def to_json_schema(self, pretty=False) -> Union[str, Dict[str, Any]]:
        result = {}
        schema = self.schema()
        for key, val in schema['properties']['data'].items():
            result[key] = val
        result['title'] = schema['title']
        result['definitions'] = schema['definitions']
        if pretty:
            return self._pretty_print_json(result)
        else:
            return json.dumps(result)

    @classmethod
    def _pretty_print_json(cls, json_content: Union[str, Any]) -> str:
        return json.dumps(json_content, indent=4)
