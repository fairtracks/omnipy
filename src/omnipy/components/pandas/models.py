from collections.abc import Iterable
from io import StringIO
from typing import Any, TYPE_CHECKING

from omnipy.data.helpers import is_model_instance
from omnipy.data.model import Model

from . import pd
from ..tables.models import (TableDictOfDictsOfJsonScalarsModel,
                             TableDictOfListsOfJsonScalarsModel,
                             TableListOfDictsOfJsonScalarsModel,
                             TableListOfListsOfJsonScalarsModel)

__all__ = ['PandasModel']


class PandasModel(Model[pd.DataFrame | pd.Series | TableListOfListsOfJsonScalarsModel
                        | TableListOfDictsOfJsonScalarsModel | TableDictOfDictsOfJsonScalarsModel
                        | TableDictOfListsOfJsonScalarsModel]):
    if TYPE_CHECKING:

        def __new__(cls, *args: Any, **kwargs: Any) -> 'PandasModel_DataFrame':
            ...

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

    def from_data(self, data: Iterable) -> None:
        self._validate_and_set_value(self._from_iterable(data))

    def from_json(self, json_contents: str) -> None:
        self._validate_and_set_value(pd.read_json(StringIO(json_contents)).convert_dtypes())


if TYPE_CHECKING:

    class PandasModel_DataFrame(PandasModel, pd.DataFrame):
        ...
