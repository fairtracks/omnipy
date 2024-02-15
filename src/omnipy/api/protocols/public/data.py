from typing import Any, Callable, IO, Iterator, Protocol, Type, TypeVar

from pydantic.fields import Undefined, UndefinedType

from omnipy.api.protocols.private.log import CanLog

_ModelT = TypeVar('_ModelT')


class IsDataset(Protocol[_ModelT]):
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
    def get_model_class(cls) -> Type[_ModelT]:
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

    def as_multi_model_dataset(self) -> 'MultiModelDataset[_ModelT]':
        ...


class MultiModelDataset(Protocol[_ModelT]):
    """
        Variant of Dataset that allows custom models to be set on individual data files
    """
    def set_model(self, data_file: str, model: _ModelT) -> None:
        ...

    def get_model(self, data_file: str) -> _ModelT:
        ...


class IsSerializer(Protocol):
    """"""
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        pass

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        pass

    @classmethod
    def get_output_file_suffix(cls) -> str:
        pass

    @classmethod
    def serialize(cls, dataset: IsDataset) -> bytes | memoryview:
        pass

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> IsDataset:
        pass


class IsTarFileSerializer(IsSerializer):
    @classmethod
    def create_tarfile_from_dataset(cls,
                                    dataset: IsDataset,
                                    data_encode_func: Callable[[Any], bytes | memoryview]):
        """"""

    @classmethod
    def create_dataset_from_tarfile(cls,
                                    dataset: IsDataset,
                                    tarfile_bytes: bytes,
                                    data_decode_func: Callable[[IO[bytes]], Any],
                                    dictify_object_func: Callable[[str, Any], dict | str],
                                    import_method='from_data',
                                    any_file_suffix: bool = False):
        ...


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

    def auto_detect(self, dataset: IsDataset):
        ...

    def auto_detect_tar_file_serializer(self, dataset: IsDataset):
        ...

    @classmethod
    def _autodetect_serializer(cls, dataset, serializers):
        ...

    def detect_tar_file_serializers_from_dataset_cls(self, dataset: IsDataset):
        ...

    def detect_tar_file_serializers_from_file_suffix(self, file_suffix: str):
        ...

    def load_from_tar_file_path_based_on_file_suffix(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset):
        ...

    def load_from_tar_file_path_based_on_dataset_cls(self,
                                                     log_obj: CanLog,
                                                     tar_file_path: str,
                                                     to_dataset: IsDataset):
        ...
