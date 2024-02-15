from typing import Any, IO, Type

from omnipy.api.protocols.public.data import IsDataset
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import TarFileSerializer


class RawStrDatasetToTarFileSerializer(TarFileSerializer):
    """"""
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        return type(dataset) is Dataset[Model[str]]

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        return Dataset[Model[str]]

    @classmethod
    def get_output_file_suffix(cls) -> str:
        return 'txt'

    @classmethod
    def serialize(cls, dataset: Dataset[Model[str]]) -> bytes | memoryview:
        def raw_encode_func(contents: str) -> bytes:
            return contents.encode('utf8')

        return cls.create_tarfile_from_dataset(dataset, data_encode_func=raw_encode_func)

    @classmethod
    def deserialize(cls, tarfile_bytes: bytes, any_file_suffix=False) -> Dataset[Model[str]]:
        dataset = Dataset[Model[str]]()

        def raw_decode_func(file_stream: IO[bytes]) -> str:
            return file_stream.read().decode('utf8')

        def python_dictify_object(data_file: str, obj_val: Any) -> dict:
            return {data_file: obj_val}

        cls.create_dataset_from_tarfile(
            dataset,
            tarfile_bytes,
            data_decode_func=raw_decode_func,
            dictify_object_func=python_dictify_object,
            import_method='from_data',
            any_file_suffix=any_file_suffix,
        )  # noqa

        return dataset


class RawBytesDatasetToTarFileSerializer(TarFileSerializer):
    """"""
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        return type(dataset) is Dataset[Model[bytes]]

    @classmethod
    def get_dataset_cls_for_new(cls) -> Type[IsDataset]:
        return Dataset[Model[bytes]]

    @classmethod
    def get_output_file_suffix(cls) -> str:
        return 'bytes'

    @classmethod
    def serialize(cls, dataset: Dataset[Model[bytes]]) -> bytes | memoryview:
        def raw_encode_func(contents: bytes) -> bytes:
            return contents

        return cls.create_tarfile_from_dataset(dataset, data_encode_func=raw_encode_func)

    @classmethod
    def deserialize(cls, tarfile_bytes: bytes, any_file_suffix=False) -> Dataset[Model[bytes]]:
        dataset = Dataset[Model[bytes]]()

        def raw_decode_func(file_stream: IO[bytes]) -> bytes:
            return file_stream.read()

        def python_dictify_object(data_file: str, obj_val: Any) -> dict:
            return {data_file: obj_val}

        cls.create_dataset_from_tarfile(
            dataset,
            tarfile_bytes,
            data_decode_func=raw_decode_func,
            dictify_object_func=python_dictify_object,
            import_method='from_data',
            any_file_suffix=any_file_suffix,
        )  # noqa

        return dataset
