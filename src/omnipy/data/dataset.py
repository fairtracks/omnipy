import asyncio
from collections import defaultdict, UserDict
from collections.abc import Iterable, Mapping, MutableMapping
from copy import copy
import json
import os
import tarfile
from typing import Any, Callable, cast, Generic, Iterator, overload, TYPE_CHECKING

from typing_extensions import TypeVar

from omnipy.data._data_class_creator import DataClassBase, DataClassBaseMeta
from omnipy.data._mixins.display import DatasetDisplayMixin
from omnipy.data._mixins.task import TaskDatasetMixin
from omnipy.data._selector import (create_updated_mapping,
                                   Index2DataItemsType,
                                   Key2DataItemType,
                                   prepare_selected_items_with_iterable_data,
                                   prepare_selected_items_with_mapping_data,
                                   select_keys)
from omnipy.data.constants import ASYNC_LOAD_SLEEP_TIME, DATA_KEY
from omnipy.data.helpers import (cleanup_name_qualname_and_module,
                                 is_model_instance,
                                 is_model_subclass)
from omnipy.data.model import Model
from omnipy.shared.protocols.data import IsDataset, IsModel, IsMultiModelDataset
from omnipy.shared.typedefs import TypeForm
from omnipy.util._pydantic import Undefined, UndefinedType, ValidationError
import omnipy.util._pydantic as pyd
from omnipy.util.decorators import call_super_if_available
from omnipy.util.helpers import (get_default_if_typevar,
                                 get_event_loop_and_check_if_loop_is_running,
                                 is_iterable,
                                 remove_forward_ref_notation)

if TYPE_CHECKING:
    from omnipy.components.remote.datasets import HttpUrlDataset
    from omnipy.components.remote.models import HttpUrlModel
    from omnipy.data._mimic_models import (Model_bool,
                                           Model_dict,
                                           Model_float,
                                           Model_int,
                                           Model_list,
                                           Model_str,
                                           Model_tuple_all_same,
                                           Model_tuple_pair)
    from omnipy.data._typedefs import _KeyT, _ValT, _ValT2

_ModelT = TypeVar('_ModelT', bound=IsModel)
_NewModelT = TypeVar('_NewModelT', bound=IsModel)
_GeneralModelT = TypeVar('_GeneralModelT', bound=IsModel)
_DatasetT = TypeVar('_DatasetT')

# def orjson_dumps(v, *, default):
#     # orjson.dumps returns bytes, to match standard json.dumps we need to decode
#     return orjson.dumps(v, default=default).decode()

# TODO: implement copy(), __copy__() and __deepcopy__() for Dataset and Model, making use of
#       pyd.BaseModel.copy()


class _DatasetMetaclass(DataClassBaseMeta, pyd.ModelMetaclass):
    ...


class Dataset(
        DatasetDisplayMixin,
        TaskDatasetMixin,
        DataClassBase,
        pyd.GenericModel,
        Generic[_ModelT],
        UserDict,
        metaclass=_DatasetMetaclass):
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
        arbitrary_types_allowed = True

        # TODO: Use json serializer package from the pydantic config instead of 'json'

        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

    data: dict[str, _ModelT] = pyd.Field(default={})

    def __class_getitem__(
        cls,
        params: type[_ModelT] | tuple[type[_ModelT]] | tuple[type[_ModelT], Any] | TypeVar
        | tuple[TypeVar, ...],
    ) -> 'type[Dataset[type[_ModelT]]]':
        # TODO: change model type to params: Type[Any] | tuple[Type[Any], ...]
        #       as in GenericModel.

        model = cls._prepare_params(params)
        orig_model = cls._clean_model(model)

        if cls == Dataset:
            if not isinstance(orig_model, TypeVar) and not is_model_subclass(orig_model):
                raise TypeError('Invalid model: {}! '.format(orig_model)
                                + 'omnipy Dataset models must be a specialization of the omnipy '
                                'Model class.')
        else:
            if isinstance(orig_model, TypeVar):
                model = get_default_if_typevar(orig_model)

        created_dataset = super().__class_getitem__(model)
        cls._recursively_set_allow_none(created_dataset._get_data_field())
        cleanup_name_qualname_and_module(cls, created_dataset, orig_model)

        return created_dataset

    @call_super_if_available(call_super_before_method=True)
    @classmethod
    def _clean_model(cls, model: TypeForm) -> TypeForm:
        return model

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

        model_cls = self.get_model_class()
        if model_cls == _ModelT:  # type: ignore[misc]
            self._raise_no_model_exception()

        model_or_dataset_as_input = False
        if DATA_KEY in super_kwargs:
            done = False
            while not done:
                match super_kwargs[DATA_KEY]:
                    case Dataset():
                        model_or_dataset_as_input = True
                        super_kwargs[DATA_KEY] = cast(Dataset, super_kwargs[DATA_KEY]).to_data()
                        done = True
                    case MutableMapping():
                        mapping_value = cast(MutableMapping, super_kwargs[DATA_KEY])
                        for key, val in mapping_value.items():
                            if is_model_instance(val):
                                model_or_dataset_as_input = True
                                mapping_value[key] = model_cls(val)
                        done = True
                    case Iterable():
                        try:
                            super_kwargs[DATA_KEY] = dict(cast(Iterable, super_kwargs[DATA_KEY]))
                        except TypeError as e:
                            raise TypeError('Data object must be a mapping or an iterable of '
                                            '(key, val) pairs') from e
                    case _:
                        done = True

        self._init(super_kwargs, **kwargs)

        try:
            self._primary_validation(super_kwargs)
        except ValidationError:
            if model_or_dataset_as_input:
                self._secondary_validation_from_data(super_kwargs)
            else:
                raise

        if not self.__doc__:
            self._set_standard_field_description()

    def _primary_validation(self, super_kwargs):
        # Pydantic validation of super_kwargs
        super().__init__(**super_kwargs)

    def _secondary_validation_from_data(self, super_kwargs):
        super().__init__()
        self.from_data(super_kwargs[DATA_KEY])

    def _init(self, super_kwargs: dict[str, Any], **kwargs: Any) -> None:
        ...

    # TODO: Revise with pydantic v2: __deepcopy__ is not defined for Dataset and Model, as it is not
    #       supported by pydantic v1. BaseModel.copy(deep=True) does not support a deepcopy memo.
    #       So we instead make use of the builtin support for deepcopy, which seems to work fine.
    #       However, __deepcopy__ in pydantic v2 is probably more efficient due to the memo and
    #       the Rust backend.

    def __copy__(self):
        return self.copy(deep=False)

    def copy(self, *, deep: bool = False, **kwargs) -> 'Dataset[_ModelT]':
        pydantic_copy = pyd.GenericModel.copy(self, deep=deep, **kwargs)
        if not deep:
            pydantic_copy.__dict__[DATA_KEY] = pydantic_copy.__dict__[DATA_KEY].copy()
        return pydantic_copy  # pyright: ignore [reportReturnType]

    @classmethod
    def clone_dataset_cls(cls: type[_DatasetT],
                          new_dataset_cls_name: str,
                          model_cls: type[_NewModelT] | None = None) -> type[IsDataset[_NewModelT]]:
        if model_cls:
            generic_dataset_cls = cls.__bases__[0]
            new_base_cls = generic_dataset_cls[model_cls]
        else:
            new_base_cls = cls

        new_dataset_cls = type(new_dataset_cls_name, (new_base_cls,), {})
        return cast(type[IsDataset[_NewModelT]], new_dataset_cls)

    @classmethod
    def _get_data_field(cls) -> pyd.ModelField:
        return cast(pyd.ModelField, cls.__fields__.get(DATA_KEY))

    @classmethod
    def get_model_class(cls) -> type[_ModelT]:
        """
        Returns the concrete Model class used for all data files in the dataset, e.g.:
        `Model[list[int]]`
        :return: The concrete Model class used for all data files in the dataset
        """
        return cls._clean_model(cls._get_data_field().type_)

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
        return ('This class represents a dataset in the `omnipy` Python package and contains '
                'a set of named data items that follows the same data model. '
                'It is a statically typed specialization of the Dataset class according to a '
                'particular specialization of the Model class. Both main classes are wrapping '
                'the excellent Python package named `pydantic`.')

    if TYPE_CHECKING:  # noqa: C901

        # The code below is a hack needed because ofa fundamental limitation of the current Python
        # typing syntax. There is no way (that we know of) to tell the type checkers that Model
        # objects can mimic the functionality of their type arguments, say that a Model[list] can
        # mimic a list. What we were aiming to do as a lesser hack was to tell to the type checkers
        # that the Model objects can be considered as inheriting from both the Model class
        # and the type argument class, e.g. Model[list] and list, but in a general way, using type
        # variables. As a workaround, we have to overload the Model.__new__ and Dataset.__getitem__
        # methods for the most important types.

        @overload
        def __getitem__(
            self: 'Dataset[Model[float]]',
            selector: str | int,
        ) -> Model_float:
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[int]]',
            selector: str | int,
        ) -> Model_int:
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[bool]]',
            selector: str | int,
        ) -> Model_bool:
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[str]]',
            selector: str | int,
        ) -> Model_str:
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[list[_ValT]]]',
            selector: str | int,
        ) -> Model_list[_ValT]:
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[tuple[_ValT, _ValT2]]]',
            selector: str | int,
        ) -> Model_tuple_pair[_ValT, _ValT2]:
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[tuple[_ValT, ...]]]',
            selector: str | int,
        ) -> Model_tuple_all_same[_ValT]:
            ...

        @overload
        def __getitem__(
            self: 'Dataset[Model[dict[_KeyT, _ValT]]]',
            selector: str | int,
        ) -> Model_dict[_KeyT, _ValT]:
            ...

        @overload
        def __getitem__(
            self: 'Dataset[_ModelT]',
            selector: str | int,
        ) -> _ModelT:
            ...
    else:

        # The only thing that should really be needed – if Python type hints would have able to
        # describe that Model objects can dynamically inherit from their type arguments. This would
        # at least go some way towards what we really want, which is a way to describe exactly the
        # way Model objects mimic the functionality of their type arguments.

        @overload
        def __getitem__(self: 'Dataset[_ModelT]', selector: str | int) -> _ModelT:
            ...

    @overload
    def __getitem__(self, selector: slice | Iterable[str | int]) -> 'Dataset[_ModelT]':
        ...

    def __getitem__(
            self,
            selector: str | int | slice | Iterable[str | int]) -> '_ModelT | Dataset[_ModelT]':
        selected_keys = select_keys(selector, self.data)

        if selected_keys.singular:
            value = self.data[selected_keys.keys[0]]
        else:
            value = self.__class__({key: self.data[key] for key in selected_keys.keys})

        return self._check_value(value)

    @call_super_if_available(call_super_before_method=True)
    def _check_value(self, value: Any) -> Any:
        return value

    def __delitem__(self, selector: str | int | slice | Iterable[str | int]) -> None:
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

    @overload
    def __setitem__(self, selector: str | int, data_obj: object) -> None:
        ...

    @overload
    def __setitem__(self,
                    selector: slice | Iterable[str | int],
                    data_obj: Mapping[str, object] | Iterable[object]) -> None:
        ...

    def __setitem__(
        self,
        selector: str | int | slice | Iterable[str | int],
        data_obj: object | Mapping[str, object] | Iterable[object],
    ) -> None:
        selected_keys = select_keys(selector, self.data)

        if selected_keys.singular:
            self._set_data_file_and_validate(selected_keys.keys[0], cast(_ModelT, data_obj))
        else:
            key_2_data_item: Key2DataItemType[object]
            index_2_data_items: Index2DataItemsType[object]

            if isinstance(data_obj, MutableMapping):
                key_2_data_item, index_2_data_items = \
                    prepare_selected_items_with_mapping_data(
                        selected_keys.keys, selected_keys.last_index,
                        cast(Mapping[str, object], data_obj),
                    )

            elif is_iterable(data_obj) and not isinstance(data_obj, (str, bytes)):
                key_2_data_item, index_2_data_items = \
                    prepare_selected_items_with_iterable_data(
                        selected_keys.keys, selected_keys.last_index, tuple(data_obj),
                        cast(Mapping[str, object], self.data),
                    )

            else:
                raise TypeError('Data object must be a mapping or an iterable')

            self._update_selected_items_with_data_items(key_2_data_item, index_2_data_items)

    def _update_selected_items_with_data_items(
        self,
        key_2_data_item: Key2DataItemType[object],
        index_2_data_item: Index2DataItemsType[object],
    ) -> None:

        updated_mapping = create_updated_mapping(
            cast(MutableMapping[str, object], self.data), key_2_data_item,
            index_2_data_item)  # pyright: ignore [reportUndefinedVariable]
        self._replace_data_with_mapping(updated_mapping)

    def _replace_data_with_mapping(self, updated_mapping: MutableMapping[str, object]) -> None:
        prev_data = self.data
        try:
            self.absorb_and_replace(self.__class__(updated_mapping))
        except Exception:
            self.data = prev_data
            raise

    def _set_data_file_and_validate(self, key: str, val: _ModelT) -> None:
        has_prev_value = key in self.data
        if has_prev_value:
            prev_value = self.data[key]

        try:
            self.data[key] = val
            self._validate_data_file(key)
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

    def _validate_data_file(self, _data_file: str) -> None:
        val = self.data[_data_file]
        if is_model_instance(val):
            self.data[_data_file] = self.get_model_class()(val)
        else:
            self._force_full_validation()

    def _force_full_validation(self):
        self.data = self.data  # Triggers pydantic validation, as validate_assignment=True

    def __iter__(self) -> Iterator:
        return UserDict.__iter__(self)

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in self.__dict__ or attr == DATA_KEY or attr.startswith('__'):
            super().__setattr__(attr, value)
        elif attr == 'repr_state':
            prop = getattr(self.__class__, attr)
            prop.__set__(self, value)
        else:
            raise RuntimeError('Model does not allow setting of extra attributes')

    @pyd.root_validator
    def _parse_root_object(cls, root_obj: dict[str, _ModelT]) -> Any:  # noqa
        assert DATA_KEY in root_obj
        data_dict = root_obj[DATA_KEY]
        model = cls.get_model_class()
        for key, val in data_dict.items():
            if val is None:
                data_dict[key] = model.parse_obj(val)
        return {DATA_KEY: data_dict}

    def to_data(self) -> dict[str, Any]:
        return {
            key: self._check_value(val)
            for key, val in pyd.GenericModel.dict(self, by_alias=True).get(DATA_KEY).items()
        }

    def from_data(self,
                  data: dict[str, Any] | Iterator[tuple[str, Any]],
                  update: bool = True) -> None:
        def callback_func(model: _ModelT, contents: Any):
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
            self.data[data_file] = new_model

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
        def callback_func(model: _ModelT, contents: Any):
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
    def to_json_schema(cls, pretty: bool = True) -> str | dict[str, str]:
        result = {}
        clean_dataset = super(Dataset, Dataset).__class_getitem__(cls.get_model_class())
        schema = clean_dataset.schema()
        for key, val in schema['properties'][DATA_KEY].items():
            result[key] = val
        result['title'] = cls.__name__
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

    def load(self,
             paths_or_urls: 'str | Iterable[str] | HttpUrlModel | HttpUrlDataset '
             '| Mapping[str, str | HttpUrlModel] | None' = None,
             by_file_suffix: bool = False,
             **kwargs: 'str | HttpUrlModel') -> list[asyncio.Task] | None:
        from omnipy import HttpUrlDataset, HttpUrlModel

        if paths_or_urls is None:
            assert len(kwargs) > 0, 'No paths or urls specified'
            paths_or_urls = kwargs
        else:
            assert len(kwargs) == 0, 'No keyword arguments allowed when paths_or_urls is specified'

        match paths_or_urls:
            case HttpUrlDataset():
                return self._load_http_urls(paths_or_urls)

            case HttpUrlModel():
                return self._load_http_urls(HttpUrlDataset({str(paths_or_urls): paths_or_urls}))

            case str():
                try:
                    http_url_dataset = HttpUrlDataset({paths_or_urls: paths_or_urls})
                except ValidationError:
                    return self._load_paths([paths_or_urls], by_file_suffix)
                return self._load_http_urls(http_url_dataset)

            case Mapping():
                try:
                    http_url_dataset = HttpUrlDataset(paths_or_urls)
                except ValidationError as exp:
                    raise NotImplementedError(
                        'Loading files with specified keys is not yet '
                        'implemented, as only tar.gz file import is '
                        'supported until serializers have been refactored.') from exp
                return self._load_http_urls(http_url_dataset)

            case Iterable():
                try:
                    path_or_url_iterable = cast(Iterable[str], paths_or_urls)
                    http_url_dataset = HttpUrlDataset(
                        zip(path_or_url_iterable, path_or_url_iterable))
                except ValidationError:
                    return self._load_paths(path_or_url_iterable, by_file_suffix)
                return self._load_http_urls(http_url_dataset)
            case _:
                raise TypeError(f'"paths_or_urls" argument is of incorrect type. Type '
                                f'{type(paths_or_urls)} is not supported.')

    def _load_http_urls(self, http_url_dataset: 'HttpUrlDataset') -> list[asyncio.Task]:
        from omnipy.components.remote.helpers import RateLimitingClientSession
        from omnipy.components.remote.tasks import get_json_from_api_endpoint
        hosts: defaultdict[str, list[int]] = defaultdict(list)
        for i, url in enumerate(http_url_dataset.values()):
            hosts[url.host].append(i)

        async def load_all():
            tasks = []

            for host in hosts:
                async with RateLimitingClientSession(
                        self.config.http_config_for_host[host].requests_per_time_period,
                        self.config.http_config_for_host[host].time_period_in_secs
                ) as client_session:
                    indices = hosts[host]
                    task = (
                        get_json_from_api_endpoint.refine(
                            output_dataset_param='output_dataset').run(
                                http_url_dataset[indices],
                                client_session=client_session,
                                output_dataset=self))
                    tasks.append(task)
                    while not task.done():
                        await asyncio.sleep(ASYNC_LOAD_SLEEP_TIME)

            await asyncio.gather(*tasks)
            return self

        loop, loop_is_running = get_event_loop_and_check_if_loop_is_running()

        if loop and loop_is_running:
            return loop.create_task(load_all())
        else:
            return asyncio.run(load_all())

    def _load_paths(self, path_or_urls: Iterable[str], by_file_suffix: bool) -> None:
        for path_or_url in path_or_urls:
            serializer_registry = self._get_serializer_registry()
            tar_gz_file_path = self._ensure_tar_gz_file(path_or_url)

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
                raise RuntimeError('Unable to load from serializer')

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
        from omnipy.components import get_serializer_registry
        return get_serializer_registry()

    def as_multi_model_dataset(self) -> 'IsMultiModelDataset[_ModelT]':
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
        return [(k, v.contents) if is_model_instance(v) else (k, v) for k, v in self.data.items()]


class MultiModelDataset(Dataset[_GeneralModelT], Generic[_GeneralModelT]):
    """
        Variant of Dataset that allows custom models to be set on individual data files

        Note that the general model still needs to hold for all data files, in addition to any
        custom models.
    """

    # Custom field models should really be a subtype of _ModelT, however this is currently not
    # checkable in the type system. Instead, we rely on the _validate method to ensure that the
    # custom field models are valid.
    _custom_field_models: dict[str, type[IsModel]] = pyd.PrivateAttr(default={})

    def set_model(self, data_file: str, model: type[IsModel]) -> None:
        try:
            self._custom_field_models[data_file] = model
            if data_file in self.data:
                self._validate_data_file(data_file)
            else:
                self.data[data_file] = model()
        except ValidationError:
            del self._custom_field_models[data_file]
            raise

    def get_model(self, data_file: str) -> type[IsModel]:
        if data_file in self._custom_field_models:
            return self._custom_field_models[data_file]
        else:
            return self.get_model_class()

    def from_data(self,
                  data: dict[str, Any] | Iterator[tuple[str, Any]],
                  update: bool = True) -> None:
        super().from_data(data, update)
        for data_file in self:
            self._validate_data_file_according_to_custom_field_model(data_file)
        self._force_full_validation()

    def _validate_data_file(self, data_file: str) -> None:
        self._validate_data_file_according_to_custom_field_model(data_file)
        self._force_full_validation()

    def _validate_data_file_according_to_custom_field_model(self, data_file: str):
        if data_file in self._custom_field_models:
            model = self._custom_field_models[data_file]
            if not is_model_instance(model):
                model = Model[model]
            data_obj = self._to_data_if_model(self.data[data_file])
            parsed_data = self._to_data_if_model(model(data_obj))
            self.data[data_file] = parsed_data

    @staticmethod
    def _to_data_if_model(data_obj: Any):
        if is_model_instance(data_obj):
            data_obj = data_obj.to_data()
        return data_obj
