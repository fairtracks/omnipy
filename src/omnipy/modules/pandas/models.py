import json
from typing import Any, Dict, Iterable, List

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model, ROOT_KEY

from . import pd


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

    def from_json(self, value: str) -> None:
        self.contents = self._convert_ints_to_nullable_ints(pd.read_json(value))

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


class ListOfPandasDatasetsWithSameNumberOfFiles(Model[List[PandasDataset]]):
    @classmethod
    def _parse_data(cls, dataset_list: List[PandasDataset]) -> Any:
        assert len(dataset_list) >= 2
        assert all(len(dataset) for dataset in dataset_list)
