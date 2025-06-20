import asyncio
from typing import (Any,
                    Callable,
                    ContextManager,
                    IO,
                    Iterable,
                    Iterator,
                    Mapping,
                    overload,
                    Protocol,
                    runtime_checkable,
                    Type,
                    TypeAlias)

from typing_extensions import TypeVar

from omnipy.shared.protocols._util import IsWeakKeyRefContainer
from omnipy.shared.protocols.builtins import IsMutableMapping
from omnipy.shared.protocols.config import IsDataConfig
from omnipy.shared.protocols.hub.log import CanLog
import omnipy.util._pydantic as pyd
from omnipy.util.setdeque import SetDeque

_RootT = TypeVar('_RootT', covariant=True)
_ModelT = TypeVar('_ModelT', bound='IsModel')

ContentsT = TypeVar('ContentsT', bound=object)
HasContentsT = TypeVar('HasContentsT', bound='HasContents')
ObjContraT = TypeVar('ObjContraT', contravariant=True, bound=object)

IsPathOrUrl: TypeAlias = 'str | IsHttpUrlModel'
IsPathsOrUrls: TypeAlias = 'Iterable[str] | IsHttpUrlDataset | Mapping[str, IsPathOrUrl]'
IsPathsOrUrlsOneOrMore: TypeAlias = 'IsPathOrUrl | IsPathsOrUrls'
IsPathsOrUrlsOneOrMoreOrNone: TypeAlias = 'IsPathsOrUrlsOneOrMore | None'


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
        value: dict[str, object] | Iterator[tuple[str, object]] | pyd.UndefinedType = pyd.Undefined,
        *,
        data: dict[str, object] | pyd.UndefinedType = pyd.Undefined,
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

    def save(self, path: str) -> None:
        ...

    @classmethod
    def load(
        cls,
        paths_or_urls: IsPathsOrUrlsOneOrMore = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> 'IsDataset[_ModelT] | asyncio.Task[IsDataset[_ModelT]]':
        ...

    def load_into(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMore = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> 'IsDataset[_ModelT] | asyncio.Task[IsDataset[_ModelT]]':
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


@runtime_checkable
class IsHttpUrlModel(IsModel, Protocol):
    ...


@runtime_checkable
class IsHttpUrlDataset(IsDataset, Protocol):
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


@runtime_checkable
class HasContents(Protocol[ContentsT]):
    @property
    def contents(self) -> ContentsT:
        ...

    @contents.setter
    def contents(self, value: ContentsT) -> None:
        ...


class IsSnapshotWrapper(Protocol[ObjContraT, ContentsT]):
    id: int
    snapshot: ContentsT

    def taken_of_same_obj(self, obj: ObjContraT) -> bool:
        ...

    def differs_from(self, obj: ObjContraT) -> bool:
        ...


class IsSnapshotHolder(IsWeakKeyRefContainer[HasContentsT,
                                             IsSnapshotWrapper[HasContentsT, ContentsT]],
                       Protocol[HasContentsT, ContentsT]):
    """"""
    def clear(self) -> None:
        ...

    def all_are_empty(self, debug: bool = False) -> bool:
        ...

    def get_deepcopy_content_ids(self) -> SetDeque[int]:
        ...

    def get_deepcopy_content_ids_scheduled_for_deletion(self) -> SetDeque[int]:
        ...

    def schedule_deepcopy_content_ids_for_deletion(self, *keys: int) -> None:
        ...

    def delete_scheduled_deepcopy_content_ids(self) -> None:
        ...

    def take_snapshot_setup(self) -> None:
        ...

    def take_snapshot_teardown(self) -> None:
        ...

    def take_snapshot(self, obj: HasContentsT) -> None:
        ...


@runtime_checkable
class IsDataClassCreator(Protocol[HasContentsT, ContentsT]):
    """"""
    @property
    def config(self) -> IsDataConfig:
        ...

    def set_config(self, config: IsDataConfig) -> None:
        ...

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[HasContentsT, ContentsT]:
        ...

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        ...
