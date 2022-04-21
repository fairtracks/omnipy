import pandas as pd
from collections import UserDict
from pydantic import BaseModel, validator
from typing import Dict
from unifair.data.common import validate


class PandasDataset(UserDict, BaseModel):
    data: Dict[str, pd.DataFrame] = {}

    class Config:
        arbitrary_types_allowed = True

    def __init__(self):
        BaseModel.__init__(self)
        UserDict.__init__(self)

    def __setitem__(self, key: str, data: str) -> None:
        self.data[key] = pd.DataFrame(data)
        validate(self)

    @validator('data')
    def validate_data(cls, data):
        cls._data_column_names_are_strings(data)
        cls._data_not_empty_object(data)

    @staticmethod
    def _data_column_names_are_strings(data):
        for obj_type_df in data.values():
            for column in obj_type_df.columns:
                assert isinstance(column, str)

    @staticmethod
    def _data_not_empty_object(data):
        for obj_type_df in data.values():
            assert not any(obj_type_df.isna().all(axis=1))


