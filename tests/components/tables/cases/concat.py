from dataclasses import dataclass
import typing

import pytest_cases as pc
from scripts.type_alias_example import JsonScalar

from omnipy.components.tables.models import (ColumnWiseTableDictOfListsModel,
                                             ColWiseAddOtherType,
                                             RowWiseTableListOfDictsModel)

from .raw.table_data import (col_wise_dict_of_empty_lists_data,
                             column_wise_dict_of_lists_data,
                             concat_col_wise_data,
                             concat_non_overlapping_col_wise_data,
                             other_col_wise_dict_of_lists_data,
                             other_non_overlapping_col_wise_dict_of_lists_data,
                             other_row_wise_list_of_dicts_data,
                             reverse_concat_col_wise_data,
                             reverse_concat_non_overlapping_col_wise_data)

if typing.TYPE_CHECKING:
    pass


@dataclass
class ConcatCase:
    col_wise_model: ColumnWiseTableDictOfListsModel
    other: ColWiseAddOtherType
    expected: dict[str, list[JsonScalar]]


@dataclass
class ConcatCaseReverse(ConcatCase):
    expected_reverse: dict[str, list[JsonScalar]]


@pc.case(id='concat_col_wise_model_with_col_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_col_wise_model() -> ConcatCase:
    return ConcatCase(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=ColumnWiseTableDictOfListsModel(other_col_wise_dict_of_lists_data),
        expected=concat_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_dict_of_lists', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_dict_of_lists() -> ConcatCase:
    return ConcatCaseReverse(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=other_col_wise_dict_of_lists_data,
        expected=concat_col_wise_data,
        expected_reverse=reverse_concat_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_row_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_row_wise_model() -> ConcatCase:
    return ConcatCase(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=RowWiseTableListOfDictsModel(other_row_wise_list_of_dicts_data),
        expected=concat_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_list_of_dicts', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_list_of_dicts() -> ConcatCase:
    return ConcatCaseReverse(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=other_row_wise_list_of_dicts_data,
        expected=concat_col_wise_data,
        expected_reverse=reverse_concat_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_non_overlapping_col_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_non_overlapping_col_wise_model() -> ConcatCase:
    return ConcatCase(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=ColumnWiseTableDictOfListsModel(other_non_overlapping_col_wise_dict_of_lists_data),
        expected=concat_non_overlapping_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_non_overlapping_dict_of_lists', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_non_overlapping_dict_of_lists() -> ConcatCase:
    return ConcatCaseReverse(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=other_non_overlapping_col_wise_dict_of_lists_data,
        expected=concat_non_overlapping_col_wise_data,
        expected_reverse=reverse_concat_non_overlapping_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_empty_col_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_empty_col_wise_model() -> ConcatCase:
    return ConcatCase(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=ColumnWiseTableDictOfListsModel(),
        expected=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_empty_dict', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_empty_dict() -> ConcatCase:
    return ConcatCaseReverse(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other={},
        expected=column_wise_dict_of_lists_data,
        expected_reverse=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_col_wise_empty_lists_model', tags=['concat'])
def case_concat_col_wise_model_with_col_wise_empty_lists_model() -> ConcatCase:
    return ConcatCase(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=ColumnWiseTableDictOfListsModel(col_wise_dict_of_empty_lists_data),
        expected=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_dict_of_empty_lists', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_dict_of_empty_lists() -> ConcatCase:
    return ConcatCaseReverse(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=col_wise_dict_of_empty_lists_data,
        expected=column_wise_dict_of_lists_data,
        expected_reverse=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_empty_row_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_empty_row_wise_model() -> ConcatCase:
    return ConcatCase(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=RowWiseTableListOfDictsModel(),
        expected=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_empty_list', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_empty_list() -> ConcatCase:
    return ConcatCaseReverse(
        col_wise_model=ColumnWiseTableDictOfListsModel(column_wise_dict_of_lists_data),
        other=[],
        expected=column_wise_dict_of_lists_data,
        expected_reverse=column_wise_dict_of_lists_data,
    )
