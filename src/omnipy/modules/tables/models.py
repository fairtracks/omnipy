from typing import cast, Generic, get_args, TypeVar

from pydantic import BaseModel

from omnipy.data.model import Model

from ..general.models import Chain3
from ..json.models import JsonListOfScalarsModel
from ..json.typedefs import JsonScalar
from ..raw.models import SplitLinesToColumnsModel, SplitToLinesModel


class TableListOfListsOfJsonScalarsModel(Model[list[list[JsonScalar]]]):
    ...


class TableListOfDictsOfJsonScalarsModel(Model[list[dict[str, JsonScalar]]]):
    ...


class TableDictOfDictsOfJsonScalarsModel(Model[dict[str, dict[str, JsonScalar]]]):
    ...


class TableDictOfListsOfJsonScalarsModel(Model[dict[str, list[JsonScalar]]]):
    ...


# TODO: Add a test for TableWithColNamesModel
class TableWithColNamesModel(Model[TableListOfDictsOfJsonScalarsModel
                                   | TableListOfListsOfJsonScalarsModel]):
    @classmethod
    def _parse_data(
        cls, data: TableListOfDictsOfJsonScalarsModel | TableListOfListsOfJsonScalarsModel
    ) -> TableListOfDictsOfJsonScalarsModel:
        if len(data) > 0:
            if isinstance(data[0], list):  # type: ignore[index]
                first_row_as_colnames = Model[list[str]](data[0])  # type: ignore[index]
                first_row_as_colnames_data: list[str] = \
                    first_row_as_colnames.to_data()  # type: ignore[assignment]

                return cls._convert_list_of_lists_to_list_of_dicts(data, first_row_as_colnames_data)
            else:
                assert isinstance(data[0], dict)  # type: ignore[index]
                return cast(TableListOfDictsOfJsonScalarsModel, data)

        return cast(TableListOfDictsOfJsonScalarsModel, data)

    @classmethod
    def _convert_list_of_lists_to_list_of_dicts(cls, data, first_row_as_colnames_data):
        # TODO: Fix auto-formatting. Current setting is relatively ugly many places
        return [
            {
                col_name: (row[i] if i < len(row) else None)
                for (i, col_name) in enumerate(first_row_as_colnames_data)
            }
            for (j, row) in enumerate(data)  # noqa: E126
            if j > 0
        ]

    @property
    def col_names(self) -> tuple[str]:
        col_names = {}
        for row in self:
            col_names.update(dict.fromkeys(row.keys()))  # type: ignore[attr-defined]
        return tuple(col_names.keys())


_PydanticBaseModelT = TypeVar('_PydanticBaseModelT', bound=BaseModel)
_PydanticRecordT = TypeVar('_PydanticRecordT', bound=BaseModel)


class PydanticRecordModel(Model[_PydanticBaseModelT | JsonListOfScalarsModel],
                          Generic[_PydanticBaseModelT]):
    @classmethod
    def _parse_data(cls, data: _PydanticBaseModelT | JsonListOfScalarsModel) -> _PydanticBaseModelT:
        match data:
            case JsonListOfScalarsModel():
                pydantic_model = get_args(cls.outer_type(with_args=True))[0]
                headers = pydantic_model.__fields__.keys()
                assert len(headers) == len(data), f'{len(headers)} != {len(data)}'
                return pydantic_model(**dict(zip(headers, data)))
            case _:
                return data


class TableOfPydanticRecordsModel(Chain3[SplitToLinesModel,
                                         SplitLinesToColumnsModel,
                                         Model[list[PydanticRecordModel[_PydanticRecordT]]]],
                                  Generic[_PydanticRecordT]):
    ...
