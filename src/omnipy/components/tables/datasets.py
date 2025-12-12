from typing import Generic, TypeVar

from omnipy.data.dataset import Dataset
import omnipy.util._pydantic as pyd

from .models import (ColumnWiseTableDictOfDictsModel,
                     ColumnWiseTableDictOfListsModel,
                     CsvTableModel,
                     RowWiseTableFirstRowAsColNamesModel,
                     RowWiseTableListOfDictsModel,
                     RowWiseTableListOfListsModel,
                     TableOfPydanticRecordsModel,
                     TsvTableModel)


class TableListOfListsOfJsonScalarsDataset(Dataset[RowWiseTableListOfListsModel]):
    ...


class TableListOfDictsOfJsonScalarsDataset(Dataset[RowWiseTableListOfDictsModel]):
    ...


class TableDictOfDictsOfJsonScalarsDataset(Dataset[ColumnWiseTableDictOfDictsModel]):
    ...


class TableDictOfListsOfJsonScalarsDataset(Dataset[ColumnWiseTableDictOfListsModel]):
    ...


class TableWithColNamesDataset(Dataset[RowWiseTableFirstRowAsColNamesModel]):
    @property
    def col_names(self) -> tuple[str]:
        col_names = {}
        for data_file in self.values():
            col_names.update(dict.fromkeys(data_file.col_names))
        return tuple(col_names.keys())


_PydanticModelT = TypeVar('_PydanticModelT', bound=pyd.BaseModel)


class TableOfPydanticRecordsDataset(Dataset[TableOfPydanticRecordsModel[_PydanticModelT]],
                                    Generic[_PydanticModelT]):
    ...


class TsvTableDataset(Dataset[TsvTableModel]):
    ...


class CsvTableDataset(Dataset[CsvTableModel]):
    ...
