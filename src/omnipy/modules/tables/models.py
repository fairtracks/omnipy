from typing import cast, Generic, get_args, TypeVar

from pydantic import BaseModel

from omnipy.data.model import Model
from omnipy.data.param import conf

from ..general.models import Chain3
from ..json.models import JsonListOfScalarsModel
from ..json.typedefs import JsonScalar
from ..raw.models import SplitLinesToColumnsModelNew, SplitToLinesModel


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
                    first_row_as_colnames.to_data()

                return [{
                    col_name: row[i] if i < len(row) else None for i,
                    col_name in enumerate(first_row_as_colnames_data)
                } for j,
                        row in enumerate(data) if j > 0]
            else:
                assert isinstance(data[0], dict)  # type: ignore[index]
                return cast(TableListOfDictsOfJsonScalarsModel, data)

        return cast(TableListOfDictsOfJsonScalarsModel, data)

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


# Hack to avoid pydantic issue. Not great
config = conf(SplitLinesToColumnsModelNew.Params)


class TableOfPydanticRecordsModel(
        Model[list[PydanticRecordModel[_PydanticModelT]]
              | Chain3[SplitToLinesModel,
                       SplitLinesToColumnsModelNew[config()],
                       Model[list[PydanticRecordModel[_PydanticModelT]]]]],
        Generic[_PydanticModelT]):
    ...
