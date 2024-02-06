from omnipy import Dataset

from .models import TableWithColNamesModel


class TableWithColNamesDataset(Dataset[TableWithColNamesModel]):
    @property
    def col_names(self) -> tuple[str]:
        col_names = {}
        for data_file in self.values():
            col_names.update(dict.fromkeys(data_file.col_names))
        return tuple(col_names.keys())
