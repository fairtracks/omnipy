import json

from collections import UserDict
from pydantic import BaseModel


class JsonDataset(UserDict):
    # def __init__(self):
    #     # super(BaseModel, self).__init__()
    #     super(UserDict, self).__init__()

    def __setitem__(self, key: str, json_str: str) -> None:
        self.data[key] = json.loads(json_str)

