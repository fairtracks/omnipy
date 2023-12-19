from collections import UserDict
from collections.abc import Iterable, Mapping
import json
import os
import tarfile
from typing import Annotated, Any, Generic, get_args, get_origin, Iterator, Optional, Type, TypeVar

import humanize
import objsize
# from orjson import orjson
from pydantic import Field, PrivateAttr, root_validator, ValidationError
from pydantic.fields import Undefined, UndefinedType
from pydantic.generics import GenericModel
from pydantic.utils import lenient_issubclass
from tabulate import tabulate

from omnipy.data.model import (_cleanup_name_qualname_and_module,
                               _is_interactive_mode,
                               _waiting_for_terminal_repr,
                               INTERACTIVE_MODULES,
                               Model)
from omnipy.util.helpers import (get_calling_module_name,
                                 is_iterable,
                                 is_optional,
                                 is_strict_subclass,
                                 remove_forward_ref_notation)

ModelT = TypeVar('ModelT', bound=Model)
DATA_KEY = 'data'

# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()

# TODO: implement copy(), __copy__() and __deepcopy__() for Dataset and Model, making use of
#       BaseModel.copy()


class Dataset(GenericModel, Generic[ModelT], UserDict):
    """
    Dict-based container of data files that follow a specific Model

    Dataset is a generic class that cannot be instantiated directly. Instead, a Dataset class needs
    to be specialized with a data model before Dataset objects can be instantiated. A data model
    functions as a data parser and guarantees that the parsed data follows the specified model.

    The specialization must be done through the use of Model, either directly, e.g.::

        MyDataset = Dataset[Model[dict[str, list[int]]])

    ... or indirectly, using a Model subclass, e.g.::

        class MyModel(Model[dict[str, list[int]]):
            pass

        MyDataset = Dataset[MyModel]

    ... alternatively through the specification of a Dataset subclass::

        class MyDataset(Dataset[MyModel]):
            pass

    The specialization can also be done in a more deeply nested structure, e.g.::

        class MyNumberList(Model[list[int]]):
            pass

        class MyToplevelDict(Model[dict[str, MyNumberList]]):
            pass

        class MyDataset(Dataset[MyToplevelDict]):
            pass

    Once instantiated, a dataset object functions as a dict of data files, with the keys
    referring to the data file names and the contents to the data file contents, e.g.::

        MyNumberListDataset = Dataset[Model[list[int]]]

        my_dataset = MyNumberListDataset({'file_1': [1,2,3]})
        my_dataset['file_2'] = [2,3,4]

        print(my_dataset.keys())

    The Dataset class is a wrapper class around the powerful `GenericModel` class from pydantic.
    """
    class Config:
        validate_assignment = True
        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

    data: dict[str, ModelT] = Field(default={})

    def __class_getitem__(cls, model: ModelT) -> ModelT:
        # TODO: change model type to params: Type[Any] | tuple[Type[Any], ...]
        #       as in GenericModel.

        # For now, only singular model types are allowed. These lines are needed for
        # interoperability with pydantic GenericModel, which internally stores the model
        # as a tuple:
        if isinstance(model, tuple) and len(model) == 1:
            model = model[0]

        orig_model = model

        model = cls._origmodel_if_annotated_optional(model)

        if not isinstance(model, TypeVar) \
                and not lenient_issubclass(model, Model) \
                and not is_strict_subclass(cls, Dataset):
            raise TypeError('Invalid model: {}! '.format(model)
                            + 'omnipy Dataset models must be a specialization of the omnipy '
                            'Model class.')

        if cls == Dataset and not is_optional(model):
            model = Annotated[Optional[model], 'Fake Optional from Dataset']

        created_dataset = super().__class_getitem__(model)

        _cleanup_name_qualname_and_module(cls, created_dataset, model, orig_model)

        return created_dataset

    def __init__(
        self,
        value: Mapping[str, object] | Iterable[tuple[str, object]] | UndefinedType = Undefined,
        *,
        data: Mapping[str, object] | UndefinedType = Undefined,
        **input_data: object,
    ) -> None:
        # TODO: Error message when forgetting parenthesis when creating Dataset should be improved.
        #       Unclear where this can be done, if anywhere? E.g.:
        #           a = Dataset[Model[int]]
        #           a['adsfas'] = 2
        #           Traceback (most recent call last):
        #             ...
        #           TypeError: 'ModelMetaclass' object does not support item assignment
        #
        # TODO: Disallow e.g.:
        #       Dataset[Model[str]](Model[int](5)) ==  Dataset[Model[str]](data=Model[int](5))
        #       == Dataset[Model[str]](data={'__root__': Model[str]('5')})

        super_kwargs = {}

        assert DATA_KEY not in input_data, \
            ('Not allowed with"data" as input_data key. Not sure how you managed this? Are you '
             'trying to break Dataset init on purpose?')

        if value != Undefined:
            assert data == Undefined, \
                'Not allowed to combine positional and "data" keyword argument'
            assert len(input_data) == 0, 'Not allowed to combine positional and keyword arguments'
            super_kwargs[DATA_KEY] = value

        if data != Undefined:
            assert len(input_data) == 0, \
                "Not allowed to combine 'data' with other keyword arguments"
            super_kwargs[DATA_KEY] = data

        if DATA_KEY not in super_kwargs and len(input_data) > 0:
            super_kwargs[DATA_KEY] = input_data

        if self.get_model_class() == ModelT:
            self._raise_no_model_exception()

        GenericModel.__init__(self, **super_kwargs)
        UserDict.__init__(self, self.data)  # noqa
        if not self.__doc__:
            self._set_standard_field_description()

    @classmethod
    def get_model_class(cls) -> Type[Model]:
        """
        Returns the concrete Model class used for all data files in the dataset, e.g.:
        `Model[list[int]]`
        :return: The concrete Model class used for all data files in the dataset
        """
        model_type = cls.__fields__.get(DATA_KEY).type_
        return cls._origmodel_if_annotated_optional(model_type)

    @classmethod
    def _origmodel_if_annotated_optional(cls, model):
        if get_origin(model) is Annotated:
            unannotated_type = get_args(model)[0]
            if is_optional(unannotated_type):
                model = get_args(unannotated_type)[0]
        return model

    # TODO: Update _raise_no_model_exception() text. Model is now a requirement
    @staticmethod
    def _raise_no_model_exception() -> None:
        raise TypeError(
            'Note: The Dataset class requires a concrete model to be specified as '
            'a type hierarchy within brackets either directly, e.g.:\n\n'
            '\tmodel = Dataset[list[int]]()\n\n'
            'or indirectly in a subclass definition, e.g.:\n\n'
            '\tclass MyNumberListDataset(Dataset[list[int]]): ...\n\n'
            'In both cases, the use of the Model class or a subclass is encouraged if anything '
            'other than the simplest cases, e.g.:\n\n'
            '\tclass MyNumberListModel(Model[list[int]]): ...\n'
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

    def __setitem__(self, data_file: str, data_obj: Any) -> None:
        has_prev_value = data_file in self.data
        prev_value = self.data.get(data_file)

        try:
            self.data[data_file] = data_obj
            self._validate(data_file)
        except:  # noqa
            if has_prev_value:
                self.data[data_file] = prev_value
            else:
                del self.data[data_file]
            raise

    def __getitem__(self, selector: str | int | slice | Iterable[str | int]) -> Any:
        if isinstance(selector, str):
            if selector in self.data:
                return self.data[selector]
            else:
                return self.data[selector]
        else:
            data_keys = tuple(self.data.keys())

            if isinstance(selector, int):
                return self.data[data_keys[selector]]
            elif isinstance(selector, slice):
                return self.__class__({key: self.data[key] for key in data_keys[selector]})
            elif is_iterable(selector):
                selected_keys = [data_keys[_] if isinstance(_, int) else _ for _ in selector]
                return self.__class__({key: self.data[key] for key in selected_keys})
            else:
                raise KeyError(
                    'Selector is of incorrect type. Must be a string, a positive integer,'
                    'or a slice (e.g. `dataset[2:5]`).')

    @classmethod
    def update_forward_refs(cls, **localns: Any) -> None:
        """
        Try to update ForwardRefs on fields based on this Model, globalns and localns.
        """
        cls.get_model_class().update_forward_refs(**localns)  # Update Model cls
        super().update_forward_refs(**localns)
        cls.__name__ = remove_forward_ref_notation(cls.__name__)
        cls.__qualname__ = remove_forward_ref_notation(cls.__qualname__)

    def _validate(self, _data_file: str) -> None:
        self.data = self.data  # Triggers pydantic validation, as validate_assignment=True

    def __iter__(self) -> Iterator:
        return UserDict.__iter__(self)

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in self.__dict__ or attr == DATA_KEY or attr.startswith('__'):
            super().__setattr__(attr, value)
        else:
            raise RuntimeError('Model does not allow setting of extra attributes')

    @root_validator()
    def _parse_root_object(cls, root_obj: dict[str, ModelT]) -> Any:  # noqa
        assert DATA_KEY in root_obj
        data_dict = root_obj[DATA_KEY]
        model = cls.get_model_class()
        for key, val in data_dict.items():
            if val is None:
                data_dict[key] = model.parse_obj(val)
        return {DATA_KEY: data_dict}

    def to_data(self) -> dict[str, Any]:
        return GenericModel.dict(self).get(DATA_KEY)

    def from_data(self,
                  data: dict[str, Any] | Iterator[tuple[str, Any]],
                  update: bool = True) -> None:
        if not isinstance(data, dict):
            data = dict(data)

        if not update:
            self.clear()

        for data_file, obj_val in data.items():
            new_model = self.get_model_class()()  # noqa
            new_model.from_data(obj_val)
            self[data_file] = new_model

    def absorb(self, other: 'Dataset'):
        self.from_data(other.to_data(), update=True)

    def absorb_and_replace(self, other: 'Dataset'):
        self.from_data(other.to_data(), update=False)

    def to_json(self, pretty=True) -> dict[str, str]:
        result = {}

        for key, val in self.to_data().items():
            result[key] = self._pretty_print_json(val) if pretty else json.dumps(val)
        return result

    def from_json(self,
                  data: Mapping[str, str] | Iterable[tuple[str, str]],
                  update: bool = True) -> None:
        if not isinstance(data, dict):
            data = dict(data)

        if not update:
            self.clear()

        for data_file, obj_val in data.items():
            new_model = self.get_model_class()()  # noqa
            new_model.from_json(obj_val)
            self[data_file] = new_model

    # @classmethod
    # def get_type_args(cls):
    #     return cls.__fields__.get(DATA_KEY).type_
    #
    #
    # @classmethod
    # def create_from_json(cls, data: str, tuple[str]]):
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
    def to_json_schema(cls, pretty=True) -> str | dict[str, str]:
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
        return json.dumps(json_content, indent=2)

    def save(self, directory: str):
        serializer_registry = self._get_serializer_registry()

        parsed_dataset, serializer = serializer_registry.auto_detect_tar_file_serializer(self)

        if serializer is None:
            print(f'Unable to find a serializer for dataset with data type "{type(self)}". '
                  f'Will abort saving...')
        else:
            print(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(directory)}"')

            out_tar_gz_path = f'{directory}.tar.gz'

            with open(out_tar_gz_path, 'wb') as out_tar_gz_file:
                out_tar_gz_file.write(serializer.serialize(parsed_dataset))

            if not os.path.exists(directory):
                os.makedirs(directory)

            tar = tarfile.open(out_tar_gz_path)
            tar.extractall(path=directory)
            tar.close()

    def load(self, tar_gz_file_path: str):
        serializer_registry = self._get_serializer_registry()

        loaded_dataset = serializer_registry.load_from_tar_file_path_based_on_dataset_cls(
            self, tar_gz_file_path, self)
        if loaded_dataset is not None:
            self.absorb(loaded_dataset)
            return

        self.absorb(
            serializer_registry.load_from_tar_file_path_based_on_file_suffix(
                self, tar_gz_file_path, self))

    @staticmethod
    def _get_serializer_registry():
        from omnipy.data.serializer import SerializerRegistry
        from omnipy.hub.runtime import runtime
        from omnipy.modules import register_serializers
        serializer_registry = SerializerRegistry() if runtime is None else \
            runtime.objects.serializers
        if len(serializer_registry.serializers) == 0:
            register_serializers(serializer_registry)
        return serializer_registry

    def as_multi_model_dataset(self) -> 'MultiModelDataset[ModelT]':
        multi_model_dataset = MultiModelDataset[self.get_model_class()]()
        for data_file in self:
            multi_model_dataset.data[data_file] = self.data[data_file]
        return multi_model_dataset

    def __eq__(self, other: object) -> bool:
        # return self.__class__ == other.__class__ and super().__eq__(other)
        return isinstance(other, Dataset) \
            and self.__class__ == other.__class__ \
            and self.data == other.data \
            and self.to_data() == other.to_data()  # last is probably unnecessary, but just in case

    def __repr_args__(self):
        return [(k, v.contents) for k, v in self.data.items()]

    def __repr__(self):
        if _is_interactive_mode() and not _waiting_for_terminal_repr():
            print(get_calling_module_name())
            if get_calling_module_name() in INTERACTIVE_MODULES:
                _waiting_for_terminal_repr(True)
                return self._table_repr()
        return self._trad_repr()

    def _trad_repr(self) -> str:
        return super().__repr__()

    def _table_repr(self) -> str:
        ret = tabulate(
            ((i,
              k,
              type(v).__name__,
              v.__len__() if hasattr(v, '__len__') else 'N/A',
              humanize.naturalsize(objsize.get_deep_size(v)))
             for i, (k, v) in enumerate(self.items())),
            ('#', 'Data file name', 'Type', 'Length', 'Size (in memory)'),
            tablefmt='rounded_outline',
        )
        _waiting_for_terminal_repr(False)
        return ret


# TODO: Use json serializer package from the pydantic config instead of 'json'


class MultiModelDataset(Dataset[ModelT], Generic[ModelT]):
    """
        Variant of Dataset that allows custom models to be set on individual data files

        Note that the general model still needs to hold for all data files, in addition to any
        custom models.
    """

    _custom_field_models: dict[str, ModelT] = PrivateAttr(default={})

    def set_model(self, data_file: str, model: ModelT) -> None:
        try:
            self._custom_field_models[data_file] = model
            if data_file in self.data:
                self._validate(data_file)
            else:
                self.data[data_file] = model()
        except ValidationError:
            del self._custom_field_models[data_file]
            raise

    def get_model(self, data_file: str) -> ModelT:
        if data_file in self._custom_field_models:
            return self._custom_field_models[data_file]
        else:
            return self.get_model_class()

    def _validate(self, data_file: str) -> None:
        if data_file in self._custom_field_models:
            model = self._custom_field_models[data_file]
            if not isinstance(model, Model):
                model = Model[model]
            data_obj = self._to_data_if_model(self.data[data_file])
            parsed_data = self._to_data_if_model(model(data_obj))
            self.data[data_file] = parsed_data
        super()._validate(data_file)  # validates all data according to ModelT

    @staticmethod
    def _to_data_if_model(data_obj: Any):
        if isinstance(data_obj, Model):
            data_obj = data_obj.to_data()
        return data_obj
