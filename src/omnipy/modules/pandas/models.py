from collections.abc import Iterable
from typing import Any

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from . import pd


class PandasModel(Model[pd.DataFrame | pd.Series]):
    # @classmethod
    # def _parse_data(cls, data: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    #     # cls._data_column_names_are_strings(data)
    #     cls._data_not_empty_object(data)
    #     return data

    # @staticmethod
    # def _data_column_names_are_strings(data: pd.DataFrame) -> None:
    #     for column in data.columns:
    #         assert isinstance(column, str)

    # @staticmethod
    # def _data_not_empty_object(data: pd.DataFrame) -> None:
    #     assert not any(data.isna().all(axis=1))
    #

    def to_data(self) -> Any:
        df = self.contents.replace({pd.NA: None})
        if isinstance(df, pd.DataFrame):
            return df.to_dict(orient='records')
        elif isinstance(df, pd.Series):
            return df.to_dict()

    def from_data(self, value: Iterable[Any]) -> None:
        self._validate_and_set_contents(pd.DataFrame(value).convert_dtypes())

    def from_json(self, value: str) -> None:
        self._validate_and_set_contents(pd.read_json(value).convert_dtypes())


class PandasDataset(Dataset[PandasModel]):
    ...


class ListOfPandasDatasetsWithSameNumberOfFiles(Model[list[PandasDataset]]):
    @classmethod
    def _parse_data(cls, dataset_list: list[PandasDataset]) -> Any:
        assert len(dataset_list) >= 2
        assert all(len(dataset) for dataset in dataset_list)
