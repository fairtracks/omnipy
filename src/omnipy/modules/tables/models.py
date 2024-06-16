from typing import cast, Generic, get_args, TypeVar

from pydantic import BaseModel

from omnipy.data.model import Model

from ..general.models import Chain3
from ..json.models import (JsonCustomDictModel,
                           JsonCustomListModel,
                           JsonListOfDictsOfScalarsModel,
                           JsonListOfListsOfScalarsModel,
                           JsonListOfScalarsModel)
from ..json.typedefs import JsonListOfDictsOfScalars
from ..raw.models import SplitLinesToColumnsModel, SplitToLinesModel

# class TableOfStrings(Model[list[dict[str, str]]]):
#     ...
#
#
# class JsonTableOfStrings(JsonCustomListModel[JsonCustomDictModel[str]]):
#     ...
#
#
# class TableOfStringsAndLists(Model[list[dict[str, str | list[str]]]]):
#     ...


# TODO: Add a test for TableWithColNamesModel
class TableWithColNamesModel(Model[JsonListOfDictsOfScalarsModel | JsonListOfListsOfScalarsModel]):
    @classmethod
    def _parse_data(
        cls, data: JsonListOfDictsOfScalarsModel | JsonListOfListsOfScalarsModel
    ) -> JsonListOfDictsOfScalarsModel | JsonListOfDictsOfScalars:
        if len(data) > 0:
            if isinstance(data[0].contents, list):
                first_row_as_colnames = JsonCustomListModel[str](data[0])
                first_row_as_colnames_data: list[str] = \
                    first_row_as_colnames.to_data()
                rows = data[1:]

                # if len(rows) == 0:
                #     rows = [[None] * len(first_row_as_colnames)]

                # col_name: JsonListOfScalars
                return [{
                    col_name: row[i] if i < len(row) else None for i,
                    col_name in enumerate(first_row_as_colnames_data)
                } for row in rows]
            else:
                assert isinstance(data[0].contents, dict)
                return cast(JsonListOfDictsOfScalarsModel, data)

        return cast(JsonListOfDictsOfScalarsModel, data)

    @property
    def col_names(self) -> tuple[str]:
        col_names = {}
        for row in self:
            col_names.update(dict.fromkeys(row.keys()))  # type: ignore[attr-defined]
        return tuple(col_names.keys())


_PydanticModelT = TypeVar('_PydanticModelT', bound=BaseModel)


class PydanticRecordModel(Model[_PydanticModelT | JsonListOfScalarsModel],
                          Generic[_PydanticModelT]):
    @classmethod
    def _parse_data(cls, data: _PydanticModelT | JsonListOfScalarsModel) -> _PydanticModelT:
        match data:
            case JsonListOfScalarsModel():
                pydantic_model = get_args(cls.outer_type(with_args=True))[0]
                headers = pydantic_model.__fields__.keys()
                assert len(headers) == len(data), f'{len(headers)} != {len(data)}'
                return pydantic_model(**dict(zip(headers, data)))
            case _:
                return data


class TableOfPydanticRecordsModel(
        Model[list[PydanticRecordModel[_PydanticModelT]]
              | Chain3[SplitToLinesModel,
                       SplitLinesToColumnsModel,
                       Model[list[PydanticRecordModel[_PydanticModelT]]]]],
        Generic[_PydanticModelT]):
    ...
