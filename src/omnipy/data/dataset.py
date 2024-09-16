from collections import UserDict
from collections.abc import Iterable, Mapping
from copy import copy
import json
import os
import tarfile
from tempfile import TemporaryDirectory
from typing import Any, Callable, cast, Generic, Iterator, MutableMapping
from urllib.parse import ParseResult, urlparse

import humanize
import objsize
# from orjson import orjson
from pydantic import Field, PrivateAttr, root_validator, ValidationError
from pydantic.fields import ModelField, Undefined, UndefinedType
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass
from pydantic.utils import lenient_isinstance, lenient_issubclass
from typing_extensions import TypeVar

from omnipy.data.data_class_creator import DataClassBase, DataClassBaseMeta
from omnipy.data.helpers import (cleanup_name_qualname_and_module,
                                 INTERACTIVE_MODULES,
                                 is_model_instance,
                                 waiting_for_terminal_repr)
from omnipy.data.model import Model
from omnipy.data.selector import (create_updated_mapping,
                                  Index2DataItemsType,
                                  Key2DataItemType,
                                  prepare_selected_items_with_iterable_data,
                                  prepare_selected_items_with_mapping_data,
                                  select_keys)
from omnipy.util.helpers import (get_calling_module_name,
                                 get_default_if_typevar,
                                 is_iterable,
                                 remove_forward_ref_notation)
from omnipy.util.tabulate import tabulate
from omnipy.util.web import download_file_to_memory

ModelT = TypeVar('ModelT', bound=Model)
GeneralModelT = TypeVar('GeneralModelT', bound=Model)
_DatasetT = TypeVar('_DatasetT')

DATA_KEY = 'data'

# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()

# TODO: implement copy(), __copy__() and __deepcopy__() for Dataset and Model, making use of
#       BaseModel.copy()


class _DatasetMetaclass(ModelMetaclass, DataClassBaseMeta):
    ...


class Dataset(GenericModel, Generic[ModelT], UserDict, DataClassBase, metaclass=_DatasetMetaclass):
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

        # TODO: Use json serializer package from the pydantic config instead of 'json'

        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

    data: dict[str, ModelT] = Field(default={})

    def __class_getitem__(
        cls,
        params: type[ModelT] | tuple[type[ModelT]] | tuple[type[ModelT], Any] | TypeVar
        | tuple[TypeVar, ...],
    ) -> 'type[Dataset[type[ModelT]]]':
        # TODO: change model type to params: Type[Any] | tuple[Type[Any], ...]
        #       as in GenericModel.

        # These lines are needed for interoperability with pydantic GenericModel, which internally
        # stores the model as a len(1) tuple
        model = params[0] if isinstance(params, tuple) and len(params) == 1 else params

        orig_model = model

        if cls == Dataset:
            if not isinstance(model, TypeVar) \
                    and not lenient_issubclass(model, Model):
                raise TypeError('Invalid model: {}! '.format(model)
                                + 'omnipy Dataset models must be a specialization of the omnipy '
                                'Model class.')

            created_dataset = super().__class_getitem__(model)
        else:
            if isinstance(model, TypeVar):
                params = get_default_if_typevar(model)

            created_dataset = super().__class_getitem__(params)

        cleanup_name_qualname_and_module(cls, created_dataset, orig_model)

        return created_dataset

    def __init__(  # noqa: C901
        self,
        value: Mapping[str, object] | Iterable[tuple[str, object]] | UndefinedType = Undefined,
        *,
        data: Mapping[str, object] | UndefinedType = Undefined,
        **kwargs: object,
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

        assert DATA_KEY not in kwargs, \
            ('Not allowed with "data" as kwargs key. Not sure how you managed this? Are you trying '
             'to break Dataset init on purpose?')

        if value != Undefined:
            assert data == Undefined, \
                'Not allowed to combine positional and "data" keyword argument'
            assert len(kwargs) == 0, \
                'Not allowed to combine positional and keyword arguments'
            super_kwargs[DATA_KEY] = value

        if data != Undefined:
            assert len(kwargs) == 0, \
                f"Not allowed to combine '{DATA_KEY}' with other keyword arguments"
            super_kwargs[DATA_KEY] = data

        if kwargs:
            if DATA_KEY not in super_kwargs:
                super_kwargs[DATA_KEY] = kwargs
                kwargs = {}

        if self.get_model_class() == ModelT:
            self._raise_no_model_exception()

        dataset_as_input = DATA_KEY in super_kwargs \
            and lenient_isinstance(super_kwargs[DATA_KEY], Dataset)
        if dataset_as_input:
            super_kwargs[DATA_KEY] = super_kwargs[DATA_KEY].to_data()

        self._init(super_kwargs, **kwargs)

        try:
            super().__init__(**super_kwargs)
        except ValidationError:
            if dataset_as_input:
                super().__init__()
                self.from_data(super_kwargs[DATA_KEY])
            else:
                raise

        UserDict.__init__(self, self.data)  # noqa

        if not self.__doc__:
            self._set_standard_field_description()

    def _init(self, super_kwargs: dict[str, Any], **kwargs: Any) -> None:
        ...

    # TODO: Revise with pydantic v2: __deepcopy__ is not defined for Dataset and Model, as it is not
    #       supported by pydantic v1. BaseModel.copy(deep=True) does not support a deepcopy memo.
    #       So we instead make use of the builtin support for deepcopy, which seems to work fine.
    #       However, __deepcopy__ in pydantic v2 is probably more efficient due to the memo and
    #       the Rust backend.

    def __copy__(self):
        return self.copy(deep=False)

    def copy(self, *, deep: bool = False, **kwargs) -> 'Dataset[ModelT]':
        pydantic_copy = GenericModel.copy(self, deep=deep, **kwargs)
        if not deep:
            pydantic_copy.__dict__[DATA_KEY] = pydantic_copy.__dict__[DATA_KEY].copy()
        return pydantic_copy

    @classmethod
    def clone_dataset_cls(cls: type[_DatasetT],
                          new_dataset_cls_name: str,
                          model_cls: type | None = None) -> type[_DatasetT]:
        # TODO: Update `model_cls` type to `type[IsModel] | None` when IsModel is defined
        if model_cls:
            generic_dataset_cls = cls.__bases__[0]
            new_base_cls = generic_dataset_cls[model_cls]
        else:
            new_base_cls = cls

        new_dataset_cls: type[_DatasetT] = type(new_dataset_cls_name, (new_base_cls,), {})
        return new_dataset_cls

    @classmethod
    def _get_data_field(cls) -> ModelField:
        return cast(ModelField, cls.__fields__.get(DATA_KEY))

    @classmethod
    def get_model_class(cls) -> type[Model] | None:
        """
        Returns the concrete Model class used for all data files in the dataset, e.g.:
        `Model[list[int]]`
        :return: The concrete Model class used for all data files in the dataset
        """
        return cls._get_data_field().type_

    @staticmethod
    def _raise_no_model_exception() -> None:
        raise TypeError(
            'Note: The Dataset class requires a Model class (or a subclass) to be specified as '
            'a type hierarchy within brackets either directly, e.g.:\n\n'
            '\tmodel = Dataset[Model[list[int]]]()\n\n'
            'or indirectly in a subclass definition, e.g.:\n\n'
            '\tclass MyNumberListDataset(Dataset[Model[list[int]]]): ...\n\n'
            'For anything other than the simplest cases, the definition of Model and Dataset '
            'subclasses is encouraged , e.g.:\n\n'
            '\tclass MyNumberListModel(Model[list[int]]): ...\n'
            '\tclass MyDataset(Dataset[MyNumberListModel]): ...\n\n')

    def _set_standard_field_description(self) -> None:
        self.__fields__[DATA_KEY].field_info.description = self._get_standard_field_description()

    @classmethod
    def _get_standard_field_description(cls) -> str:
        return ('This class represents a data in the `omnipy` Python package and contains '
                'a set of named data items that follows the same data model. '
                'It is a statically typed specialization of the Dataset class according to a '
                'particular specialization of the Model class. Both main classes are wrapping '
                'the excellent Python package named `pydantic`.')

    def __getitem__(self, selector: str | int | slice | Iterable[str | int]) -> Any:
        selected_keys = select_keys(selector, self.data)

        if selected_keys.singular:
            return self.data[selected_keys.keys[0]]
        else:
            return self.__class__({key: self.data[key] for key in selected_keys.keys})

    def __delitem__(self, selector: str | int | slice | Iterable[str | int]) -> Any:
        selected_keys = select_keys(selector, self.data)

        if selected_keys.singular:
            del self.data[selected_keys.keys[0]]
        else:
            prev_data = copy(self.data)

            try:
                for key in selected_keys.keys:
                    del self.data[key]
            except Exception:
                self.data = prev_data
                raise

    def __setitem__(
        self,
        selector: str | int | slice | Iterable[str | int],
        data_obj: dict[str, ModelT] | Iterable[ModelT] | ModelT,
    ) -> None:
        selected_keys = select_keys(selector, self.data)

        if selected_keys.singular:
            self._set_data_file_and_validate(selected_keys.keys[0], cast(ModelT, data_obj))
        else:
            key_2_data_item: Key2DataItemType[ModelT]
            index_2_data_items: Index2DataItemsType[ModelT]

            if isinstance(data_obj, MutableMapping):
                key_2_data_item, index_2_data_items = \
                    prepare_selected_items_with_mapping_data(
                        selected_keys.keys, selected_keys.last_index, data_obj,)

            elif is_iterable(data_obj) and not isinstance(data_obj, (str, bytes)):
                key_2_data_item, index_2_data_items = \
                    prepare_selected_items_with_iterable_data(
                        selected_keys.keys, selected_keys.last_index, tuple(data_obj), self.data)

            else:
                raise TypeError('Data object must be a mapping or an iterable')

            self._update_selected_items_with_data_items(key_2_data_item, index_2_data_items)

    def _update_selected_items_with_data_items(
        self,
        key_2_data_item: Key2DataItemType[ModelT],
        index_2_data_item: Index2DataItemsType[ModelT],
    ) -> None:

        updated_mapping = create_updated_mapping(self.data, key_2_data_item, index_2_data_item)
        self._replace_data_with_mapping(updated_mapping)

    def _replace_data_with_mapping(self, updated_mapping):
        prev_data = self.data
        try:
            self.absorb_and_replace(self.__class__(updated_mapping))
        except Exception:
            self.data = prev_data
            raise

    def _set_data_file_and_validate(self, key: str, val: ModelT) -> None:
        has_prev_value = key in self.data
        if has_prev_value:
            prev_value = self.data[key]

        try:
            self.data[key] = val
            self._validate(key)
        except Exception:
            if has_prev_value:
                self.data[key] = prev_value
            else:
                del self.data[key]
            raise

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

    @root_validator
    def _parse_root_object(cls, root_obj: dict[str, ModelT]) -> Any:  # noqa
        assert DATA_KEY in root_obj
        data_dict = root_obj[DATA_KEY]
        model = cls.get_model_class()
        for key, val in data_dict.items():
            if val is None:
                data_dict[key] = model.parse_obj(val)
        return {DATA_KEY: data_dict}

    def to_data(self) -> dict[str, Any]:
        return GenericModel.dict(self, by_alias=True).get(DATA_KEY)

    def from_data(self,
                  data: dict[str, Any] | Iterator[tuple[str, Any]],
                  update: bool = True) -> None:
        def callback_func(model: ModelT, contents: Any):
            model.from_data(contents)

        self._from_dict_with_callback(data, update, callback_func)

    def _from_dict_with_callback(self,
                                 data: dict[str, Any] | Iterator[tuple[str, Any]],
                                 update: bool,
                                 callback_func: Callable):
        if not isinstance(data, dict):
            data = dict(data)

        if not update:
            self.clear()

        model_cls = self.get_model_class()
        for data_file, contents in data.items():
            new_model = model_cls()
            callback_func(new_model, contents)
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
        def callback_func(model: ModelT, contents: Any):
            model.from_json(contents)

        self._from_dict_with_callback(data, update, callback_func)

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
        for key, val in schema['properties'][DATA_KEY].items():
            result[key] = val
        result['title'] = schema['title']
        result['definitions'] = schema['definitions']

        for model_desc in result['definitions'].values():
            if 'orig_model' in model_desc:
                del model_desc['orig_model']

        if pretty:
            return cls._pretty_print_json(result)
        else:
            return json.dumps(result)

    @staticmethod
    def _pretty_print_json(json_content: Any) -> str:
        return json.dumps(json_content, indent=2)

    def save(self, path: str):
        serializer_registry = self._get_serializer_registry()

        parsed_dataset, serializer = serializer_registry.auto_detect_tar_file_serializer(self)

        if serializer is None:
            print(f'Unable to find a serializer for dataset with data type "{type(self)}". '
                  f'Will abort saving...')
        else:
            if not path.endswith('.tar.gz'):
                out_tar_gz_path = f'{path}.tar.gz'

            print(f'Writing dataset as a gzipped tarpack to "{os.path.abspath(out_tar_gz_path)}"')

            with open(out_tar_gz_path, 'wb') as out_tar_gz_file:
                out_tar_gz_file.write(serializer.serialize(parsed_dataset))

            directory = os.path.abspath(out_tar_gz_path[:-7])
            if not os.path.exists(directory):
                os.makedirs(directory)

            tar = tarfile.open(out_tar_gz_path)
            print(f'Extracting contents to directory "{os.path.abspath(out_tar_gz_path[:-7])}"')
            tar.extractall(path=directory)
            tar.close()

    def load(self, *path_or_urls: str, by_file_suffix=False):
        for path_or_url in path_or_urls:
            if is_model_instance(path_or_url):
                path_or_url = path_or_url.contents

            with TemporaryDirectory() as tmp_dir_path:
                serializer_registry = self._get_serializer_registry()

                parsed_url = urlparse(path_or_url)

                if parsed_url.scheme in ['http', 'https']:
                    download_path = self._download_file(path_or_url, parsed_url.path, tmp_dir_path)
                    if download_path is None:
                        continue
                    tar_gz_file_path = self._ensure_tar_gz_file(download_path)
                elif parsed_url.scheme in ['file', '']:
                    tar_gz_file_path = self._ensure_tar_gz_file(parsed_url.path)
                elif self._is_windows_path(parsed_url):
                    tar_gz_file_path = self._ensure_tar_gz_file(path_or_url)
                else:
                    raise ValueError(f'Unsupported scheme "{parsed_url.scheme}"')

                if by_file_suffix:
                    loaded_dataset = \
                        serializer_registry.load_from_tar_file_path_based_on_file_suffix(
                            self, tar_gz_file_path, self)
                else:
                    loaded_dataset = \
                        serializer_registry.load_from_tar_file_path_based_on_dataset_cls(
                            self, tar_gz_file_path, self)
                if loaded_dataset is not None:
                    self.absorb(loaded_dataset)
                    continue
                else:
                    raise RuntimeError('Unable to load serializer')

    @staticmethod
    def _is_windows_path(parsed_url: ParseResult) -> bool:
        return len(parsed_url.scheme) == 1 and parsed_url.scheme.isalpha()

    @staticmethod
    def _download_file(url: str, path: str, tmp_dir_path: str) -> str | None:
        print(f'Downloading {url}...')
        data = download_file_to_memory(url)

        if data is None:
            print(f'Failed to download file from {url}')
            return None

        download_path = os.path.join(tmp_dir_path, os.path.basename(path))
        with open(download_path, 'wb') as out_file:
            out_file.write(data)
        return download_path

    @staticmethod
    def _ensure_tar_gz_file(path: str):
        assert os.path.exists(path), f'No file or directory at {path}'

        if not path.endswith('.tar.gz'):
            tar_gz_file_path = path + '.tar.gz'
            if not os.path.isfile(tar_gz_file_path):
                print(f'Creating compressed file {os.path.abspath(tar_gz_file_path)} from '
                      f'the contents of "{os.path.abspath(path)}"')

                with tarfile.open(tar_gz_file_path, 'w:gz') as tar:
                    if os.path.isdir(path):
                        for fn in sorted(os.listdir(path)):
                            p = os.path.join(path, fn)
                            tar.add(p, arcname=fn)
                    elif os.path.isfile(path):
                        tar.add(path, arcname=os.path.basename(path))
            return tar_gz_file_path

        return path

    @staticmethod
    def _get_serializer_registry():
        from omnipy.modules import get_serializer_registry
        return get_serializer_registry()

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
        if self.config.interactive_mode and not waiting_for_terminal_repr():
            if get_calling_module_name() in INTERACTIVE_MODULES:
                waiting_for_terminal_repr(True)
                return self._table_repr()
        return self._trad_repr()

    def _trad_repr(self) -> str:
        return super().__repr__()

    @classmethod
    def _len_if_available(cls, obj: Any) -> int | str:
        try:
            return len(obj)
        except TypeError:
            return 'N/A'

    def _table_repr(self) -> str:
        ret = tabulate(
            ((i,
              k,
              type(v).__name__,
              self._len_if_available(v),
              humanize.naturalsize(objsize.get_deep_size(v)))
             for i, (k, v) in enumerate(self.items())),
            ('#', 'Data file name', 'Type', 'Length', 'Size (in memory)'),
            tablefmt='rounded_outline',
        )
        waiting_for_terminal_repr(False)
        return ret


class MultiModelDataset(Dataset[GeneralModelT], Generic[GeneralModelT]):
    """
        Variant of Dataset that allows custom models to be set on individual data files

        Note that the general model still needs to hold for all data files, in addition to any
        custom models.
    """

    _custom_field_models: dict[str, GeneralModelT] = PrivateAttr(default={})

    def set_model(self, data_file: str, model: GeneralModelT) -> None:
        try:
            self._custom_field_models[data_file] = model
            if data_file in self.data:
                self._validate(data_file)
            else:
                self.data[data_file] = model()
        except ValidationError:
            del self._custom_field_models[data_file]
            raise

    def get_model(self, data_file: str) -> GeneralModelT:
        if data_file in self._custom_field_models:
            return self._custom_field_models[data_file]
        else:
            return self.get_model_class()

    def _validate(self, data_file: str) -> None:
        if data_file in self._custom_field_models:
            model = self._custom_field_models[data_file]
            if not is_model_instance(model):
                model = Model[model]
            data_obj = self._to_data_if_model(self.data[data_file])
            parsed_data = self._to_data_if_model(model(data_obj))
            self.data[data_file] = parsed_data
        super()._validate(data_file)  # validates all data according to ModelNewT

    @staticmethod
    def _to_data_if_model(data_obj: Any):
        if is_model_instance(data_obj):
            data_obj = data_obj.to_data()
        return data_obj
