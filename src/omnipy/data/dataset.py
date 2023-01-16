from __future__ import annotations

from collections import UserDict
import json
from typing import Any, Dict, Generic, Iterator, Tuple, Type, TypeVar, Union

# from orjson import orjson
from pydantic import Field, PrivateAttr, ValidationError
from pydantic.generics import GenericModel
from pydantic.utils import lenient_issubclass

from omnipy.data.model import Model

ModelT = TypeVar('ModelT', bound=Model)
Undefined = object()
DATA_KEY = 'data'

# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()


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
        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

    data: Dict[str, ModelT] = Field(default={})

    def __class_getitem__(cls, model: ModelT) -> ModelT:
        # TODO: change model type to params: Union[Type[Any], Tuple[Type[Any], ...]]
        #       as in GenericModel

        # For now, only singular model types are allowed. These lines are needed for
        # interoperability with pydantic GenericModel, which internally stores the model
        # as a tuple:
        if isinstance(model, tuple) and len(model) == 1:
            model = model[0]

        if not isinstance(model, TypeVar) and not lenient_issubclass(model, Model):
            raise TypeError('Invalid model: {}! '.format(model)
                            + 'omnipy Dataset models must be a specialization of the omnipy '
                            'Model class.')
        return super().__class_getitem__(model)

    def __init__(self,
                 value: Union[Dict[str, Any], Iterator[Tuple[str, Any]]] = Undefined,
                 **input_data: Any) -> None:
        if value != Undefined:
            input_data[DATA_KEY] = value

        if self.get_model_class() == ModelT:
            self._raise_no_model_exception()

        GenericModel.__init__(self, **input_data)
        UserDict.__init__(self, self.data)  # noqa
        if not self.__doc__:
            self._set_standard_field_description()

    # TODO: Add test for get_model_class

    def get_model_class(self) -> ModelT:
        return self.__fields__.get(DATA_KEY).type_

    # TODO: Update _raise_no_model_exception() text. Model is now a requirement

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
        return ('This class represents a data in the `omnipy` Python package and contains '
                'a set of named data items that follows the same data model. '
                'It is a statically typed specialization of the Dataset class according to a '
                'particular specialization of the Model class. Both main classes are wrapping '
                'the excellent Python package named `pydantic`.')

    def __setitem__(self, obj_type: str, data_obj: Any) -> None:
        has_prev_value = obj_type in self.data
        prev_value = self.data.get(obj_type)

        try:
            self.data[obj_type] = data_obj
            self._validate(obj_type)
        except:  # noqa
            if has_prev_value:
                self.data[obj_type] = prev_value
            else:
                del self.data[obj_type]
            raise

    def __getitem__(self, obj_type: str) -> Any:
        if obj_type in self.data:
            return self.data[obj_type].contents
        else:
            return self.data[obj_type]

    def _validate(self, _obj_type: str) -> None:
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
        if not isinstance(data, dict):
            data = dict(data)

        if not update:
            self.clear()

        for obj_type, obj_val in data.items():
            new_model = self.get_model_class()()  # noqa
            new_model.from_data(obj_val)
            self[obj_type] = new_model

    def to_json(self, pretty=False) -> Dict[str, str]:
        result = {}

        for key, val in self.to_data().items():
            result[key] = self._pretty_print_json(val) if pretty else json.dumps(val)
        return result

    def from_json(self,
                  data: Union[Dict[str, str], Iterator[Tuple[str, str]]],
                  update: bool = True) -> None:
        if not isinstance(data, dict):
            data = dict(data)

        if not update:
            self.clear()

        for obj_type, obj_val in data.items():
            new_model = self.get_model_class()()  # noqa
            new_model.from_json(obj_val)
            self[obj_type] = new_model

    # @classmethod
    # def get_type_args(cls):
    #     return cls.__fields__.get(DATA_KEY).type_
    #
    #
    # @classmethod
    # def create_from_json(cls, data: Union[str, Tuple[str]]):
    #     if isinstance(data, tuple):
    #         data = data[0]
    #
    #     obj = cls()
    #     obj.from_json(data, update=False)
    #     return obj
    #
    # def __reduce__(self):
    #     return self.__class__.create_from_json, (self.to_json(),)

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

    def as_multi_model_dataset(self) -> MultiModelDataset[ModelT]:
        multi_model_dataset = MultiModelDataset[self.get_model_class()]()
        for obj_type in self:
            multi_model_dataset.data[obj_type] = self.data[obj_type]
        return multi_model_dataset


# TODO: Use json serializer package from the pydantic config instead of 'json'


class MultiModelDataset(Dataset[ModelT], Generic[ModelT]):

    _custom_field_models: Dict[str, ModelT] = PrivateAttr(default={})

    def set_model(self, obj_type: str, model: ModelT) -> None:
        try:
            self._custom_field_models[obj_type] = model
            if obj_type in self.data:
                self._validate(obj_type)
            else:
                self.data[obj_type] = model()
        except ValidationError:
            del self._custom_field_models[obj_type]
            raise

    def get_model(self, obj_type: str) -> ModelT:
        if obj_type in self._custom_field_models:
            return self._custom_field_models[obj_type]
        else:
            return self.get_model_class()

    def _validate(self, obj_type: str) -> None:
        if obj_type in self._custom_field_models:
            model = self._custom_field_models[obj_type]
            if not isinstance(model, Model):
                model = Model[model]
            data_obj = self._to_data_if_model(self.data[obj_type])
            parsed_data = self._to_data_if_model(model(data_obj))
            self.data[obj_type] = parsed_data
        super()._validate(obj_type)  # validates all data according to ModelT

    @staticmethod
    def _to_data_if_model(data_obj: Any):
        if isinstance(data_obj, Model):
            data_obj = data_obj.to_data()
        return data_obj
