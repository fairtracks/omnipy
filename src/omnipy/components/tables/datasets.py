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
    """Store row-wise tables represented as lists of scalar rows.

    Each dataset entry contains a :class:`RowWiseTableModel` where rows are ordered
    lists of JSON scalar values without explicit column-name metadata.
    """
    ...


class TableListOfDictsOfJsonScalarsDataset(Dataset[RowWiseTableWithColNamesModel]):
    """Store row-wise tables keyed by column names.

    Each dataset entry contains a :class:`RowWiseTableWithColNamesModel` where each
    row is a dictionary from column name to JSON scalar cell value.
    """
    ...


class TableDictOfDictsOfJsonScalarsDataset(Dataset[ColumnWiseTableWithColNamesAndIndexModel]):
    """Store indexed tables keyed by row identifier.

    Each dataset entry contains a :class:`ColumnWiseTableWithColNamesAndIndexModel`
    where each outer key identifies a row and maps to a column-name/value mapping.
    """
    ...


class TableDictOfListsOfJsonScalarsDataset(Dataset[JsonScalarColumnWiseTableWithColNamesModel]):
    ...


class TableWithColNamesDataset(Dataset[RowWiseTableFirstRowAsColNamesModel]):
    """Store row-wise tables that derive headers from the first row.

    Entries are normalized into :class:`RowWiseTableFirstRowAsColNamesModel` values,
    where the first row becomes the header for subsequent row dictionaries.
    """
    @property
    def col_names(self) -> tuple[str]:
        """Return distinct column names seen across all dataset entries.

        Returns:
            tuple[str]: Column names aggregated in first-seen order while iterating
                through dataset values.
        """
        col_names = {}
        for data_file in self.values():
            col_names.update(dict.fromkeys(data_file.col_names))
        return tuple(col_names.keys())


_PydanticModelT = TypeVar('_PydanticModelT', bound=pyd.BaseModel)


class TableOfPydanticRecordsDataset(Dataset[TableOfPydanticRecordsModel[_PydanticModelT]],
                                    Generic[_PydanticModelT]):
    """Store tables parsed into Pydantic-validated record lists.

    Each entry contains a :class:`TableOfPydanticRecordsModel` parameterized by the
    target Pydantic record schema.
    """
    ...


class TsvTableDataset(Dataset[TsvTableModel]):
    """Store TSV text parsed into header-aware row-wise tables.

    Each dataset entry contains a :class:`TsvTableModel` where the first row is used
    as column headers for the parsed table rows.
    """
    ...


class CsvTableDataset(Dataset[CsvTableModel]):
    """Store CSV text parsed into header-aware row-wise tables.

    Each dataset entry contains a :class:`CsvTableModel` where the first row is used
    as column headers for the parsed table rows.
    """
    ...
