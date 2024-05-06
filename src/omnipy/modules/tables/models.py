from typing import cast, Generic, TypeVar

from pydantic import BaseModel

from omnipy.data.model import Model

from ..json.models import (JsonCustomListModel,
                           JsonDictM,
                           JsonListM,
                           JsonListOfDictsOfScalarsModel,
                           JsonListOfListsOfScalarsModel)
from ..json.typedefs import JsonListOfDictsOfScalars


class TableOfStrings(Model[list[dict[str, str]]]):
    ...


class JsonTableOfStrings(JsonListM[JsonDictM[str]]):
    ...


class TableOfStringsAndLists(Model[list[dict[str, str | list[str]]]]):
    ...


class TableWithColNamesModel(Model[JsonListOfDictsOfScalarsModel | JsonListOfListsOfScalarsModel]):
    @classmethod
    def _parse_data(  # type: ignore[override]
        cls,
        data: JsonListOfDictsOfScalarsModel | JsonListOfListsOfScalarsModel
    ) -> JsonListOfDictsOfScalarsModel | JsonListOfDictsOfScalars:
        if len(data) > 0:
            if isinstance(data[0], JsonListM):  # type: ignore[index]
                first_row_as_colnames = JsonCustomListModel[str](data[0])  # type: ignore[index]
                first_row_as_colnames_data: list[str] = \
                    first_row_as_colnames.to_data()  # type: ignore[assignment]
                rows = data[1:]  # type: ignore[index]

                # if len(rows) == 0:
                #     rows = [[None] * len(first_row_as_colnames)]

                # col_name: JsonListOfScalars
                return [{
                    col_name: row[i] if i < len(row) else None for i,
                    col_name in enumerate(first_row_as_colnames_data)
                } for row in rows]
            else:
                assert isinstance(data[0], JsonDictM)  # type: ignore[index]
                return cast(JsonListOfDictsOfScalarsModel, data)

        return cast(JsonListOfDictsOfScalarsModel, data)

    @property
    def col_names(self) -> tuple[str]:
        col_names = {}
        for row in self:
            col_names.update(dict.fromkeys(row.keys()))  # type: ignore[attr-defined]
        return tuple(col_names.keys())


_PydanticModelT = TypeVar('_PydanticModelT', bound=BaseModel)


class TableOfPydanticRecordsModel(Model[list[_PydanticModelT]], Generic[_PydanticModelT]):
    ...
