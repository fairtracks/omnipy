import json
import tarfile

from io import BytesIO
from tarfile import TarInfo
from typing import Dict, List, Union
from collections import UserDict
from pydantic import BaseModel, validator

from unifair.data.common import validate


class JsonDataset(UserDict, BaseModel):
    data: Dict[str, List[Dict[str, Union[str, int, float, List, Dict]]]]

    def __init__(self):
        BaseModel.__init__(self, data={})
        UserDict.__init__(self, {})

    def __setitem__(self, key: str, json_str: str) -> None:
        self.data[key] = json.loads(json_str)
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
        bytes_io = BytesIO()

        with tarfile.open(fileobj=bytes_io, mode='w:gz') as tf:
            for obj_type, json_data in json_dataset.items():
                json_data_bytestream = BytesIO(json.dumps(json_data).encode('utf8'))
                json_data_bytestream.seek(0)
                ti = TarInfo(name=f'{obj_type}.json')
                ti.size = len(json_data_bytestream.getbuffer())
                tf.addfile(ti, json_data_bytestream)

        return bytes_io.getbuffer().tobytes()

    @staticmethod
    def deserialize(tarfile_bytes: bytes) -> JsonDataset:
        json_dataset = JsonDataset()

        with tarfile.open(fileobj=BytesIO(tarfile_bytes), mode='r:gz') as tf:
            for filename in tf.getnames():
                json_file = tf.extractfile(filename)
                assert filename.endswith(".json")
                obj_type = filename[:-5]
                json_dataset[obj_type] = json_file.read().decode('utf8')

        return json_dataset
