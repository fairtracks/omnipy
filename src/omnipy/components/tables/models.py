import typing
from typing import Any, cast, Generic, get_args

from typing_extensions import TypeVar

from omnipy.data.model import Model
import omnipy.util._pydantic as pyd

from ..general.models import Chain3
from ..json.models import JsonListOfScalarsModel
from ..json.typedefs import JsonScalar
from ..raw.models import (SplitLinesToColumnsByCommaModel,
                          SplitLinesToColumnsModel,
                          SplitToLinesModel)


class RowWiseTableListOfListsModel(Model[list[list[JsonScalar]]]):
    ...


class RowWiseTableListOfDictsModel(
        Model['list[dict[str, JsonScalar]] | ColumnWiseTableDictOfListsNoConvertModel']):
    @classmethod
    def _parse_data(
        cls, data: 'list[dict[str, JsonScalar]] | ColumnWiseTableDictOfListsNoConvertModel'
    ) -> list[dict[str, JsonScalar]]:
        if isinstance(data, ColumnWiseTableDictOfListsNoConvertModel):
            # Convert column-wise to row-wise
            converted_data: list[dict[str, JsonScalar]] = []
            for col_name, col_values in data.content.items():
                for i, value in enumerate(col_values):
                    if i >= len(converted_data):
                        converted_data.append({})
                    converted_data[i][col_name] = value
            return converted_data
        else:
            return data


class RowWiseTableListOfDictsNoConvertModel(Model[list[dict[str, JsonScalar]]]):
    ...


class ColumnWiseTableDictOfDictsModel(Model[dict[str, dict[str, JsonScalar]]]):
    ...


class ColumnWiseTableDictOfListsModel(
        Model['dict[str, list[JsonScalar]] | RowWiseTableListOfDictsNoConvertModel']):
    @classmethod
    def _parse_data(
        cls, data: 'dict[str, list[JsonScalar]] | RowWiseTableListOfDictsNoConvertModel'
    ) -> dict[str, list[JsonScalar]]:
        if isinstance(data, RowWiseTableListOfDictsNoConvertModel):
            row_wise_data = cast(list[dict[str, JsonScalar]], data)
            # Convert row-wise to column-wise
            column_wise_data: dict[str, list[JsonScalar]] = {}
            row: dict[str, JsonScalar]
            for i, row in enumerate(row_wise_data):
                for col_name, value in row.items():
                    if col_name not in column_wise_data:
                        # New column, need to create new list and pad previous rows with None
                        column_wise_data[col_name] = [None] * i
                    column_wise_data[col_name].append(value)
                for col_name_not_in_row in column_wise_data.keys() - row.keys():
                    # Pad missing columns with None
                    column_wise_data[col_name_not_in_row].append(None)
            return column_wise_data
        else:
            return data


class ColumnWiseTableDictOfListsNoConvertModel(Model[dict[str, list[JsonScalar]]]):
    ...


RowWiseTableListOfDictsModel.update_forward_refs()


class ColNamesMixin:
    @property
    def col_names(self) -> tuple[str, ...]:
        col_names = {}
        for row in self:  # type: ignore[attr-defined]
            col_names.update(dict.fromkeys(row.keys()))
        return tuple(col_names.keys())


if typing.TYPE_CHECKING:
    from omnipy.data._mimic_models import Model_list

    class _RowWiseTableFirstRowAsColNamesModel(  # type: ignore[misc]
            ColNamesMixin,
            Model_list[dict[str, JsonScalar]],
    ):
        ...


class RowWiseTableFirstRowAsColNamesModel(ColNamesMixin,
                                          Model[list[dict[str, JsonScalar]]
                                                | RowWiseTableListOfListsModel]):
    if typing.TYPE_CHECKING:

        def __new__(  # type: ignore[misc]
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> '_RowWiseTableFirstRowAsColNamesModel':
            ...

    @classmethod
    def _parse_data(
        cls, data: list[dict[str, JsonScalar]] | RowWiseTableListOfListsModel
    ) -> list[dict[str, JsonScalar]]:
        if isinstance(data, RowWiseTableListOfListsModel):
            data_list_of_lists = data.content

            if len(data_list_of_lists) > 0:
                first_row_as_colnames = Model[list[str]](data_list_of_lists[0]).content

                return cls._convert_list_of_lists_to_list_of_dicts(data_list_of_lists,
                                                                   first_row_as_colnames)
            else:
                return []
        else:
            return data

    @classmethod
    def _convert_list_of_lists_to_list_of_dicts(
        cls,
        data: list[list[JsonScalar]],
        first_row_as_colnames: list[str],
    ) -> list[dict[str, JsonScalar]]:
        # TODO: Fix auto-formatting. Current setting is relatively ugly many places
        return [
            {
                col_name: (row[i] if i < len(row) else None)
                for (i, col_name) in enumerate(first_row_as_colnames)
            }
            for (j, row) in enumerate(data)  # noqa: E126
            if j > 0
        ]


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


if typing.TYPE_CHECKING:
    from omnipy.data._mimic_models import Model_list

    class TableOfPydanticRecordsModel(Model_list[PydanticRecordModel[_PydRecordT]],
                                      Generic[_PydRecordT]):
        ...
else:

    class TableOfPydanticRecordsModel(Chain3[SplitToLinesModel,
                                             SplitLinesToColumnsModel,
                                             Model[list[PydanticRecordModel[_PydRecordT]]]],
                                      Generic[_PydRecordT]):
        ...


class TsvTableModel(Chain3[
        SplitToLinesModel,
        SplitLinesToColumnsModel,
        RowWiseTableFirstRowAsColNamesModel,
]):
    if typing.TYPE_CHECKING:

        def __new__(  # type: ignore[misc]
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> '_RowWiseTableFirstRowAsColNamesModel':
            ...


class CsvTableModel(Chain3[
        SplitToLinesModel,
        SplitLinesToColumnsByCommaModel,  # type: ignore[valid-type]
        RowWiseTableFirstRowAsColNamesModel,
]):
    if typing.TYPE_CHECKING:

        def __new__(  # type: ignore[misc]
            cls,
            *args: Any,
            **kwargs: Any,
        ) -> '_RowWiseTableFirstRowAsColNamesModel':
            ...
