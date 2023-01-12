from typing import Dict, IO, Type, Union

from omnipy.data.serializer import TarFileSerializer

from ...data.dataset import Dataset
from .models import JsonDataset, JsonModel


class JsonDatasetToTarFileSerializer(TarFileSerializer):
    @classmethod
    def get_supported_dataset_type(cls) -> Type[Dataset]:
        return JsonDataset

    @classmethod
    def get_output_file_suffix(cls) -> str:
        return 'json'

    @classmethod
    def serialize(cls, json_dataset: JsonDataset) -> Union[bytes, memoryview]:
        def json_encode_func(json_data: JsonModel) -> bytes:
            return json_data.json(indent=2).encode('utf8')

        return cls.create_tarfile_from_dataset(json_dataset, data_encode_func=json_encode_func)

    @classmethod
    def deserialize(cls, tarfile_bytes: bytes) -> JsonDataset:
        json_dataset = JsonDataset()

        def json_decode_func(file_stream: IO[bytes]) -> str:
            return file_stream.read().decode('utf8')

        def json_dictify_object(obj_type: str, obj_val: str) -> Dict[str, str]:
            return {f'{obj_type}': f'{obj_val}'}

        cls.create_dataset_from_tarfile(
            json_dataset,
            tarfile_bytes,
            data_decode_func=json_decode_func,
            dictify_object_func=json_dictify_object,
            import_method='from_json')

        return json_dataset
