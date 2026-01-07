import asyncio
from dataclasses import dataclass
import functools
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
                    TypeAlias,
                    TypedDict)

from typing_extensions import Self, TypeVar

from omnipy.shared.protocols._util import IsWeakKeyRefContainer
from omnipy.shared.protocols.builtins import IsMutableMapping
from omnipy.shared.protocols.config import (IsDataConfig,
                                            IsJupyterUserInterfaceConfig,
                                            IsLayoutConfig,
                                            IsTextConfig)
from omnipy.shared.protocols.hub.log import CanLog
from omnipy.util._pydantic import Undefined, UndefinedType
import omnipy.util._pydantic as pyd
from omnipy.util.setdeque import SetDeque

_RootT = TypeVar('_RootT', covariant=True)
_ModelOrDatasetT = TypeVar('_ModelOrDatasetT', bound='IsModel | IsDataset')

ContentT = TypeVar('ContentT', bound=object)
HasContentT = TypeVar('HasContentT', bound='HasContent')
ObjContraT = TypeVar('ObjContraT', contravariant=True, bound=object)

IsPathOrUrl: TypeAlias = 'str | IsHttpUrlModel'
IsPathsOrUrls: TypeAlias = 'Iterable[str] | IsHttpUrlDataset | Mapping[str, IsPathOrUrl]'
IsPathsOrUrlsOneOrMore: TypeAlias = 'IsPathOrUrl | IsPathsOrUrls'
IsPathsOrUrlsOneOrMoreOrNone: TypeAlias = 'IsPathsOrUrlsOneOrMore | None'


@runtime_checkable
@dataclass(frozen=True, kw_only=True)
class IsPendingData(Protocol):
    job_name: str
    job_unique_name: str


@runtime_checkable
@dataclass(frozen=True, kw_only=True)
class IsFailedData(Protocol):
    job_name: str
    job_unique_name: str
    exception: BaseException


@runtime_checkable
class HasData(Protocol):
    data: dict[str, Any | IsPendingData | IsFailedData]


@runtime_checkable
class IsModel(Protocol[_RootT]):
    @property
    def content(self) -> _RootT:
        ...


@runtime_checkable
class IsDataset(IsMutableMapping[str, _ModelOrDatasetT], Protocol[_ModelOrDatasetT]):
    """
    Dict-based container of data files that follow a specific Model
    """
    def __init__(
        self,
        value: Mapping[str, object] | Iterator[tuple[str, object]] | UndefinedType = Undefined,
        *,
        data: Mapping[str, object] | UndefinedType = Undefined,
        **input_data: object,
    ) -> None:
        ...

    @classmethod
    @functools.cache
    def get_type(cls) -> type[_ModelOrDatasetT]:
        """
        Returns the concrete type (Model or Dataset class) used for all
        data files in the dataset, e.g.: `Model[list[int]]`, or
        `Dataset[Model[dict[str, float]]]` for nested datasets.
        :return: The concrete type (Model or Dataset class) used for all
                 data files in the dataset.
        """
        ...

    def to_data(self) -> dict[str, Any]:
        ...

    def from_data(self,
                  data: Mapping[str, Any] | Iterable[tuple[str, Any]],
                  update: bool = True) -> None:
        ...

    def to_json(self, pretty=True) -> dict[str, str]:
        ...

    def from_json(self,
                  data: Mapping[str, str] | Iterable[tuple[str, str]],
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
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        ...

    def load_into(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        ...

    @property
    def available_data(self) -> Self:
        ...

    @property
    def pending_data(self) -> Self:
        ...

    @property
    def failed_data(self) -> Self:
        ...

    def pending_task_details(self) -> dict[str, IsPendingData]:
        ...

    def failed_task_details(self) -> dict[str, IsFailedData]:
        ...

    # TODO: Remove methods of IsDataset that overlap with IsMutableMapping?

    @overload
    def __getitem__(self, selector: str | int) -> _ModelOrDatasetT:
        ...

    @overload
    def __getitem__(self, selector: slice | Iterable[str | int]) -> Self:
        ...

    def __getitem__(self,
                    selector: str | int | slice | Iterable[str | int]) -> '_ModelOrDatasetT | Self':
        ...

    @overload
    def __setitem__(self, selector: str | int, data_obj: _ModelOrDatasetT) -> None:
        ...

    @overload
    def __setitem__(self,
                    selector: slice | Iterable[str | int],
                    data_obj: Mapping[str, _ModelOrDatasetT] | Iterable[_ModelOrDatasetT]) -> None:
        ...

    def __setitem__(
        self,
        selector: str | int | slice | Iterable[str | int],
        data_obj: _ModelOrDatasetT | Mapping[str, _ModelOrDatasetT] | Iterable[_ModelOrDatasetT],
    ) -> None:
        ...

    def __delitem__(self, selector: str | int | slice | Iterable[str | int]) -> None:
        ...


@runtime_checkable
class IsMultiModelDataset(IsDataset[_ModelOrDatasetT], Protocol[_ModelOrDatasetT]):
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


@runtime_checkable
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
class HasContent(Protocol[ContentT]):
    @property
    def content(self) -> ContentT:
        ...

    @content.setter
    def content(self, value: ContentT) -> None:
        ...


@runtime_checkable
class IsSnapshotWrapper(Protocol[ObjContraT, ContentT]):
    id: int
    snapshot: ContentT

    def taken_of_same_obj(self, obj: ObjContraT) -> bool:
        ...

    def differs_from(self, obj: ObjContraT) -> bool:
        ...


@runtime_checkable
class IsSnapshotHolder(IsWeakKeyRefContainer[HasContentT, IsSnapshotWrapper[HasContentT, ContentT]],
                       Protocol[HasContentT, ContentT]):
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

    def take_snapshot(self, obj: HasContentT) -> None:
        ...


class AvailableDisplayDims(TypedDict):
    width: pyd.NonNegativeInt | None
    height: pyd.NonNegativeInt | None


@runtime_checkable
class IsReactive(Protocol[ContentT]):
    @property
    def value(self) -> ContentT:
        ...

    def set(self, value: ContentT):
        ...


@runtime_checkable
class IsReactiveObjects(Protocol):
    jupyter_ui_config: IsReactive[IsJupyterUserInterfaceConfig]
    text_config: IsReactive[IsTextConfig]
    layout_config: IsReactive[IsLayoutConfig]
    available_display_dims_in_px: IsReactive[AvailableDisplayDims]

    def __eq__(self, other) -> bool:
        ...


@runtime_checkable
class IsDataClassCreator(Protocol[HasContentT, ContentT]):
    """"""
    @property
    def config(self) -> IsDataConfig:
        ...

    def set_config(self, config: IsDataConfig) -> None:
        ...

    @property
    def reactive_objects(self) -> IsReactiveObjects | None:
        ...

    def set_reactive_objects(self, reactive_objects: IsReactiveObjects) -> None:
        ...

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[HasContentT, ContentT]:
        ...

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        ...
