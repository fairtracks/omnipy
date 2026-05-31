"""Concatenation cases for components tables tests."""

from dataclasses import dataclass
from typing import Generic

import pytest_cases as pc
from typing_extensions import TypeVar

from omnipy.components.tables.models import (ColumnModel,
                                             ColumnWiseTableWithColNamesModel,
                                             ColWiseAddOtherType,
                                             JsonScalarColumnWiseTableWithColNamesModel,
                                             RowWiseTableWithColNamesModel)
from omnipy.shared.protocols.stdlib_ext import IsItemSequenceLike
from omnipy.shared.protocols.typing import IsMapping

from ..helpers.classes import (FloatListLikeColumnWiseTableWithColNamesModel,
                               IntListLikeColumnWiseTableWithColNamesModel)
from .raw.table_data import (col_wise_dict_of_empty_lists_data,
                             col_wise_list_likes_of_int_data,
                             column_wise_dict_of_int_data,
                             column_wise_dict_of_lists_data,
                             column_wise_dict_of_other_int_data,
                             concat_col_wise_data,
                             concat_col_wise_list_likes_of_float_data,
                             concat_col_wise_list_likes_of_int_data,
                             concat_non_overlapping_col_wise_data,
                             other_col_wise_dict_of_lists_data,
                             other_non_overlapping_col_wise_dict_of_lists_data,
                             other_row_wise_list_of_dicts_data,
                             reverse_concat_col_wise_data,
                             reverse_concat_non_overlapping_col_wise_data,
                             reversed_concat_col_wise_list_likes_of_float_data,
                             reversed_concat_col_wise_list_likes_of_int_data,
                             row_wise_dict_of_other_float_data)

_ColModelT = TypeVar('_ColModelT', bound=ColumnModel)
_ColModelItemT = TypeVar('_ColModelItemT')


@dataclass
class ConcatCase(Generic[_ColModelT, _ColModelItemT]):
    col_wise_model: ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT]
    other: ColumnWiseTableWithColNamesModel[_ColModelT, _ColModelItemT] | ColWiseAddOtherType
    expected: IsMapping[str, IsItemSequenceLike[_ColModelItemT]]


@dataclass
class ConcatCaseReverse(
        ConcatCase[_ColModelT, _ColModelItemT],
        Generic[_ColModelT, _ColModelItemT],
):
    expected_reverse: IsMapping[str, IsItemSequenceLike[_ColModelItemT]]


@pc.case(id='concat_col_wise_model_with_col_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_col_wise_model() -> ConcatCase:
    """Return the concat col wise model with col wise model case."""
    return ConcatCase(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=JsonScalarColumnWiseTableWithColNamesModel(other_col_wise_dict_of_lists_data),
        expected=concat_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_dict_of_lists', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_dict_of_lists() -> ConcatCase:
    """Return the concat col wise model with dict of lists case."""
    return ConcatCaseReverse(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=other_col_wise_dict_of_lists_data,
        expected=concat_col_wise_data,
        expected_reverse=reverse_concat_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_row_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_row_wise_model() -> ConcatCase:
    """Return the concat col wise model with row wise model case."""
    return ConcatCase(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=RowWiseTableWithColNamesModel(other_row_wise_list_of_dicts_data),
        expected=concat_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_list_of_dicts', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_list_of_dicts() -> ConcatCase:
    """Return the concat col wise model with list of dicts case."""
    return ConcatCaseReverse(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=other_row_wise_list_of_dicts_data,
        expected=concat_col_wise_data,
        expected_reverse=reverse_concat_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_non_overlapping_col_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_non_overlapping_col_wise_model() -> ConcatCase:
    """Return the concat col wise model with non overlapping col wise model case."""
    return ConcatCase(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=JsonScalarColumnWiseTableWithColNamesModel(
            other_non_overlapping_col_wise_dict_of_lists_data),
        expected=concat_non_overlapping_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_non_overlapping_dict_of_lists', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_non_overlapping_dict_of_lists() -> ConcatCase:
    """Return the concat col wise model with non overlapping dict of lists case."""
    return ConcatCaseReverse(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=other_non_overlapping_col_wise_dict_of_lists_data,
        expected=concat_non_overlapping_col_wise_data,
        expected_reverse=reverse_concat_non_overlapping_col_wise_data,
    )


@pc.case(id='concat_col_wise_model_with_empty_col_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_empty_col_wise_model() -> ConcatCase:
    """Return the concat col wise model with empty col wise model case."""
    return ConcatCase(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=JsonScalarColumnWiseTableWithColNamesModel(),
        expected=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_empty_dict', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_empty_dict() -> ConcatCase:
    """Return the concat col wise model with empty dict case."""
    return ConcatCaseReverse(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other={},
        expected=column_wise_dict_of_lists_data,
        expected_reverse=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_col_wise_empty_lists_model', tags=['concat'])
def case_concat_col_wise_model_with_col_wise_empty_lists_model() -> ConcatCase:
    """Return the concat col wise model with col wise empty lists model case."""
    return ConcatCase(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=JsonScalarColumnWiseTableWithColNamesModel(col_wise_dict_of_empty_lists_data),
        expected=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_dict_of_empty_lists', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_dict_of_empty_lists() -> ConcatCase:
    """Return the concat col wise model with dict of empty lists case."""
    return ConcatCaseReverse(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=col_wise_dict_of_empty_lists_data,
        expected=column_wise_dict_of_lists_data,
        expected_reverse=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_empty_row_wise_model', tags=['concat'])
def case_concat_col_wise_model_with_empty_row_wise_model() -> ConcatCase:
    """Return the concat col wise model with empty row wise model case."""
    return ConcatCase(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=RowWiseTableWithColNamesModel(),
        expected=column_wise_dict_of_lists_data,
    )


@pc.case(id='concat_col_wise_model_with_empty_list', tags=['concat', 'reverse'])
def case_concat_col_wise_model_with_empty_list() -> ConcatCase:
    """Return the concat col wise model with empty list case."""
    return ConcatCaseReverse(
        col_wise_model=JsonScalarColumnWiseTableWithColNamesModel(column_wise_dict_of_lists_data),
        other=[],
        expected=column_wise_dict_of_lists_data,
        expected_reverse=column_wise_dict_of_lists_data,
    )


@pc.case(id='list_like_col_wise_model_with_empty_row_wise_model', tags=['concat'])
def case_list_like_col_wise_model_with_empty_row_wise_model() -> ConcatCase:
    return ConcatCase(
        col_wise_model=IntListLikeColumnWiseTableWithColNamesModel(column_wise_dict_of_int_data),
        other=RowWiseTableWithColNamesModel(),
        expected=col_wise_list_likes_of_int_data,
    )


@pc.case(id='list_like_col_wise_model_with_int_other', tags=['concat', 'reverse'])
def case_list_like_col_wise_model_with_int_other() -> ConcatCase:
    return ConcatCaseReverse(
        col_wise_model=IntListLikeColumnWiseTableWithColNamesModel(column_wise_dict_of_int_data),
        other=column_wise_dict_of_other_int_data,
        expected=concat_col_wise_list_likes_of_int_data,
        expected_reverse=reversed_concat_col_wise_list_likes_of_int_data,
    )


@pc.case(id='list_like_col_wise_model_with_float_other', tags=['concat', 'reverse'])
def case_list_like_col_wise_model_with_float_other() -> ConcatCase:
    return ConcatCaseReverse(
        col_wise_model=FloatListLikeColumnWiseTableWithColNamesModel(column_wise_dict_of_int_data),
        other=row_wise_dict_of_other_float_data,
        expected=concat_col_wise_list_likes_of_float_data,
        expected_reverse=reversed_concat_col_wise_list_likes_of_float_data,
    )
