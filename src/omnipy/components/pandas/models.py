from collections.abc import Iterable
from io import StringIO
from typing import Any, TYPE_CHECKING

from typing_extensions import Self

from omnipy.data.model import Model
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.exceptions import ShouldNotOccurException

from ..tables.models import (TableDictOfDictsOfJsonScalarsModel,
                             TableDictOfListsOfJsonScalarsModel,
                             TableListOfDictsOfJsonScalarsModel,
                             TableListOfListsOfJsonScalarsModel)

if TYPE_CHECKING:
    from .lazy_import import pd

__all__ = ['PandasModel']

AnyJsonTableType = (
    TableListOfListsOfJsonScalarsModel | TableListOfDictsOfJsonScalarsModel
    | TableDictOfDictsOfJsonScalarsModel | TableDictOfListsOfJsonScalarsModel)


class PandasModel(Model['pd.DataFrame | pd.Series | AnyJsonTableType']):
    if TYPE_CHECKING:

        def __new__(cls, *args: Any, **kwargs: Any) -> 'PandasModel_DataFrame':
            ...

    else:

        def __new__(cls, *args: Any, **kwargs: Any) -> Self:
            from .lazy_import import pd

            cls.update_forward_refs(pd=pd, AnyJsonTableType=AnyJsonTableType)
            return super().__new__(cls, *args, **kwargs)

    @classmethod
    def _parse_data(
        cls,
        data: 'pd.DataFrame | pd.Series | AnyJsonTableType',
    ) -> 'pd.DataFrame | pd.Series':
        from .lazy_import import pd

        cls.update_forward_refs(pd=pd, AnyJsonTableType=AnyJsonTableType)

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
    def _from_iterable(cls, data: Iterable) -> 'pd.DataFrame':
        from .lazy_import import pd
        return pd.DataFrame(data.content if is_model_instance(data) else data).convert_dtypes()

    def to_data(self) -> Any:
        from .lazy_import import pd

        df = self.content.replace({pd.NA: None})
        if isinstance(df, pd.DataFrame):
            return df.to_dict(orient='records')
        elif isinstance(df, pd.Series):
            return df.to_dict()

    def from_data(self, data: Iterable) -> None:
        self._validate_and_set_value(self._from_iterable(data))

    def from_json(self, json_content: str) -> None:
        from .lazy_import import pd

        self._validate_and_set_value(pd.read_json(StringIO(json_content)).convert_dtypes())

    def to_json(self, pretty=True) -> str:
        from .lazy_import import pd

        if isinstance(self.content, pd.DataFrame):
            return self.content.to_json(orient='records')
        elif isinstance(self.content, pd.Series):
            return self.content.to_json()
        else:
            raise ShouldNotOccurException()


if TYPE_CHECKING:

    class PandasModel_DataFrame(PandasModel, pd.DataFrame):  # type: ignore[misc]
        ...
