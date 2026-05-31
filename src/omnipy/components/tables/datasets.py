"""Datasets for grouped tabular data in row-wise, column-wise, CSV, TSV, and record forms."""

from typing import Generic, TypeVar

from omnipy.data.dataset import Dataset
import omnipy.util.pydantic as pyd

from .models import (ColumnWiseTableWithColNamesAndIndexModel,
                     CsvTableModel,
                     JsonScalarColumnWiseTableWithColNamesModel,
                     RowWiseTableFirstRowAsColNamesModel,
                     RowWiseTableModel,
                     RowWiseTableWithColNamesModel,
                     TableOfPydanticRecordsModel,
                     TsvTableModel)


class TableListOfListsOfJsonScalarsDataset(Dataset[RowWiseTableModel]):
    """Store row-wise tables whose rows are plain lists of JSON scalar values."""
    ...


class TableListOfDictsOfJsonScalarsDataset(Dataset[RowWiseTableWithColNamesModel]):
    """Store row-wise tables whose rows map column names to JSON scalar values."""
    ...


class TableDictOfDictsOfJsonScalarsDataset(Dataset[ColumnWiseTableWithColNamesAndIndexModel]):
    """Store indexed tables keyed by row identifier with column-name mappings per row."""
    ...


class TableDictOfListsOfJsonScalarsDataset(Dataset[JsonScalarColumnWiseTableWithColNamesModel]):
    ...


class TableWithColNamesDataset(Dataset[RowWiseTableFirstRowAsColNamesModel]):
    """Store row-wise tables whose first row defines the column names."""
    @property
    def col_names(self) -> tuple[str]:
        col_names = {}
        for data_file in self.values():
            col_names.update(dict.fromkeys(data_file.col_names))
        return tuple(col_names.keys())


_PydanticModelT = TypeVar('_PydanticModelT', bound=pyd.BaseModel)


class TableOfPydanticRecordsDataset(Dataset[TableOfPydanticRecordsModel[_PydanticModelT]],
                                    Generic[_PydanticModelT]):
    """Store tables parsed into lists of records validated by a Pydantic model."""
    ...


class TsvTableDataset(Dataset[TsvTableModel]):
    """Store TSV tables parsed into row-wise records with header-derived column names."""
    ...


class CsvTableDataset(Dataset[CsvTableModel]):
    """Store CSV tables parsed into row-wise records with header-derived column names."""
    ...
