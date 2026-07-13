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
        """Return the wrapped content value.

        Returns:
            ContentT: Current content stored by the object.
        """
        ...

    @content.setter
    def content(self, value: ContentT) -> None:
        """Replace the wrapped content value.

        Args:
            value: New content to store.
        """
        ...


@runtime_checkable
class IsModel(HasContent[_RootT], Protocol[_RootT]):
    """Single-value data wrapper with typed content and conversion support."""
    @classmethod
    def full_type(cls) -> type[_RootT]:
        """Return the fully resolved Python type represented by this model.

        Returns:
            type[_RootT]: Concrete Python type accepted as model content.
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
        """Return the item type stored by this dataset class.

        Returns:
            type[_ModelOrDatasetT]: Model or nested-dataset type used for items.
        """
        ...

    def to_data(self) -> dict[str, Any]:
        """Convert the dataset to plain Python data.

        Returns:
            dict[str, Any]: Plain-data representation keyed by dataset entry name.
        """
        ...

    def from_data(self,
                  data: Mapping[str, Any] | Iterable[tuple[str, Any]],
                  update: bool = True) -> None:
        """Populate the dataset from plain Python data.

        Args:
            data: Plain-data mapping or iterable of key-value pairs to import.
            update: Whether imported values should merge into existing content.
        """
        ...

    def to_json(self, pretty=True) -> dict[str, str]:
        """Serialize the dataset to JSON strings.

        Args:
            pretty: Whether to format the JSON output for readability.

        Returns:
            dict[str, str]: JSON representation for each dataset entry.
        """
        ...

    def from_json(self,
                  data: Mapping[str, str] | Iterable[tuple[str, str]],
                  update: bool = True) -> None:
        """Populate the dataset from JSON-encoded entries.

        Args:
            data: JSON strings keyed by dataset entry name.
            update: Whether imported values should merge into existing content.
        """
        ...

    @classmethod
    def to_json_schema(cls, pretty=True) -> str | dict[str, str]:
        """Return the JSON schema for this dataset type.

        Args:
            pretty: Whether to format the schema output for readability.

        Returns:
            str | dict[str, str]: JSON schema as one string or per-entry mapping.
        """
        ...

    def save(self, path: str) -> None:
        """Persist the dataset to a filesystem path.

        Args:
            path: Destination path for the serialized dataset.
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
        """Load dataset content from one or more paths or URLs.

        Args:
            paths_or_urls: Source path, URL, or collection of sources to load.
            by_file_suffix: Whether serializer lookup should prefer file suffixes.
            as_mime_type: Explicit MIME type override, if any.
            kwargs: Additional named path or URL sources.

        Returns:
            Self | asyncio.Task[Self]: Loaded dataset or asynchronous load task.
        """
        ...

    def load_into(
        self,
        paths_or_urls: IsPathsOrUrlsOneOrMoreOrNone = None,
        by_file_suffix: bool = False,
        as_mime_type: None | str = None,
        **kwargs: IsPathOrUrl,
    ) -> Self | asyncio.Task[Self]:
        """Load external content into the current dataset instance.

        Args:
            paths_or_urls: Source path, URL, or collection of sources to load.
            by_file_suffix: Whether serializer lookup should prefer file suffixes.
            as_mime_type: Explicit MIME type override, if any.
            kwargs: Additional named path or URL sources.

        Returns:
            Self | asyncio.Task[Self]: Updated dataset or asynchronous load task.
        """
        ...

    @property
    def available_data(self) -> Self:
        """Return a view containing only successfully available entries.

        Returns:
            Self: Dataset containing entries whose content is already available.
        """
        ...

    @property
    def pending_data(self) -> Self:
        """Return a view containing entries that are still processing.

        Returns:
            Self: Dataset containing entries backed by pending work.
        """
        ...

    @property
    def failed_data(self) -> Self:
        """Return a view containing entries whose processing failed.

        Returns:
            Self: Dataset containing entries associated with failures.
        """
        ...

    def pending_task_details(self) -> dict[str, IsPendingData]:
        """Return metadata for entries that are still processing.

        Returns:
            dict[str, IsPendingData]: Pending metadata keyed by dataset entry name.
        """
        ...

    def failed_task_details(self) -> dict[str, IsFailedData]:
        """Return failure metadata for entries whose processing failed.

        Returns:
            dict[str, IsFailedData]: Failure metadata keyed by dataset entry name.
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
        """Assign a model class to one dataset entry.

        Args:
            data_file: Entry name whose model should be updated.
            model: Model class to associate with that entry.
        """
        ...

    def get_model(self, data_file: str) -> type[IsModel]:
        """Return the model class associated with one dataset entry.

        Args:
            data_file: Entry name whose model should be returned.

        Returns:
            type[IsModel]: Model class associated with that entry.
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
        """Return whether the serializer can handle the dataset as-is.

        Args:
            dataset: Dataset instance to check.

        Returns:
            bool: ``True`` when no dataset conversion is required before serialization.
        """
        ...

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        """Return the dataset class this serializer creates when deserializing.

        Returns:
            Type[IsDataset]: Dataset class produced for fresh deserialization targets.
        """
        ...

    @classmethod
    def get_output_file_suffix(cls) -> str:
        """Return the default file suffix produced by this serializer.

        Returns:
            str: File suffix used for serialized output files.
        """
        ...

    @classmethod
    def serialize(cls, dataset: _DatasetT) -> bytes | memoryview:
        """Serialize a dataset into a bytes-like payload.

        Args:
            dataset: Dataset instance to serialize.

        Returns:
            bytes | memoryview: Serialized dataset payload.
        """
        ...

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> _DatasetT:
        """Deserialize a bytes payload into a dataset instance.

        Args:
            serialized: Serialized dataset payload.
            any_file_suffix: Whether suffix validation should be relaxed.

        Returns:
            _DatasetT: Deserialized dataset instance.
        """
        ...


@runtime_checkable
class IsTarFileSerializer(IsSerializer[_DatasetT], Protocol[_DatasetT]):
    """Serializer extension that stores dataset entries inside tar archives."""
    @classmethod
    def create_tarfile_from_dataset(cls,
                                    dataset: _DatasetT,
                                    data_encode_func: Callable[..., bytes | memoryview]) -> bytes:
        """Create a tar archive payload from a dataset.

        Args:
            dataset: Dataset to archive.
            data_encode_func: Encoder used for individual dataset-entry payloads.

        Returns:
            bytes: Tar archive containing the serialized dataset entries.
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
        """Populate a dataset from a tar archive payload.

        Args:
            dataset: Dataset instance to populate.
            tarfile_bytes: Serialized tar archive payload.
            data_decode_func: Decoder used for individual archived payloads.
            dictify_object_func: Helper that converts decoded objects to importable values.
            import_method: Dataset import method to call for decoded entries.
            any_file_suffix: Whether suffix validation should be relaxed.
        """
        ...


@runtime_checkable
class IsSerializerRegistry(Protocol):
    """Registry that tracks serializers and selects suitable ones for datasets."""
    def __init__(self) -> None:
        ...

    def register(self, serializer_cls: Type[IsSerializer]) -> None:
        """Register a serializer class with the registry.

        Args:
            serializer_cls: Serializer class to add.
        """
        ...

    @property
    def serializers(self) -> tuple[Type[IsSerializer], ...]:
        """Return all registered serializer classes.

        Returns:
            tuple[Type[IsSerializer], ...]: Registered serializer classes.
        """
        ...

    @property
    def tar_file_serializers(self) -> tuple[Type[IsTarFileSerializer], ...]:
        """Return the registered tar-file serializer classes.

        Returns:
            tuple[Type[IsTarFileSerializer], ...]: Registered tar-file serializers.
        """
        ...

    def auto_detect(self, dataset: IsDataset) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        """Return the best serializer match for a dataset, if any.

        Args:
            dataset: Dataset to inspect.

        Returns:
            tuple[IsDataset, IsSerializer] | tuple[None, None]: Parsed dataset and
                serializer pair, or ``(None, None)`` when no match exists.
        """
        ...

    def auto_detect_tar_file_serializer(
            self, dataset: IsDataset) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        """Return the best tar-file serializer match for a dataset, if any.

        Args:
            dataset: Dataset to inspect.

        Returns:
            tuple[IsDataset, IsSerializer] | tuple[None, None]: Parsed dataset and
                tar-file serializer pair, or ``(None, None)`` when no match exists.
        """
        ...

    @classmethod
    def _autodetect_serializer(cls, dataset,
                               serializers) -> tuple[IsDataset, IsSerializer] | tuple[None, None]:
        ...

    def detect_tar_file_serializers_from_dataset_cls(
            self, dataset: IsDataset) -> tuple[Type[IsTarFileSerializer], ...]:
        """Return tar-file serializers compatible with the dataset class.

        Args:
            dataset: Dataset whose class should be inspected.

        Returns:
            tuple[Type[IsTarFileSerializer], ...]: Compatible tar-file serializer classes.
        """
        ...

    def detect_tar_file_serializers_from_file_suffix(
            self, file_suffix: str) -> tuple[Type[IsTarFileSerializer], ...]:
        """Return tar-file serializers matching a file suffix.

        Args:
            file_suffix: File suffix to match against registered serializers.

        Returns:
            tuple[Type[IsTarFileSerializer], ...]: Matching tar-file serializer classes.
        """
        ...

    def load_from_tar_file_path_based_on_file_suffix(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset) -> IsDataset | None:
        """Load a tar archive into a dataset using suffix-based detection.

        Args:
            log_obj: Logger used for progress and error reporting.
            tar_file_path: Path to the tar archive on disk.
            to_dataset: Dataset instance to populate.

        Returns:
            IsDataset | None: Populated dataset, or ``None`` when no serializer matches.
        """
        ...

    def load_from_tar_file_path_based_on_dataset_cls(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset) -> IsDataset | None:
        """Load a tar archive into a dataset using dataset-class detection.

        Args:
            log_obj: Logger used for progress and error reporting.
            tar_file_path: Path to the tar archive on disk.
            to_dataset: Dataset instance to populate.

        Returns:
            IsDataset | None: Populated dataset, or ``None`` when no serializer matches.
        """
        ...


@runtime_checkable
class IsSnapshotWrapper(Protocol[ObjContraT, ContentT]):
    """Snapshot record linking an object identity to captured content."""

    id: int
    snapshot: ContentT

    def taken_of_same_obj(self, obj: ObjContraT) -> bool:
        """Return whether the snapshot belongs to the given object.

        Args:
            obj: Object to compare with the captured snapshot owner.

        Returns:
            bool: ``True`` when the snapshot was taken from ``obj``.
        """
        ...

    def differs_from(self, obj: ObjContraT) -> bool:
        """Return whether the object's current content differs from the snapshot.

        Args:
            obj: Object whose current content should be compared.

        Returns:
            bool: ``True`` when the current content no longer matches the snapshot.
        """
        ...


@runtime_checkable
class IsSnapshotHolder(IsWeakKeyRefContainer[HasContentT, IsSnapshotWrapper[HasContentT, ContentT]],
                       Protocol[HasContentT, ContentT]):
    """Container protocol managing snapshots used for deepcopy/reactive tracking."""
    def clear(self) -> None:
        """Remove all tracked snapshots and bookkeeping state."""
        ...

    def all_are_empty(self, debug: bool = False) -> bool:
        """Return whether every tracked snapshot collection is empty.

        Args:
            debug: Whether extra diagnostics should be enabled during the check.

        Returns:
            bool: ``True`` when no tracked snapshot state remains.
        """
        ...

    def get_deepcopy_content_ids(self) -> SetDeque[int]:
        """Return tracked content ids participating in deepcopy bookkeeping.

        Returns:
            SetDeque[int]: Content ids currently tracked for deepcopy handling.
        """
        ...

    def get_deepcopy_content_ids_scheduled_for_deletion(self) -> SetDeque[int]:
        """Return tracked content ids waiting to be deleted.

        Returns:
            SetDeque[int]: Content ids marked for later deletion.
        """
        ...

    def schedule_deepcopy_content_ids_for_deletion(self, *keys: int) -> None:
        """Mark tracked content ids for later deletion.

        Args:
            keys: Content ids to queue for deletion.
        """
        ...

    def delete_scheduled_deepcopy_content_ids(self) -> None:
        """Delete every content id previously scheduled for removal."""
        ...

    def take_snapshot_setup(self) -> None:
        """Prepare internal state before taking one or more snapshots."""
        ...

    def take_snapshot_teardown(self) -> None:
        """Finalize snapshot bookkeeping after snapshot capture completes."""
        ...

    def take_snapshot(self, obj: HasContentT) -> None:
        """Capture a snapshot of the given object's current content.

        Args:
            obj: Object whose content should be snapshotted.
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
        """Return the current reactive value.

        Returns:
            ContentT: Current value stored by the reactive wrapper.
        """
        ...

    def set(self, value: ContentT):
        """Replace the current reactive value.

        Args:
            value: New value to publish.
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
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISDATACLASSCREATOR_CONFIG_SUMMARY}}
        #
        # {{ISDATACLASSCREATOR_CONFIG_DETAILS}}
        """Return the data configuration shared by the owning data-class family.

        Returns:
            IsDataConfig: Shared configuration object used by related models and datasets.
        """
        ...

    def set_config(self, config: IsDataConfig) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISDATACLASSCREATOR_SET_CONFIG_SUMMARY}}
        #
        # {{ISDATACLASSCREATOR_SET_CONFIG_DETAILS}}
        """Replace the shared data configuration for the owning data-class family.

        Args:
            config: Data configuration object to store for related models and datasets.
        """
        ...

    @property
    def reactive_objects(self) -> IsReactiveObjects | None:
        """Return the shared bundle of reactive runtime objects, if configured.

        Returns:
            IsReactiveObjects | None: Shared reactive-object bundle, or ``None``.
        """
        ...

    def set_reactive_objects(self, reactive_objects: IsReactiveObjects) -> None:
        """Store the shared bundle of reactive runtime objects.

        Args:
            reactive_objects: Reactive-object bundle to share with related data classes.
        """
        ...

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[HasContentT, ContentT]:
        """Return the snapshot manager used for deepcopy and reactive tracking.

        Returns:
            IsSnapshotHolder[HasContentT, ContentT]: Snapshot manager for related objects.
        """
        ...

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        """Return a context manager for coordinated deepcopy bookkeeping.

        Args:
            top_level_entry_func: Callback invoked when entering the outermost deepcopy.
            top_level_exit_func: Callback invoked when leaving the outermost deepcopy.

        Returns:
            ContextManager[int]: Context manager tracking nested deepcopy depth.
        """
        ...
