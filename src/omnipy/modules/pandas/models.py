from collections.abc import Iterable
from io import StringIO
from typing import Any, TYPE_CHECKING, TypeAlias

from omnipy.data.dataset import Dataset
from omnipy.data.helpers import is_model_instance
from omnipy.data.model import Model

from . import pd
from ..tables.models import TableListOfDictsOfJsonScalarsModel


class _PandasModel(Model[pd.DataFrame | pd.Series | TableListOfDictsOfJsonScalarsModel]):
    @classmethod
    def _parse_data(
        cls, data: pd.DataFrame | pd.Series | TableListOfDictsOfJsonScalarsModel
    ) -> pd.DataFrame | pd.Series:
        if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
            return data

        return cls._from_iterable(data)

    # @staticmethod
    # def _data_column_names_are_strings(data: pd.DataFrame) -> None:
    #     for column in data.columns:
    #         assert isinstance(column, str)

    # @staticmethod
    # def _data_not_empty_object(data: pd.DataFrame) -> None:
    #     assert not any(data.isna().all(axis=1))
    #

    @classmethod
    def _from_iterable(cls, data: Iterable) -> pd.DataFrame:
        return pd.DataFrame(data.contents if is_model_instance(data) else data).convert_dtypes()

    def to_data(self) -> Any:
        df = self.contents.replace({pd.NA: None})
        if isinstance(df, pd.DataFrame):
            return df.to_dict(orient='records')
        elif isinstance(df, pd.Series):
            return df.to_dict()

    def from_data(self, value: Iterable) -> None:
        self._validate_and_set_value(self._from_iterable(value))

    def from_json(self, value: str) -> None:
        self._validate_and_set_value(pd.read_json(StringIO(value)).convert_dtypes())


if TYPE_CHECKING:

    class PandasModel(_PandasModel):
        def __new__(
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> 'PandasDataFrameModel':
            ...

    class PandasDataFrameModel(PandasModel, pd.DataFrame):
        ...
else:

    PandasModel: TypeAlias = _PandasModel


class PandasDataset(Dataset[PandasModel]):
    ...


class ListOfPandasDatasetsWithSameNumberOfFiles(Model[list[PandasDataset]]):
    @classmethod
    def _parse_data(cls, dataset_list: list[PandasDataset]) -> Any:
        assert len(dataset_list) >= 2
        assert all(len(dataset) for dataset in dataset_list)
