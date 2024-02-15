from typing import Generic, TypeVar

from pydantic import BaseModel

from omnipy.data.model import Model

from ..json.models import (JsonCustomListModel,
                           JsonDictM,
                           JsonListM,
                           JsonListOfDictsOfScalarsModel,
                           JsonListOfListsOfScalarsModel)


class TableOfStrings(Model[list[dict[str, str]]]):
    ...


class JsonTableOfStrings(JsonListM[JsonDictM[str]]):
    ...


class TableOfStringsAndLists(Model[list[dict[str, str | list[str]]]]):
    ...


class TableWithColNamesModel(Model[JsonListOfListsOfScalarsModel | JsonListOfDictsOfScalarsModel]):
    @classmethod
    def _parse_data(cls, data: JsonListOfListsOfScalarsModel | JsonListOfDictsOfScalarsModel):
        if len(data) > 0:
            if isinstance(data[0], JsonListM):
                first_row_as_colnames = JsonCustomListModel[str](data[0])
                rows = data[1:]
                # if len(rows) == 0:
                #     rows = [[None] * len(first_row_as_colnames)]
                return [{
                    col_name: row[i] if i < len(row) else None for i,
                    col_name in enumerate(first_row_as_colnames)
                } for row in rows]
            else:
                assert isinstance(data[0], JsonDictM)
                return data

        return data

    @property
    def col_names(self) -> tuple[str]:
        col_names = {}
        for row in self:
            col_names.update(dict.fromkeys(row.keys()))
        return tuple(col_names.keys())


_PydanticModelT = TypeVar('_PydanticModelT', bound=BaseModel)


class TableOfPydanticRecordsModel(Model[list[_PydanticModelT]], Generic[_PydanticModelT]):
    ...
