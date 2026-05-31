"""Tar-file serializers for raw string and bytes datasets."""

from typing import Any, cast, IO, Type

from omnipy.data._typing.helpers import all_dataset_type_variants
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import TarFileSerializer
from omnipy.shared.protocols.data import IsDataset

from .datasets import StrictBytesDataset, StrictStrDataset


class RawStrDatasetToTarFileSerializer(TarFileSerializer[StrictStrDataset]):
    """Serialize raw string datasets to and from gzipped tar archives."""

    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        """Return whether a dataset stores raw strings."""

        type_variants = all_dataset_type_variants(dataset)
        return len(type_variants) > 0 and type_variants[0] is str

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        """{{SERIALIZER_GET_DATASET_CLS_FOR_NEW_SUMMARY}}"""

        return StrictStrDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        """{{SERIALIZER_GET_OUTPUT_FILE_SUFFIX_SUMMARY}}"""

        return 'txt'

    @classmethod
    def serialize(cls, dataset: StrictStrDataset) -> bytes | memoryview:
        """{{SERIALIZE_GZIPPED_TAR_SUMMARY}}"""

        def raw_encode_func(content: str) -> bytes:
            return content.encode('utf8')

        return cls.create_tarfile_from_dataset(dataset, data_encode_func=raw_encode_func)

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> StrictStrDataset:
        """{{DESERIALIZE_GZIPPED_TAR_SUMMARY}}"""

        dataset = StrictStrDataset()

        def raw_decode_func(file_stream: IO[bytes]) -> str:
            return file_stream.read().decode('utf8')

        def python_dictify_object(data_file: str, obj_val: Any) -> dict:
            return {data_file: obj_val}

        cls.create_dataset_from_tarfile(
            dataset,
            serialized,
            data_decode_func=raw_decode_func,
            dictify_object_func=python_dictify_object,
            import_method='from_data',
            any_file_suffix=any_file_suffix,
        )  # noqa

        return dataset


class RawBytesDatasetToTarFileSerializer(TarFileSerializer[StrictBytesDataset]):
    """Serialize raw bytes datasets to and from gzipped tar archives."""

    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        """Return whether a dataset stores raw bytes."""

        type_variants = all_dataset_type_variants(dataset)
        return len(type_variants) > 0 and type_variants[0] is bytes

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        """{{SERIALIZER_GET_DATASET_CLS_FOR_NEW_SUMMARY}}"""

        return StrictBytesDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        """{{SERIALIZER_GET_OUTPUT_FILE_SUFFIX_SUMMARY}}"""

        return 'bytes'

    @classmethod
    def serialize(cls, dataset: StrictBytesDataset) -> bytes | memoryview:
        """{{SERIALIZE_GZIPPED_TAR_SUMMARY}}"""

        def raw_encode_func(content: bytes) -> bytes:
            return content

        return cls.create_tarfile_from_dataset(dataset, data_encode_func=raw_encode_func)

    @classmethod
    def deserialize(cls, serialized: bytes, any_file_suffix=False) -> StrictBytesDataset:
        """{{DESERIALIZE_GZIPPED_TAR_SUMMARY}}"""

        dataset = cast(StrictBytesDataset, Dataset[Model[bytes]]())

        def raw_decode_func(file_stream: IO[bytes]) -> bytes:
            return file_stream.read()

        def python_dictify_object(data_file: str, obj_val: Any) -> dict:
            return {data_file: obj_val}

        cls.create_dataset_from_tarfile(
            dataset,
            serialized,
            data_decode_func=raw_decode_func,
            dictify_object_func=python_dictify_object,
            import_method='from_data',
            any_file_suffix=any_file_suffix,
        )  # noqa

        return dataset
