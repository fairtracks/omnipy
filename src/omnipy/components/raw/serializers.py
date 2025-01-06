from typing import Any, IO, Type

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import TarFileSerializer
from omnipy.shared.protocols.data import IsDataset
from omnipy.util.helpers import all_type_variants


class RawStrDatasetToTarFileSerializer(TarFileSerializer):
    """"""
    @classmethod
    def is_dataset_directly_supported(cls, dataset: IsDataset) -> bool:
        model_type_variants = all_type_variants(dataset.get_model_class().full_type())
        return len(model_type_variants) > 0 and model_type_variants[0] is str

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
        model_type_variants = all_type_variants(dataset.get_model_class().full_type())
        return len(model_type_variants) > 0 and model_type_variants[0] is bytes

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
