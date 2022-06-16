from io import BytesIO
from typing import Dict, IO, Union

import pandas as pd
from pydantic import validator

from unifair.dataset import (create_dataset_from_tarfile,
                             create_tarfile_from_dataset,
                             Dataset,
                             validate)


class PandasDataset(Dataset):
    data: Dict[str, pd.DataFrame] = {}

    class Config:
        arbitrary_types_allowed = True

    def __setitem__(self, obj_type: str, data_obj: list) -> None:
        self.data[obj_type] = self._convert_ints_to_nullable_ints(pd.DataFrame(data_obj))
        validate(self)

    @staticmethod
    def _convert_ints_to_nullable_ints(dataframe: pd.DataFrame) -> pd.DataFrame:
        for key, col in dataframe.items():
            if col.dtype == 'int64' or (col.dtype == 'float64' and col.isna().any()):
                try:
                    dataframe[key] = col.astype(float).astype('Int64')
                except TypeError:
                    pass
        return dataframe

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


class PandasDatasetToTarFileSerializer:
    @staticmethod
    def serialize(pandas_dataset: PandasDataset) -> Union[bytes, memoryview]:
        def pandas_encode_func(pandas_data: pd.DataFrame) -> memoryview:
            csv_bytes = BytesIO()
            pandas_data.to_csv(csv_bytes, encoding='utf8', mode='b')
            return csv_bytes.getbuffer()

        return create_tarfile_from_dataset(
            pandas_dataset, file_suffix='csv', data_encode_func=pandas_encode_func)

    @staticmethod
    def deserialize(tarfile_bytes: bytes) -> PandasDataset:
        pandas_dataset = PandasDataset()

        def csv_decode_func(file_stream: IO[bytes]) -> pd.DataFrame:
            return pd.read_csv(file_stream, index_col=0, encoding='utf8')

        create_dataset_from_tarfile(
            pandas_dataset,
            tarfile_bytes,
            file_suffix='csv',
            data_decode_func=csv_decode_func,
        )

        return pandas_dataset
