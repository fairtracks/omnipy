from io import BytesIO
from typing import Any, Dict, IO, Iterable, Union

import pandas as pd

from unifair.dataset.dataset import Dataset
from unifair.dataset.model import Model, ROOT_KEY
from unifair.dataset.serializer import (create_dataset_from_tarfile, create_tarfile_from_dataset)


class PandasModel(Model[pd.DataFrame]):
    @classmethod
    def _parse_data(cls, data: pd.DataFrame) -> pd.DataFrame:
        cls._data_column_names_are_strings(data)
        cls._data_not_empty_object(data)
        return data

    @staticmethod
    def _data_column_names_are_strings(data: pd.DataFrame) -> None:
        for column in data.columns:
            assert isinstance(column, str)

    @staticmethod
    def _data_not_empty_object(data: pd.DataFrame) -> None:
        assert not any(data.isna().all(axis=1))

    def dict(self, *args, **kwargs) -> Dict[Any, Any]:
        return super().dict(*args, **kwargs)[ROOT_KEY].to_dict(orient='records')  # noqa

    def from_data(self, value: Iterable[Any]) -> None:
        self.contents = self._convert_ints_to_nullable_ints(pd.DataFrame(value))

    @classmethod
    def _convert_ints_to_nullable_ints(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        for key, col in dataframe.items():
            if col.dtype == 'int64' or (col.dtype == 'float64' and col.isna().any()):
                try:
                    dataframe[key] = col.astype(float).astype('Int64')
                except TypeError:
                    pass
        return dataframe


class PandasDataset(Dataset[PandasModel]):
    ...


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
