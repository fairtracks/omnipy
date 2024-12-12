from abc import abstractmethod
from collections.abc import Sized
from typing import (AbstractSet,
                    Any,
                    Callable,
                    Hashable,
                    IO,
                    Iterable,
                    Iterator,
                    Mapping,
                    overload,
                    Protocol,
                    runtime_checkable,
                    Type,
                    TypeVar)

from omnipy.api.protocols.private.log import CanLog
from omnipy.util.pydantic import Undefined, UndefinedType

_RootT = TypeVar('_RootT', covariant=True)
_ModelT = TypeVar('_ModelT', bound='IsModel')
KeyT = TypeVar('KeyT')
KeyContraT = TypeVar('KeyContraT', bound=Hashable, contravariant=True)
ValT = TypeVar('ValT')
ValCoT = TypeVar('ValCoT', covariant=True)

RootT = TypeVar('RootT')


class SupportsKeysAndGetItem(Protocol[KeyT, ValCoT]):
    def keys(self) -> Iterable[KeyT]:
        ...

    def __getitem__(self, __key: KeyT) -> ValCoT:
        ...


class IsSet(Protocol):
    """
    IsSet is a protocol with the same interface as the abstract class Set.
    It is the protocol of a finite, iterable container.
    """
    def __le__(self, other: AbstractSet) -> bool:
        ...

    def __lt__(self, other: AbstractSet) -> bool:
        ...

    def __gt__(self, other: AbstractSet) -> bool:
        ...

    def __ge__(self, other: AbstractSet) -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        ...

    def __and__(self, other: Iterable) -> 'IsSet':
        ...

    def __rand__(self, other: Iterable) -> 'IsSet':
        ...

    def isdisjoint(self, other: AbstractSet) -> bool:
        ...

    def __or__(self, other: Iterable) -> 'IsSet':
        ...

    def __ror__(self, other: Iterable) -> 'IsSet':
        ...

    def __sub__(self, other: Iterable) -> 'IsSet':
        ...

    def __rsub__(self, other: Iterable) -> 'IsSet':
        ...

    def __xor__(self, other: Iterable) -> 'IsSet':
        ...

    def __rxor__(self, other: Iterable) -> 'IsSet':
        ...


class IsMapping(Protocol[KeyT, ValT]):
    """
    IsMapping is a protocol with the same interface as the abstract class Mapping.
    It is the protocol of a generic container for associating key/value pairs.
    """
    @abstractmethod
    def __getitem__(self, key: KeyT) -> ValT:
        raise KeyError

    def get(self, key: KeyT, /) -> ValT | None:
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        ...

    def __contains__(self, key: KeyT) -> bool:
        ...

    def keys(self) -> 'IsKeysView[KeyT]':
        """
        D.keys() -> a set-like object providing a view on D's keys
        """
        ...

    def items(self) -> 'IsItemsView[KeyT, ValT]':
        """
        D.items() -> a set-like object providing a view on D's items
        """
        ...

    def values(self) -> 'IsValuesView[ValT]':
        """
        D.values() -> an object providing a view on D's values
        """
        ...

    def __eq__(self, other: object) -> bool:
        ...


class IsMappingView(Sized, Protocol):
    def __len__(self) -> int:
        ...

    def __repr__(self) -> str:
        ...


class IsKeysView(IsMappingView, Protocol[KeyT]):
    def __contains__(self, key: KeyT) -> bool:
        ...

    def __iter__(self) -> Iterator[KeyT]:
        ...


class IsItemsView(IsMappingView, Protocol[KeyT, ValT]):
    def __contains__(self, item: tuple[KeyT, ValT]) -> bool:
        ...

    def __iter__(self) -> Iterator[tuple[KeyT, ValT]]:
        ...


class IsValuesView(IsMappingView, Protocol[ValT]):
    def __contains__(self, value: ValT) -> bool:
        ...

    def __iter__(self) -> Iterator[ValT]:
        ...


class IsMutableMapping(IsMapping[KeyT, ValT], Protocol[KeyT, ValT]):
    """
    IsMutableMapping is a protocol with the same interface as the abstract class MutableMapping.
    It is the protocol of a generic mutable container for associating key/value pairs.
    """
    def __setitem__(
        self,
        selector: str | int | slice | Iterable[str | int],
        data_obj: ValT | Mapping[str, ValT] | Iterable[ValT],
    ) -> None:
        ...

    def __delitem__(self, key: KeyT) -> None:
        ...

    def pop(self, key: KeyT, /) -> ValT:
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised.
        """
        ...

    def popitem(self) -> tuple[KeyT, ValT]:
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair
           as a 2-tuple; but raise KeyError if D is empty.
        """
        ...

    def clear(self) -> None:
        """
        D.clear() -> None.  Remove all items from D.
        """
        ...

    @overload
    def update(self, other: SupportsKeysAndGetItem[KeyT, ValT], /, **kwargs: ValT) -> None:
        ...

    @overload
    def update(self, other: Iterable[tuple[KeyT, ValT]], /, **kwargs: ValT) -> None:
        ...

    @overload
    def update(self, /, **kwargs: ValT) -> None:
        ...

    def update(self, other: Any = None, /, **kwargs: ValT) -> None:
        """
        D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k, v in F.items(): D[k] = v
        """
        ...

    def setdefault(self, key: KeyT, default: ValT, /):
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
        ...


@runtime_checkable
class IsModel(Protocol[_RootT]):
    # @property
    # def contents(self) -> _RootT:
    #     ...
    ...


class IsDataset(IsMutableMapping[str, _ModelT], Protocol[_ModelT]):
    """
    Dict-based container of data files that follow a specific Model
    """
    def __init__(
        self,
        value: dict[str, object] | Iterator[tuple[str, object]] | UndefinedType = Undefined,
        *,
        data: dict[str, object] | UndefinedType = Undefined,
        **input_data: object,
    ) -> None:
        ...

    @classmethod
    def get_model_class(cls) -> type[_ModelT]:
        """
        Returns the concrete Model class used for all data files in the dataset, e.g.:
        `Model[list[int]]`
        :return: The concrete Model class used for all data files in the dataset
        """
        ...

    def to_data(self) -> dict[str, Any]:
        ...

    def from_data(self,
                  data: dict[str, Any] | Iterator[tuple[str, Any]],
                  update: bool = True) -> None:
        ...

    def to_json(self, pretty=True) -> dict[str, str]:
        ...

    def from_json(self,
                  data: dict[str, str] | Iterator[tuple[str, str]],
                  update: bool = True) -> None:
        ...

    @classmethod
    def to_json_schema(cls, pretty=True) -> str | dict[str, str]:
        ...

    @overload
    def __getitem__(self, selector: str | int) -> _ModelT:
        ...

    @overload
    def __getitem__(self, selector: slice | Iterable[str | int]) -> 'IsDataset[_ModelT]':
        ...

    def __getitem__(
            self,
            selector: str | int | slice | Iterable[str | int]) -> '_ModelT | IsDataset[_ModelT]':
        ...

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
        ...

    def __delitem__(self, selector: str | int | slice | Iterable[str | int]) -> None:
        ...


class IsMultiModelDataset(IsDataset[_ModelT], Protocol[_ModelT]):
    """
        Variant of Dataset that allows custom models to be set on individual data files
    """
    def set_model(self, data_file: str, model: type[IsModel]) -> None:
        ...

    def get_model(self, data_file: str) -> type[IsModel]:
        ...


class IsSerializer(Protocol):
    """"""
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        ...

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        ...

    @classmethod
    def get_output_file_suffix(cls) -> str:
        ...

    @classmethod
    def serialize(cls, dataset: IsDataset) -> bytes | memoryview:
        ...

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> IsDataset:
        ...


class IsTarFileSerializer(IsSerializer, Protocol):
    @classmethod
    def create_tarfile_from_dataset(cls,
                                    dataset: IsDataset,
                                    data_encode_func: Callable[..., bytes | memoryview]) -> bytes:
        """"""
        ...

    @classmethod
    def create_dataset_from_tarfile(cls,
                                    dataset: IsDataset,
                                    tarfile_bytes: bytes,
                                    data_decode_func: Callable[[IO[bytes]], Any],
                                    dictify_object_func: Callable[[str, Any], dict | str],
                                    import_method: str = 'from_data',
                                    any_file_suffix: bool = False) -> None:
        ...


@runtime_checkable
class IsSerializerRegistry(Protocol):
    """"""
    def __init__(self) -> None:
        ...

    def register(self, serializer_cls: Type[IsSerializer]) -> None:
        ...

    @property
    def serializers(self) -> tuple[Type[IsSerializer], ...]:
        ...

    @property
    def tar_file_serializers(self) -> tuple[Type[IsTarFileSerializer], ...]:
        ...

    def auto_detect(self, dataset: IsDataset) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        ...

    def auto_detect_tar_file_serializer(
            self, dataset: IsDataset) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        ...

    @classmethod
    def _autodetect_serializer(cls, dataset,
                               serializers) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        ...

    def detect_tar_file_serializers_from_dataset_cls(
            self, dataset: IsDataset) -> tuple[Type[IsTarFileSerializer], ...]:
        ...

    def detect_tar_file_serializers_from_file_suffix(
            self, file_suffix: str) -> tuple[Type[IsTarFileSerializer], ...]:
        ...

    def load_from_tar_file_path_based_on_file_suffix(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset) -> IsDataset | None:
        ...

    def load_from_tar_file_path_based_on_dataset_cls(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset) -> IsDataset | None:
        ...
