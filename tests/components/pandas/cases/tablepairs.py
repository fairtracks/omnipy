from dataclasses import dataclass

import pytest_cases as pc

from omnipy.components.json.typedefs import JsonListOfListsOfScalars


@dataclass
class TablePairCase:
    table_1: JsonListOfListsOfScalars
    table_2: JsonListOfListsOfScalars
    common_colnames: tuple[str, ...]
    on_cols: tuple[str, ...] | dict[str, str] | None = None
    result_outer_join: JsonListOfListsOfScalars | None = None
    result_inner_join: JsonListOfListsOfScalars | None = None
    result_left_join: JsonListOfListsOfScalars | None = None
    result_right_join: JsonListOfListsOfScalars | None = None
    result_cartesian: JsonListOfListsOfScalars | None = None
    exception_cls: type[Exception] | None = None


@pc.case(id='error_join_two_empty_tables', tags=['join', 'on_all_cols'])
def case_error_join_two_empty_tables() -> TablePairCase:
    return TablePairCase(table_1=[], table_2=[], common_colnames=(), exception_cls=ValueError)


@pc.case(id='cross_two_empty_tables', tags=['cartesian'])
def case_cross_two_empty_tables() -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = []
    return TablePairCase(
        table_1=[], table_2=[], common_colnames=(), result_cartesian=result_cartesian)


@pc.case(id='join_two_empty_tables_with_cols', tags=['join', 'on_all_cols'])
def case_join_two_empty_tables_with_cols() -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [['a', 'b', 'c']]
    return TablePairCase(
        table_1=[['a', 'b']],
        table_2=[['b', 'c']],
        common_colnames=('b',),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_outer_join,
    )


@pc.case(id='cross_two_empty_tables_with_cols', tags=['cartesian'])
def case_cross_two_empty_tables_with_cols() -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [['a', 'b_1', 'b_2', 'c']]
    return TablePairCase(
        table_1=[['a', 'b']],
        table_2=[['b', 'c']],
        common_colnames=('b',),
        result_cartesian=result_cartesian)


@pc.case(id='join_two_tables_one_common_colname_all_match', tags=['join', 'on_all_cols'])
def case_join_two_tables_one_common_colname_all_match(
        table_age_firstname_lastname, table_weight_firstname_height_all_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', 69.8, 171],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_all_match,
        common_colnames=('firstname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_outer_join,
    )


@pc.case(id='cross_two_tables_one_common_colname_all_match', tags=['cartesian'])
def case_cross_two_tables_one_common_colname_all_match(
        table_age_firstname_lastname, table_weight_firstname_height_all_match) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'weight', 'firstname_2', 'height'],
        [7, 'Bob', 'Duck', 37.2, 'Bob', 127],
        [7, 'Bob', 'Duck', 75.4, 'Donald', 165],
        [7, 'Bob', 'Duck', 69.8, 'Mickey', 171],
        [39, 'Donald', 'Duck', 37.2, 'Bob', 127],
        [39, 'Donald', 'Duck', 75.4, 'Donald', 165],
        [39, 'Donald', 'Duck', 69.8, 'Mickey', 171],
        [41, 'Mickey', 'Mouse', 37.2, 'Bob', 127],
        [41, 'Mickey', 'Mouse', 75.4, 'Donald', 165],
        [41, 'Mickey', 'Mouse', 69.8, 'Mickey', 171],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_all_match,
        common_colnames=('firstname',),
        result_cartesian=result_cartesian,
    )


@pc.case(id='join_two_tables_one_common_colname_partial_match', tags=['join', 'on_all_cols'])
def case_join_two_tables_one_common_colname_partial_match(
        table_age_firstname_lastname, table_weight_firstname_height_partial_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', None, None],
    ]
    result_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_partial_match,
        common_colnames=('firstname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_inner_join,
        result_left_join=result_outer_join,
        result_right_join=result_inner_join,
    )


@pc.case(id='cross_two_tables_one_common_colname_partial_match', tags=['cartesian'])
def case_cross_two_tables_one_common_colname_partial_match(
        table_age_firstname_lastname, table_weight_firstname_height_partial_match) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'weight', 'firstname_2', 'height'],
        [7, 'Bob', 'Duck', 37.2, 'Bob', 127],
        [7, 'Bob', 'Duck', 75.4, 'Donald', 165],
        [39, 'Donald', 'Duck', 37.2, 'Bob', 127],
        [39, 'Donald', 'Duck', 75.4, 'Donald', 165],
        [41, 'Mickey', 'Mouse', 37.2, 'Bob', 127],
        [41, 'Mickey', 'Mouse', 75.4, 'Donald', 165],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_partial_match,
        common_colnames=('firstname',),
        result_cartesian=result_cartesian,
    )


@pc.case(
    id='join_two_tables_one_common_colname_partial_match_plus_extra', tags=['join', 'on_all_cols'])
def case_join_two_tables_one_common_colname_partial_match_plus_extra(
        table_age_firstname_lastname,
        table_weight_firstname_height_partial_match_plus_extra) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', None, None],
        [None, 'Minnie', None, 71.1, 168],
    ]
    result_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
    ]
    result_left_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', None, None],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [None, 'Minnie', None, 71.1, 168],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_partial_match_plus_extra,
        common_colnames=('firstname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_inner_join,
        result_left_join=result_left_join,
        result_right_join=result_right_join,
    )


@pc.case(id='cross_two_tables_one_common_colname_partial_match_plus_extra', tags=['cartesian'])
def case_cross_two_tables_one_common_colname_partial_match_plus_extra(
        table_age_firstname_lastname,
        table_weight_firstname_height_partial_match_plus_extra) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'weight', 'firstname_2', 'height'],
        [7, 'Bob', 'Duck', 37.2, 'Bob', 127],
        [7, 'Bob', 'Duck', 75.4, 'Donald', 165],
        [7, 'Bob', 'Duck', 71.1, 'Minnie', 168],
        [39, 'Donald', 'Duck', 37.2, 'Bob', 127],
        [39, 'Donald', 'Duck', 75.4, 'Donald', 165],
        [39, 'Donald', 'Duck', 71.1, 'Minnie', 168],
        [41, 'Mickey', 'Mouse', 37.2, 'Bob', 127],
        [41, 'Mickey', 'Mouse', 75.4, 'Donald', 165],
        [41, 'Mickey', 'Mouse', 71.1, 'Minnie', 168],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_partial_match_plus_extra,
        common_colnames=('firstname',),
        result_cartesian=result_cartesian,
    )


@pc.case(id='join_two_tables_two_common_colnames_all_match', tags=['join', 'on_all_cols'])
def case_join_two_tables_two_common_colnames_all_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_all_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
        [7, 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match,
        common_colnames=('firstname', 'lastname'),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_on_last_col_quadruple_plus_one_match', tags=['join'])
def case_join_two_tables_two_common_colnames_on_last_col_quadruple_plus_one_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_all_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match,
        common_colnames=('firstname', 'lastname'),
        on_cols=('lastname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(id='cross_two_tables_two_common_colnames_complete_match', tags=['cartesian'])
def case_cross_two_tables_two_common_colnames_complete_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_all_match) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname_1', 'firstname_2', 'lastname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', 'Duck', True],
        [7, 'Bob', 'Duck', 'Mickey', 'Mouse', True],
        [7, 'Bob', 'Duck', 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', 'Donald', 'Duck', True],
        [39, 'Donald', 'Duck', 'Mickey', 'Mouse', True],
        [39, 'Donald', 'Duck', 'Bob', 'Duck', False],
        [41, 'Mickey', 'Mouse', 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', 'Mickey', 'Mouse', True],
        [41, 'Mickey', 'Mouse', 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match,
        common_colnames=('firstname', 'lastname'),
        result_cartesian=result_cartesian,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_all_match_out_of_order', tags=['join', 'on_all_cols'])
def case_join_two_tables_two_common_colnames_all_match_out_of_order(
        table_age_firstname_lastname, table_adult_lastname_firstname_all_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
        [7, 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_adult_lastname_firstname_all_match,
        common_colnames=('firstname', 'lastname'),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_on_last_col_quadruple_plus_one_match_out_of_order',
    tags=['join'])
def case_join_two_tables_two_common_colnames_on_last_col_quadruple_plus_one_match_out_of_order(
        table_age_firstname_lastname, table_adult_lastname_firstname_all_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'adult', 'firstname_2'],
        [7, 'Bob', 'Duck', True, 'Donald'],
        [7, 'Bob', 'Duck', False, 'Bob'],
        [39, 'Donald', 'Duck', True, 'Donald'],
        [39, 'Donald', 'Duck', False, 'Bob'],
        [41, 'Mickey', 'Mouse', True, 'Mickey'],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'adult', 'firstname_2'],
        [7, 'Bob', 'Duck', True, 'Donald'],
        [39, 'Donald', 'Duck', True, 'Donald'],
        [41, 'Mickey', 'Mouse', True, 'Mickey'],
        [7, 'Bob', 'Duck', False, 'Bob'],
        [39, 'Donald', 'Duck', False, 'Bob'],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_adult_lastname_firstname_all_match,
        common_colnames=('firstname', 'lastname'),
        on_cols=('lastname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(id='cross_two_tables_two_common_colnames_complete_match_out_of_order', tags=['cartesian'])
def case_cross_two_tables_two_common_colnames_complete_match_out_of_order(
        table_age_firstname_lastname, table_adult_lastname_firstname_all_match) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname_1', 'adult', 'lastname_2', 'firstname_2'],
        [7, 'Bob', 'Duck', True, 'Duck', 'Donald'],
        [7, 'Bob', 'Duck', True, 'Mouse', 'Mickey'],
        [7, 'Bob', 'Duck', False, 'Duck', 'Bob'],
        [39, 'Donald', 'Duck', True, 'Duck', 'Donald'],
        [39, 'Donald', 'Duck', True, 'Mouse', 'Mickey'],
        [39, 'Donald', 'Duck', False, 'Duck', 'Bob'],
        [41, 'Mickey', 'Mouse', True, 'Duck', 'Donald'],
        [41, 'Mickey', 'Mouse', True, 'Mouse', 'Mickey'],
        [41, 'Mickey', 'Mouse', False, 'Duck', 'Bob'],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_adult_lastname_firstname_all_match,
        common_colnames=('firstname', 'lastname'),
        result_cartesian=result_cartesian,
    )


@pc.case(id='join_two_tables_two_common_colnames_double_match', tags=['join', 'on_all_cols'])
def case_join_two_tables_two_common_colnames_double_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_double_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', True],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', True],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
        [7, 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_double_match,
        common_colnames=('firstname', 'lastname'),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(id='join_two_tables_two_common_colnames_on_last_col_sixfold_plus_one_match', tags=['join'])
def case_join_two_tables_two_common_colnames_on_last_col_sixfold_plus_one_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_double_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Bob', True],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Bob', True],
        [39, 'Donald', 'Duck', 'Bob', True],
        [7, 'Bob', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_double_match,
        common_colnames=('firstname', 'lastname'),
        on_cols=('lastname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(
    id='cross_two_tables_two_common_colnames_complete_match_plus_duplicate', tags=['cartesian'])
def case_cross_two_tables_two_common_colnames_complete_match_plus_duplicate(
        table_age_firstname_lastname, table_firstname_lastname_adult_double_match) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname_1', 'firstname_2', 'lastname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Bob', 'Duck', True],
        [7, 'Bob', 'Duck', 'Donald', 'Duck', True],
        [7, 'Bob', 'Duck', 'Mickey', 'Mouse', True],
        [7, 'Bob', 'Duck', 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', 'Bob', 'Duck', True],
        [39, 'Donald', 'Duck', 'Donald', 'Duck', True],
        [39, 'Donald', 'Duck', 'Mickey', 'Mouse', True],
        [39, 'Donald', 'Duck', 'Bob', 'Duck', False],
        [41, 'Mickey', 'Mouse', 'Bob', 'Duck', True],
        [41, 'Mickey', 'Mouse', 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', 'Mickey', 'Mouse', True],
        [41, 'Mickey', 'Mouse', 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_double_match,
        common_colnames=('firstname', 'lastname'),
        result_cartesian=result_cartesian,
    )


@pc.case(id='join_two_tables_two_common_colnames_partial_match', tags=['join', 'on_all_cols'])
def case_join_two_tables_two_common_colnames_partial_match(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', None],
    ]
    result_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [39, 'Donald', 'Duck', True],
        [7, 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match,
        common_colnames=('firstname', 'lastname'),
        result_outer_join=result_outer_join,
        result_inner_join=result_inner_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_on_last_col_quadruple_plus_missing_match',
    tags=['join'])
def case_join_two_tables_two_common_colnames_on_last_col_quadruple_plus_missing_match(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
        [41, 'Mickey', 'Mouse', None, None],
    ]
    result_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match,
        common_colnames=('firstname', 'lastname'),
        on_cols=('lastname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_inner_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(id='cross_two_tables_two_common_colnames_partial_match', tags=['cartesian'])
def case_cross_two_tables_two_common_colnames_partial_match(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname_1', 'firstname_2', 'lastname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', 'Duck', True],
        [7, 'Bob', 'Duck', 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', 'Donald', 'Duck', True],
        [39, 'Donald', 'Duck', 'Bob', 'Duck', False],
        [41, 'Mickey', 'Mouse', 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match,
        common_colnames=('firstname', 'lastname'),
        result_cartesian=result_cartesian,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_partial_match_plus_extra', tags=['join', 'on_all_cols'])
def case_join_two_tables_two_common_colnames_partial_match_plus_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match_plus_extra) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', None],
        [None, 'Minnie', 'Mouse', True],
    ]
    result_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
    ]
    result_left_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', None],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [39, 'Donald', 'Duck', True],
        [None, 'Minnie', 'Mouse', True],
        [7, 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
        result_outer_join=result_outer_join,
        result_inner_join=result_inner_join,
        result_left_join=result_left_join,
        result_right_join=result_right_join,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_on_last_col_quadruple_plus_one_match_with_extra',
    tags=['join'])
def case_join_two_tables_two_common_colnames_on_last_col_quadruple_plus_one_match_with_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match_plus_extra) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
        [41, 'Mickey', 'Mouse', 'Minnie', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [41, 'Mickey', 'Mouse', 'Minnie', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
        on_cols=('lastname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(id='cross_two_tables_two_common_colnames_partial_match_plus_extra', tags=['cartesian'])
def case_cross_two_tables_two_common_colnames_partial_match_plus_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match_plus_extra) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname_1', 'firstname_2', 'lastname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', 'Duck', True],
        [7, 'Bob', 'Duck', 'Minnie', 'Mouse', True],
        [7, 'Bob', 'Duck', 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', 'Donald', 'Duck', True],
        [39, 'Donald', 'Duck', 'Minnie', 'Mouse', True],
        [39, 'Donald', 'Duck', 'Bob', 'Duck', False],
        [41, 'Mickey', 'Mouse', 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', 'Minnie', 'Mouse', True],
        [41, 'Mickey', 'Mouse', 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
        result_cartesian=result_cartesian,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_all_match_plus_extra', tags=['join', 'on_all_cols'])
def case_join_two_tables_two_common_colnames_all_match_plus_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_all_match_plus_extra) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
        [None, 'Minnie', 'Mouse', True],
    ]
    result_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
        [None, 'Minnie', 'Mouse', True],
        [7, 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
        result_outer_join=result_outer_join,
        result_inner_join=result_inner_join,
        result_left_join=result_inner_join,
        result_right_join=result_right_join,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_on_last_col_quadruple_plus_double_match_with_extra',
    tags=['join'])
def case_join_two_tables_two_common_colnames_on_last_col_quadruple_plus_double_match_with_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_all_match_plus_extra) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
        [41, 'Mickey', 'Mouse', 'Minnie', True],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
        [41, 'Mickey', 'Mouse', 'Minnie', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
        on_cols=('lastname',),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(id='cross_two_tables_two_common_colnames_complete_match_plus_extra', tags=['cartesian'])
def case_cross_two_tables_two_common_colnames_complete_match_plus_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_all_match_plus_extra) -> TablePairCase:

    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname_1', 'firstname_2', 'lastname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', 'Duck', True],
        [7, 'Bob', 'Duck', 'Mickey', 'Mouse', True],
        [7, 'Bob', 'Duck', 'Minnie', 'Mouse', True],
        [7, 'Bob', 'Duck', 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', 'Donald', 'Duck', True],
        [39, 'Donald', 'Duck', 'Mickey', 'Mouse', True],
        [39, 'Donald', 'Duck', 'Minnie', 'Mouse', True],
        [39, 'Donald', 'Duck', 'Bob', 'Duck', False],
        [41, 'Mickey', 'Mouse', 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', 'Mickey', 'Mouse', True],
        [41, 'Mickey', 'Mouse', 'Minnie', 'Mouse', True],
        [41, 'Mickey', 'Mouse', 'Bob', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
        result_cartesian=result_cartesian,
    )


@pc.case(id='join_two_tables_two_common_colnames_no_match', tags=['join', 'on_all_cols'])
def case_join_two_tables_two_common_colnames_no_match(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_no_match_when_paired) -> TablePairCase:
    # Why this order of result_outer_join?
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', None],
        [39, 'Donald', 'Duck', None],
        [41, 'Mickey', 'Mouse', None],
        [None, 'Mickey', 'Duck', True],
        [None, 'Mickey', 'Duck', False],
        [None, 'Donald', 'Mouse', True],
        [None, 'Bob', 'Mouse', False],
    ]
    result_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
    ]
    result_left_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', None],
        [39, 'Donald', 'Duck', None],
        [41, 'Mickey', 'Mouse', None],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [None, 'Mickey', 'Duck', True],
        [None, 'Donald', 'Mouse', True],
        [None, 'Bob', 'Mouse', False],
        [None, 'Mickey', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_no_match_when_paired,
        common_colnames=('firstname', 'lastname'),
        result_outer_join=result_outer_join,
        result_inner_join=result_inner_join,
        result_left_join=result_left_join,
        result_right_join=result_right_join,
    )


@pc.case(
    id='join_two_tables_two_common_colnames_on_last_col_using_mapping_quadruple_plus_double_match',
    tags=['join'])
def case_join_two_tables_two_common_colnames_on_last_col_using_mapping_quadruple_plus_double_match(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_no_match_when_paired) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Mickey', True],
        [7, 'Bob', 'Duck', 'Mickey', False],
        [39, 'Donald', 'Duck', 'Mickey', True],
        [39, 'Donald', 'Duck', 'Mickey', False],
        [41, 'Mickey', 'Mouse', 'Donald', True],
        [41, 'Mickey', 'Mouse', 'Bob', False],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Mickey', True],
        [39, 'Donald', 'Duck', 'Mickey', True],
        [41, 'Mickey', 'Mouse', 'Donald', True],
        [41, 'Mickey', 'Mouse', 'Bob', False],
        [7, 'Bob', 'Duck', 'Mickey', False],
        [39, 'Donald', 'Duck', 'Mickey', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_no_match_when_paired,
        common_colnames=('firstname', 'lastname'),
        on_cols=dict(lastname='lastname'),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(id='cross_two_tables_two_common_colnames_no_match', tags=['cartesian'])
def case_cross_two_tables_two_common_colnames_no_match(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_no_match_when_paired) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname_1', 'firstname_2', 'lastname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Mickey', 'Duck', True],
        [7, 'Bob', 'Duck', 'Donald', 'Mouse', True],
        [7, 'Bob', 'Duck', 'Bob', 'Mouse', False],
        [7, 'Bob', 'Duck', 'Mickey', 'Duck', False],
        [39, 'Donald', 'Duck', 'Mickey', 'Duck', True],
        [39, 'Donald', 'Duck', 'Donald', 'Mouse', True],
        [39, 'Donald', 'Duck', 'Bob', 'Mouse', False],
        [39, 'Donald', 'Duck', 'Mickey', 'Duck', False],
        [41, 'Mickey', 'Mouse', 'Mickey', 'Duck', True],
        [41, 'Mickey', 'Mouse', 'Donald', 'Mouse', True],
        [41, 'Mickey', 'Mouse', 'Bob', 'Mouse', False],
        [41, 'Mickey', 'Mouse', 'Mickey', 'Duck', False],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_no_match_when_paired,
        common_colnames=('firstname', 'lastname'),
        result_cartesian=result_cartesian,
    )


@pc.case(id='error_join_two_tables_no_common_colnames', tags=['join', 'on_all_cols'])
def case_error_join_two_tables_no_common_colnames(table_age_firstname_lastname,
                                                  table_last_first_weight_height) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_last_first_weight_height,
        common_colnames=(),
        exception_cls=ValueError,
    )


@pc.case(id='join_two_tables_no_common_colnames_on_mapping_both_cols', tags=['join'])
def case_join_two_tables_no_common_colnames_on_mapping_both_cols(
        table_age_firstname_lastname, table_last_first_weight_height) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'last', 'first', 'weight', 'height'],
        [7, 'Bob', 'Duck', 'Duck', 'Bob', 37.2, 127],
        [39, 'Donald', 'Duck', 'Duck', 'Donald', 75.4, 165],
        [41, 'Mickey', 'Mouse', 'Mouse', 'Mickey', 69.8, 171],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_last_first_weight_height,
        common_colnames=(),
        on_cols=dict(firstname='first', lastname='last'),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_outer_join,
    )


@pc.case(id='join_two_tables_no_common_colnames_on_mapping_one_col', tags=['join'])
def case_join_two_tables_no_common_colnames_on_mapping_one_col(
        table_age_firstname_lastname, table_last_first_weight_height) -> TablePairCase:
    result_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'last', 'first', 'weight', 'height'],
        [7, 'Bob', 'Duck', 'Duck', 'Bob', 37.2, 127],
        [7, 'Bob', 'Duck', 'Duck', 'Donald', 75.4, 165],
        [39, 'Donald', 'Duck', 'Duck', 'Bob', 37.2, 127],
        [39, 'Donald', 'Duck', 'Duck', 'Donald', 75.4, 165],
        [41, 'Mickey', 'Mouse', 'Mouse', 'Mickey', 69.8, 171],
    ]
    result_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'last', 'first', 'weight', 'height'],
        [7, 'Bob', 'Duck', 'Duck', 'Bob', 37.2, 127],
        [39, 'Donald', 'Duck', 'Duck', 'Bob', 37.2, 127],
        [7, 'Bob', 'Duck', 'Duck', 'Donald', 75.4, 165],
        [39, 'Donald', 'Duck', 'Duck', 'Donald', 75.4, 165],
        [41, 'Mickey', 'Mouse', 'Mouse', 'Mickey', 69.8, 171],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_last_first_weight_height,
        common_colnames=(),
        on_cols=dict(lastname='last'),
        result_outer_join=result_outer_join,
        result_inner_join=result_outer_join,
        result_left_join=result_outer_join,
        result_right_join=result_right_join,
    )


@pc.case(id='error_join_two_tables_two_common_colnames_on_empty_colname_list', tags=['join'])
def case_error_join_two_tables_two_common_colnames_on_empty_colname_list(
        table_age_firstname_lastname, table_firstname_lastname_adult_all_match) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match,
        common_colnames=('firstname', 'lastname'),
        on_cols=(),
        exception_cls=ValueError,
    )


@pc.case(id='error_join_two_tables_two_common_colnames_on_incorrect_colname', tags=['join'])
def case_error_join_two_tables_two_common_colnames_on_incorrect_colname(
        table_age_firstname_lastname, table_firstname_lastname_adult_all_match) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match,
        common_colnames=('firstname', 'lastname'),
        on_cols=('last',),
        exception_cls=KeyError,
    )


@pc.case(id='error_join_two_tables_no_common_colnames_on_empty_colname_mapping', tags=['join'])
def case_error_join_two_tables_no_common_colnames_on_empty_colname_mapping(
        table_age_firstname_lastname, table_last_first_weight_height) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_last_first_weight_height,
        common_colnames=(),
        on_cols=dict(),
        exception_cls=ValueError,
    )


@pc.case(id='error_join_two_tables_no_common_colnames_on_incorrect_colname_mapping', tags=['join'])
def case_error_join_two_tables_no_common_colnames_on_incorrect_colname_mapping(
        table_age_firstname_lastname, table_last_first_weight_height) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_last_first_weight_height,
        common_colnames=(),
        on_cols=dict(last='last'),
        exception_cls=KeyError,
    )


@pc.case(
    id='error_join_two_tables_no_common_colnames_on_incorrect_colname_mapping_2', tags=['join'])
def case_error_join_two_tables_no_common_colnames_on_incorrect_colname_mapping_2(
        table_age_firstname_lastname, table_last_first_weight_height) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_last_first_weight_height,
        common_colnames=(),
        on_cols=dict(lastname='lastname'),
        exception_cls=KeyError,
    )


@pc.case(id='cross_two_tables_no_common_colnames', tags=['cartesian'])
def case_cross_two_tables_no_common_colnames(table_age_firstname_lastname,
                                             table_last_first_weight_height) -> TablePairCase:
    result_cartesian: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'last', 'first', 'weight', 'height'],
        [7, 'Bob', 'Duck', 'Duck', 'Bob', 37.2, 127],
        [7, 'Bob', 'Duck', 'Duck', 'Donald', 75.4, 165],
        [7, 'Bob', 'Duck', 'Mouse', 'Mickey', 69.8, 171],
        [39, 'Donald', 'Duck', 'Duck', 'Bob', 37.2, 127],
        [39, 'Donald', 'Duck', 'Duck', 'Donald', 75.4, 165],
        [39, 'Donald', 'Duck', 'Mouse', 'Mickey', 69.8, 171],
        [41, 'Mickey', 'Mouse', 'Duck', 'Bob', 37.2, 127],
        [41, 'Mickey', 'Mouse', 'Duck', 'Donald', 75.4, 165],
        [41, 'Mickey', 'Mouse', 'Mouse', 'Mickey', 69.8, 171],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_last_first_weight_height,
        common_colnames=(),
        result_cartesian=result_cartesian,
    )
