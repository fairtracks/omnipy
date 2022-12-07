from typing import Any, Dict, IO

from unifair.data.dataset import Dataset
from unifair.data.model import Model
from unifair.data.serializer import create_dataset_from_tarfile, create_tarfile_from_dataset


class RawDatasetToTarFileSerializer:
    @staticmethod
    def serialize(dataset: Dataset[Model[str]]) -> bytes:
        def raw_encode_func(contents: str) -> bytes:
            return contents.encode('utf8')

        return create_tarfile_from_dataset(
            dataset, file_suffix='raw', data_encode_func=raw_encode_func)

    @staticmethod
    def deserialize(tarfile_bytes: bytes) -> Dataset[Model[str]]:
        dataset = Dataset[Model[str]]()

        def raw_decode_func(file_stream: IO[bytes]) -> str:
            return file_stream.read().decode('utf8')

        def python_dictify_object(obj_type: str, obj_val: Any) -> Dict:
            return {obj_type: obj_val}

        create_dataset_from_tarfile(
            dataset,
            tarfile_bytes,
            file_suffix='raw',
            data_decode_func=raw_decode_func,
            dictify_object_func=python_dictify_object,
            import_method='from_data')  # noqa

        return dataset
