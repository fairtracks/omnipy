from typing import Generic, TypeVar

from pydantic import BaseModel

from omnipy.data.dataset import Dataset

from .models import (TableDictOfDictsOfJsonScalarsModel,
                     TableDictOfListsOfJsonScalarsModel,
                     TableListOfDictsOfJsonScalarsModel,
                     TableListOfListsOfJsonScalarsModel,
                     TableOfPydanticRecordsModel,
                     TableWithColNamesModel)


class TableListOfListsOfJsonScalarsDataset(Dataset[TableListOfListsOfJsonScalarsModel]):
    ...


class TableListOfDictsOfJsonScalarsDataset(Dataset[TableListOfDictsOfJsonScalarsModel]):
    ...


class TableDictOfDictsOfJsonScalarsDataset(Dataset[TableDictOfDictsOfJsonScalarsModel]):
    ...


class TableDictOfListsOfJsonScalarsDataset(Dataset[TableDictOfListsOfJsonScalarsModel]):
    ...


class TableWithColNamesDataset(Dataset[TableWithColNamesModel]):
    @property
    def col_names(self) -> tuple[str]:
        col_names = {}
        for data_file in self.values():
            col_names.update(dict.fromkeys(data_file.col_names))
        return tuple(col_names.keys())


_PydanticModelT = TypeVar('_PydanticModelT', bound=BaseModel)


class TableOfPydanticRecordsDataset(Dataset[TableOfPydanticRecordsModel[_PydanticModelT]],
                                    Generic[_PydanticModelT]):
    ...
