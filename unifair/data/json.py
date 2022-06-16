import json
from typing import Dict, IO, List, Union

from pydantic import validator

from unifair.data import (create_dataset_from_tarfile,
                          create_tarfile_from_dataset,
                          Dataset,
                          validate)


class JsonDataset(Dataset):
    data: Dict[str, List[Dict[str, Union[str, int, float, List, Dict]]]]

    def __setitem__(self, obj_type: str, data_obj: str) -> None:
        self.data[obj_type] = json.loads(data_obj)
        validate(self)

    @validator('data')
    def validate_data(cls, data):
        cls._data_not_empty_object(data)

    @staticmethod
    def _data_not_empty_object(data):
        for obj_list in data.values():
            for obj in obj_list:
                assert len(obj) > 0


class JsonDatasetToTarFileSerializer:
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

        create_dataset_from_tarfile(
            json_dataset,
            tarfile_bytes,
            file_suffix='json',
            data_decode_func=json_decode_func,
        )

        return json_dataset
