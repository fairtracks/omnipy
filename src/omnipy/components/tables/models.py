from typing import cast, Generic, get_args, TypeVar

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd

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


_PydBaseModelT = TypeVar('_PydBaseModelT', bound=pyd.BaseModel)
_PydRecordT = TypeVar('_PydRecordT', bound=pyd.BaseModel)


class PydanticRecordModel(Model[_PydBaseModelT | JsonListOfScalarsModel], Generic[_PydBaseModelT]):
    @classmethod
    def _parse_data(cls, data: _PydBaseModelT | JsonListOfScalarsModel) -> _PydBaseModelT:
        match data:
            case JsonListOfScalarsModel():
                pydantic_model = get_args(cls.outer_type(with_args=True))[0]
                headers = pydantic_model.__fields__

                num_required_fields = -1
                for i, header_field in enumerate(headers.values()):
                    if not header_field.required:
                        if num_required_fields == -1:
                            num_required_fields = i
                        continue
                    elif num_required_fields != -1 and i > num_required_fields:
                        raise ValueError('Required fields must not come after optional fields')

                assert len(headers) >= len(data) >= num_required_fields, \
                    (f'Incorrect number of data elements: '
                     f'{len(headers)} >= {len(data)} >= {num_required_fields}')

                return pydantic_model(**dict(zip(headers, data)))
            case _:
                return data


class TableOfPydanticRecordsModel(Chain3[SplitToLinesModel,
                                         SplitLinesToColumnsModel,
                                         Model[list[PydanticRecordModel[_PydRecordT]]]],
                                  Generic[_PydRecordT]):
    ...


class TsvTableModel(Chain3[
        SplitToLinesModel,
        SplitLinesToColumnsModel,
        TableWithColNamesModel,
]):
    ...


# TODO: Implement SplitLinesToColumnsByCommaModel properly in parallel to SplitLinesToColumnsModel

SplitLinesToColumnsByCommaModel = SplitLinesToColumnsModel.adjust(
    'SplitLinesToColumnsByCommaModel', delimiter=',')


class CsvTableModel(Chain3[
        SplitToLinesModel,
        SplitLinesToColumnsByCommaModel,
        TableWithColNamesModel,
]):
    ...
