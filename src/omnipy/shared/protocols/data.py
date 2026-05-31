"""Protocols for Omnipy data models, datasets, serializers, and reactive state."""

import asyncio
from dataclasses import dataclass
import functools
import os
from textwrap import dedent
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

from typing_extensions import override, Self, TypeVar

from omnipy.shared.protocols._util import IsWeakKeyRefContainer
from omnipy.shared.protocols.config import (IsDataConfig,
                                            IsJupyterUserInterfaceConfig,
                                            IsLayoutConfig,
                                            IsTextConfig)
from omnipy.shared.protocols.hub.log import CanLog
from omnipy.shared.protocols.typing import IsMutableMapping
from omnipy.util.helpers import is_package_editable
from omnipy.util.pydantic import Undefined, UndefinedType
import omnipy.util.pydantic as pyd
from omnipy.util.setdeque import SetDeque

_RootT = TypeVar('_RootT')
_DatasetT = TypeVar('_DatasetT', bound='IsDataset')
_ModelOrDatasetT = TypeVar('_ModelOrDatasetT', bound='IsModel | IsDataset')

ContentT = TypeVar('ContentT', bound=object)
HasContentT = TypeVar('HasContentT', bound='HasContent')
ObjContraT = TypeVar('ObjContraT', contravariant=True, bound=object)


if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISDATACLASSCREATOR_CONFIG_SUMMARY'] = (
        'Return the data configuration shared by the owning data-class family.')
    os.environ['OMNIPY_MACRO_ISDATACLASSCREATOR_CONFIG_DETAILS'] = dedent("""\
        Returns:
            IsDataConfig: Shared configuration object used by related models and datasets.
    """)

    os.environ['OMNIPY_MACRO_ISDATACLASSCREATOR_SET_CONFIG_SUMMARY'] = (
        'Replace the shared data configuration for the owning data-class family.')
    os.environ['OMNIPY_MACRO_ISDATACLASSCREATOR_SET_CONFIG_DETAILS'] = dedent("""\
        Args:
            config: Data configuration object to store for related models and datasets.
    """)

IsPathOrUrl: TypeAlias = 'str | IsHttpUrlModel'
IsPathsOrUrls: TypeAlias = 'Iterable[str] | IsHttpUrlDataset | Mapping[str, IsPathOrUrl]'
IsPathsOrUrlsOneOrMore: TypeAlias = 'IsPathOrUrl | IsPathsOrUrls'
IsPathsOrUrlsOneOrMoreOrNone: TypeAlias = 'IsPathsOrUrlsOneOrMore | None'


@runtime_checkable
@dataclass(frozen=True, kw_only=True)
class IsPendingData(Protocol):
    """Metadata describing a dataset entry that is still processing.

    Used for items backed by asynchronous work that has not completed yet.
    """

    job_name: str
    job_unique_name: str


@runtime_checkable
@dataclass(frozen=True, kw_only=True)
class IsFailedData(Protocol):
    """Metadata describing a dataset entry whose asynchronous load failed."""

    job_name: str
    job_unique_name: str
    exception: BaseException


@runtime_checkable
class HasData(Protocol):
    """Object exposing an internal mapping of loaded, pending, and failed items."""

    data: dict[str, Any | IsPendingData | IsFailedData]


@runtime_checkable
class HasContent(Protocol[ContentT]):
    """Object with a typed ``content`` value that can be read or replaced."""

    @property
    def content(self) -> ContentT:
        """Content.
        
        Returns:
            ContentT: Result produced by ``content()``.
        """
        ...

    @content.setter
    def content(self, value: ContentT) -> None:
        """Content.
        
        Args:
            value: (ContentT) Argument passed to ``content()``.
        """
        ...


@runtime_checkable
class IsModel(HasContent[_RootT], Protocol[_RootT]):
    """Single-value data wrapper with typed content and conversion support."""

    @classmethod
    def full_type(cls) -> type[_RootT]:
        """Full type.
        
        Returns:
            type[_RootT]: Result produced by ``full_type()``.
        """
        ...


@runtime_checkable
class IsDataset(IsMutableMapping[str, _ModelOrDatasetT], Protocol[_ModelOrDatasetT]):
    """Dictionary-like collection of named models or nested datasets.

    Datasets expose conversion helpers for plain data, JSON, and file-based
    load/save operations.
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
        """Get type.
        
        Returns:
            type[_ModelOrDatasetT]: Result produced by ``get_type()``.
        """
        ...

    def to_data(self) -> dict[str, Any]:
        """To data.
        
        Returns:
            dict[str, Any]: Result produced by ``to_data()``.
        """
        ...

    def from_data(self,
                  data: Mapping[str, Any] | Iterable[tuple[str, Any]],
                  update: bool = True) -> None:
        """From data.
        
        Args:
            data: (Mapping[str, Any] | Iterable[tuple[str, Any]]) Argument passed to ``from_data()``.
            update: (bool) Argument passed to ``from_data()``.
        """
        ...

    def to_json(self, pretty=True) -> dict[str, str]:
        """To json.
        
        Args:
            pretty: Argument passed to ``to_json()``.
        
        Returns:
            dict[str, str]: Result produced by ``to_json()``.
        """
        ...

    def from_json(self,
                  data: Mapping[str, str] | Iterable[tuple[str, str]],
                  update: bool = True) -> None:
        """From json.
        
        Args:
            data: (Mapping[str, str] | Iterable[tuple[str, str]]) Argument passed to ``from_json()``.
            update: (bool) Argument passed to ``from_json()``.
        """
        ...

    @classmethod
    def to_json_schema(cls, pretty=True) -> str | dict[str, str]:
        """To json schema.
        
        Args:
            pretty: Argument passed to ``to_json_schema()``.
        
        Returns:
            str | dict[str, str]: Result produced by ``to_json_schema()``.
        """
        ...

    def save(self, path: str) -> None:
        """Save.
        
        Args:
            path: (str) Argument passed to ``save()``.
        """
        ...

    @classmethod
    def load(
        cls,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Load.
        
        Args:
            paths_or_urls: (IsPathsOrUrlsOneOrMoreOrNone) Argument passed to ``load()``.
            by_file_suffix: (bool) Argument passed to ``load()``.
            as_mime_type: (None | str) Argument passed to ``load()``.
            kwargs: (IsPathOrUrl) Argument passed to ``load()``.
        
        Returns:
            Self | asyncio.Task[Self]: Result produced by ``load()``.
        """
        ...

    def load_into(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Load into.
        
        Args:
            paths_or_urls: (IsPathsOrUrlsOneOrMoreOrNone) Argument passed to ``load_into()``.
            by_file_suffix: (bool) Argument passed to ``load_into()``.
            as_mime_type: (None | str) Argument passed to ``load_into()``.
            kwargs: (IsPathOrUrl) Argument passed to ``load_into()``.
        
        Returns:
            Self | asyncio.Task[Self]: Result produced by ``load_into()``.
        """
        ...

    @property
    def available_data(self) -> Self:
        """Available data.
        
        Returns:
            Self: Result produced by ``available_data()``.
        """
        ...

    @property
    def pending_data(self) -> Self:
        """Pending data.
        
        Returns:
            Self: Result produced by ``pending_data()``.
        """
        ...

    @property
    def failed_data(self) -> Self:
        """Failed data.
        
        Returns:
            Self: Result produced by ``failed_data()``.
        """
        ...

    def pending_task_details(self) -> dict[str, IsPendingData]:
        """Pending task details.
        
        Returns:
            dict[str, IsPendingData]: Result produced by ``pending_task_details()``.
        """
        ...

    def failed_task_details(self) -> dict[str, IsFailedData]:
        """Failed task details.
        
        Returns:
            dict[str, IsFailedData]: Result produced by ``failed_task_details()``.
        """
        ...

    # TODO: Remove methods of IsDataset that overlap with IsMutableMapping?

    @overload
    def __getitem__(self, selector: str | int) -> _ModelOrDatasetT:
        ...

    @overload
    def __getitem__(self, selector: slice | Iterable[str | int]) -> Self:
        ...

    @override
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
    """Dataset protocol that can assign different model classes per item."""
    def set_model(self, data_file: str, model: type[IsModel]) -> None:
        """Set model.
        
        Args:
            data_file: (str) Argument passed to ``set_model()``.
            model: (type[IsModel]) Argument passed to ``set_model()``.
        """
        ...

    def get_model(self, data_file: str) -> type[IsModel]:
        """Get model.
        
        Args:
            data_file: (str) Argument passed to ``get_model()``.
        
        Returns:
            type[IsModel]: Result produced by ``get_model()``.
        """
        ...


@runtime_checkable
class IsHttpUrlModel(IsModel, Protocol):
    """Model protocol representing a validated HTTP URL value."""

    ...


@runtime_checkable
class IsHttpUrlDataset(IsDataset, Protocol):
    """Dataset protocol for collections of HTTP URL model entries."""

    ...


class IsSerializer(Protocol[_DatasetT]):
    """Serializer interface for converting datasets to and from bytes."""

    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        """Is dataset directly supported.
        
        Args:
            dataset: (IsDataset) Argument passed to ``is_dataset_directly_supported()``.
        
        Returns:
            bool: Result produced by ``is_dataset_directly_supported()``.
        """
        ...

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        """Get dataset cls for new.
        
        Returns:
            Type[IsDataset]: Result produced by ``get_dataset_cls_for_new()``.
        """
        ...

    @classmethod
    def get_output_file_suffix(cls) -> str:
        """Get output file suffix.
        
        Returns:
            str: Result produced by ``get_output_file_suffix()``.
        """
        ...

    @classmethod
    def serialize(cls, dataset: _DatasetT) -> bytes | memoryview:
        """Serialize.
        
        Args:
            dataset: (_DatasetT) Argument passed to ``serialize()``.
        
        Returns:
            bytes | memoryview: Result produced by ``serialize()``.
        """
        ...

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> _DatasetT:
        """Deserialize.
        
        Args:
            serialized: (bytes) Argument passed to ``deserialize()``.
            any_file_suffix: Argument passed to ``deserialize()``.
        
        Returns:
            _DatasetT: Result produced by ``deserialize()``.
        """
        ...


@runtime_checkable
class IsTarFileSerializer(IsSerializer[_DatasetT], Protocol[_DatasetT]):
    """Serializer extension that stores dataset entries inside tar archives."""

    @classmethod
    def create_tarfile_from_dataset(cls,
                                    dataset: _DatasetT,
                                    data_encode_func: Callable[..., bytes | memoryview]) -> bytes:
        """Create tarfile from dataset.
        
        Args:
            dataset: (_DatasetT) Argument passed to ``create_tarfile_from_dataset()``.
            data_encode_func: (Callable[..., bytes | memoryview]) Argument passed to ``create_tarfile_from_dataset()``.
        
        Returns:
            bytes: Result produced by ``create_tarfile_from_dataset()``.
        """

        ...

    @classmethod
    def create_dataset_from_tarfile(cls,
                                    dataset: _DatasetT,
                                    tarfile_bytes: bytes,
                                    data_decode_func: Callable[[IO[bytes]], Any],
                                    dictify_object_func: Callable[[str, Any], dict | str],
                                    import_method: str = 'from_data',
                                    any_file_suffix: bool = False) -> None:
        """Create dataset from tarfile.
        
        Args:
            dataset: (_DatasetT) Argument passed to ``create_dataset_from_tarfile()``.
            tarfile_bytes: (bytes) Argument passed to ``create_dataset_from_tarfile()``.
            data_decode_func: (Callable[[IO[bytes]], Any]) Argument passed to ``create_dataset_from_tarfile()``.
            dictify_object_func: (Callable[[str, Any], dict | str]) Argument passed to ``create_dataset_from_tarfile()``.
            import_method: (str) Argument passed to ``create_dataset_from_tarfile()``.
            any_file_suffix: (bool) Argument passed to ``create_dataset_from_tarfile()``.
        """
        ...


@runtime_checkable
class IsSerializerRegistry(Protocol):
    """Registry that tracks serializers and selects suitable ones for datasets."""

    def __init__(self) -> None:
        ...

    def register(self, serializer_cls: Type[IsSerializer]) -> None:
        """Register.
        
        Args:
            serializer_cls: (Type[IsSerializer]) Argument passed to ``register()``.
        """
        ...

    @property
    def serializers(self) -> tuple[Type[IsSerializer], ...]:
        """Serializers.
        
        Returns:
            tuple[Type[IsSerializer], ...]: Result produced by ``serializers()``.
        """
        ...

    @property
    def tar_file_serializers(self) -> tuple[Type[IsTarFileSerializer], ...]:
        """Tar file serializers.
        
        Returns:
            tuple[Type[IsTarFileSerializer], ...]: Result produced by ``tar_file_serializers()``.
        """
        ...

    def auto_detect(self, dataset: IsDataset) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        """Auto detect.
        
        Args:
            dataset: (IsDataset) Argument passed to ``auto_detect()``.
        
        Returns:
            tuple[IsDataset, IsSerializer] | tuple[None, None]: Result produced by ``auto_detect()``.
        """
        ...

    def auto_detect_tar_file_serializer(
            self, dataset: IsDataset) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        """Auto detect tar file serializer.
        
        Args:
            dataset: (IsDataset) Argument passed to ``auto_detect_tar_file_serializer()``.
        
        Returns:
            tuple[IsDataset, IsSerializer] | tuple[None, None]: Result produced by ``auto_detect_tar_file_serializer()``.
        """
        ...

    @classmethod
    def _autodetect_serializer(cls, dataset,
                               serializers) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        ...

    def detect_tar_file_serializers_from_dataset_cls(
            self, dataset: IsDataset) -> tuple[Type[IsTarFileSerializer], ...]:
        """Detect tar file serializers from dataset cls.
        
        Args:
            dataset: (IsDataset) Argument passed to ``detect_tar_file_serializers_from_dataset_cls()``.
        
        Returns:
            tuple[Type[IsTarFileSerializer], ...]: Result produced by ``detect_tar_file_serializers_from_dataset_cls()``.
        """
        ...

    def detect_tar_file_serializers_from_file_suffix(
            self, file_suffix: str) -> tuple[Type[IsTarFileSerializer], ...]:
        """Detect tar file serializers from file suffix.
        
        Args:
            file_suffix: (str) Argument passed to ``detect_tar_file_serializers_from_file_suffix()``.
        
        Returns:
            tuple[Type[IsTarFileSerializer], ...]: Result produced by ``detect_tar_file_serializers_from_file_suffix()``.
        """
        ...

    def load_from_tar_file_path_based_on_file_suffix(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset) -> IsDataset | None:
        """Load from tar file path based on file suffix.
        
        Args:
            log_obj: (CanLog) Argument passed to ``load_from_tar_file_path_based_on_file_suffix()``.
            tar_file_path: (str) Argument passed to ``load_from_tar_file_path_based_on_file_suffix()``.
            to_dataset: (IsDataset) Argument passed to ``load_from_tar_file_path_based_on_file_suffix()``.
        
        Returns:
            IsDataset | None: Result produced by ``load_from_tar_file_path_based_on_file_suffix()``.
        """
        ...

    def load_from_tar_file_path_based_on_dataset_cls(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset) -> IsDataset | None:
        """Load from tar file path based on dataset cls.
        
        Args:
            log_obj: (CanLog) Argument passed to ``load_from_tar_file_path_based_on_dataset_cls()``.
            tar_file_path: (str) Argument passed to ``load_from_tar_file_path_based_on_dataset_cls()``.
            to_dataset: (IsDataset) Argument passed to ``load_from_tar_file_path_based_on_dataset_cls()``.
        
        Returns:
            IsDataset | None: Result produced by ``load_from_tar_file_path_based_on_dataset_cls()``.
        """
        ...


@runtime_checkable
class IsSnapshotWrapper(Protocol[ObjContraT, ContentT]):
    """Snapshot record linking an object identity to captured content."""

    id: int
    snapshot: ContentT

    def taken_of_same_obj(self, obj: ObjContraT) -> bool:
        """Taken of same obj.
        
        Args:
            obj: (ObjContraT) Argument passed to ``taken_of_same_obj()``.
        
        Returns:
            bool: Result produced by ``taken_of_same_obj()``.
        """
        ...

    def differs_from(self, obj: ObjContraT) -> bool:
        """Differs from.
        
        Args:
            obj: (ObjContraT) Argument passed to ``differs_from()``.
        
        Returns:
            bool: Result produced by ``differs_from()``.
        """
        ...


@runtime_checkable
class IsSnapshotHolder(IsWeakKeyRefContainer[HasContentT, IsSnapshotWrapper[HasContentT, ContentT]],
                       Protocol[HasContentT, ContentT]):
    """Container protocol managing snapshots used for deepcopy/reactive tracking."""

    def clear(self) -> None:
        """Clear.
        """
        ...

    def all_are_empty(self, debug: bool = False) -> bool:
        """All are empty.
        
        Args:
            debug: (bool) Argument passed to ``all_are_empty()``.
        
        Returns:
            bool: Result produced by ``all_are_empty()``.
        """
        ...

    def get_deepcopy_content_ids(self) -> SetDeque[int]:
        """Get deepcopy content ids.
        
        Returns:
            SetDeque[int]: Result produced by ``get_deepcopy_content_ids()``.
        """
        ...

    def get_deepcopy_content_ids_scheduled_for_deletion(self) -> SetDeque[int]:
        """Get deepcopy content ids scheduled for deletion.
        
        Returns:
            SetDeque[int]: Result produced by ``get_deepcopy_content_ids_scheduled_for_deletion()``.
        """
        ...

    def schedule_deepcopy_content_ids_for_deletion(self, *keys: int) -> None:
        """Schedule deepcopy content ids for deletion.
        
        Args:
            keys: (int) Argument passed to ``schedule_deepcopy_content_ids_for_deletion()``.
        """
        ...

    def delete_scheduled_deepcopy_content_ids(self) -> None:
        """Delete scheduled deepcopy content ids.
        """
        ...

    def take_snapshot_setup(self) -> None:
        """Take snapshot setup.
        """
        ...

    def take_snapshot_teardown(self) -> None:
        """Take snapshot teardown.
        """
        ...

    def take_snapshot(self, obj: HasContentT) -> None:
        """Take snapshot.
        
        Args:
            obj: (HasContentT) Argument passed to ``take_snapshot()``.
        """
        ...


class AvailableDisplayDims(TypedDict):
    """Display-space dimensions available for rendering, in pixels."""

    width: pyd.NonNegativeInt | None
    height: pyd.NonNegativeInt | None


@runtime_checkable
class IsReactive(Protocol[ContentT]):
    """Mutable reactive value wrapper used for config/state propagation."""

    @property
    def value(self) -> ContentT:
        """Value.
        
        Returns:
            ContentT: Result produced by ``value()``.
        """
        ...

    def set(self, value: ContentT):
        """Set.
        
        Args:
            value: (ContentT) Argument passed to ``set()``.
        """
        ...


@runtime_checkable
class IsReactiveObjects(Protocol):
    """Bundle of reactive objects shared by display and configuration layers."""

    jupyter_ui_config: IsReactive[IsJupyterUserInterfaceConfig]
    text_config: IsReactive[IsTextConfig]
    layout_config: IsReactive[IsLayoutConfig]
    available_display_dims_in_px: IsReactive[AvailableDisplayDims]
    obj_id_update_flags: IsReactive[dict[int, bool]]

    def __eq__(self, other) -> bool:
        ...


@runtime_checkable
class IsDataClassCreator(Protocol[HasContentT, ContentT]):
    """Factory/service protocol that wires config, reactive state, and snapshots."""

    @property
    def config(self) -> IsDataConfig:
        """{{ISDATACLASSCREATOR_CONFIG_SUMMARY}}

        {{ISDATACLASSCREATOR_CONFIG_DETAILS}}"""
        ...

    def set_config(self, config: IsDataConfig) -> None:
        """{{ISDATACLASSCREATOR_SET_CONFIG_SUMMARY}}

        {{ISDATACLASSCREATOR_SET_CONFIG_DETAILS}}"""
        ...

    @property
    def reactive_objects(self) -> IsReactiveObjects | None:
        """Reactive objects.
        
        Returns:
            IsReactiveObjects | None: Result produced by ``reactive_objects()``.
        """
        ...

    def set_reactive_objects(self, reactive_objects: IsReactiveObjects) -> None:
        """Set reactive objects.
        
        Args:
            reactive_objects: (IsReactiveObjects) Argument passed to ``set_reactive_objects()``.
        """
        ...

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[HasContentT, ContentT]:
        """Snapshot holder.
        
        Returns:
            IsSnapshotHolder[HasContentT, ContentT]: Result produced by ``snapshot_holder()``.
        """
        ...

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        """Deepcopy context.
        
        Args:
            top_level_entry_func: (Callable[[], None]) Argument passed to ``deepcopy_context()``.
            top_level_exit_func: (Callable[[], None]) Argument passed to ``deepcopy_context()``.
        
        Returns:
            ContextManager[int]: Result produced by ``deepcopy_context()``.
        """
        ...
