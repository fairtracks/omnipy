from typing import Any, Dict, IO, Type

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.serializer import TarFileSerializer


class RawDatasetToTarFileSerializer(TarFileSerializer):
    @classmethod
    def get_supported_dataset_type(cls) -> Type[Dataset]:
        return Dataset[Model[str]]

    @classmethod
    def serialize(cls, dataset: Dataset[Model[str]]) -> bytes:
        def raw_encode_func(contents: str) -> bytes:
            return contents.encode('utf8')

        return cls.create_tarfile_from_dataset(
            dataset, file_suffix='raw', data_encode_func=raw_encode_func)

    @classmethod
    def deserialize(cls, tarfile_bytes: bytes) -> Dataset[Model[str]]:
        dataset = Dataset[Model[str]]()

        def raw_decode_func(file_stream: IO[bytes]) -> str:
            return file_stream.read().decode('utf8')

        def python_dictify_object(obj_type: str, obj_val: Any) -> Dict:
            return {obj_type: obj_val}

        cls.create_dataset_from_tarfile(
            dataset,
            tarfile_bytes,
            file_suffix='raw',
            data_decode_func=raw_decode_func,
            dictify_object_func=python_dictify_object,
            import_method='from_data')  # noqa

        return dataset
