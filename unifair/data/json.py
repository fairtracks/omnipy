import json

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
