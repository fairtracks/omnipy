import json
from typing import IO, Union

from unifair.data.serializer import (create_dataset_from_tarfile,
                                     create_tarfile_from_dataset,
                                     Serializer)

from .models import JsonDataset


class JsonDatasetToTarFileSerializer(Serializer):
    @staticmethod
    def serialize(json_dataset: JsonDataset) -> Union[bytes, memoryview]:
        def json_encode_func(json_data: list) -> bytes:
            return json.dumps(json_data).encode('utf8')

        return create_tarfile_from_dataset(
            json_dataset, file_suffix='json', data_encode_func=json_encode_func)

    @staticmethod
    def deserialize(tarfile_bytes: bytes) -> JsonDataset:
        json_dataset = JsonDataset()

        def json_decode_func(file_stream: IO[bytes]) -> str:
            return file_stream.read().decode('utf8')

        def json_dictify_object(obj_type: str, obj_val: str) -> str:
            return '{{"{}": {}}}'.format(obj_type, obj_val)

        create_dataset_from_tarfile(
            json_dataset,
            tarfile_bytes,
            file_suffix='json',
            data_decode_func=json_decode_func,
            dictify_object_func=json_dictify_object,
            import_method='from_json')

        return json_dataset