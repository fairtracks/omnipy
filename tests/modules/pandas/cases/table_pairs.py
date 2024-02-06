from dataclasses import dataclass

import pytest_cases as pc

from omnipy.modules.json.typedefs import JsonListOfListsOfScalars


@dataclass
class TablePairCase:
    table_1: JsonListOfListsOfScalars
    table_2: JsonListOfListsOfScalars
    common_colnames: tuple[str, ...]
    res_outer_join: JsonListOfListsOfScalars | None = None
    res_outer_join_last_col: JsonListOfListsOfScalars | None = None
    res_inner_join: JsonListOfListsOfScalars | None = None
    res_inner_join_last_col: JsonListOfListsOfScalars | None = None
    res_left_join: JsonListOfListsOfScalars | None = None
    res_left_join_last_col: JsonListOfListsOfScalars | None = None
    res_right_join: JsonListOfListsOfScalars | None = None
    res_right_join_last_col: JsonListOfListsOfScalars | None = None
    res_cross_join: JsonListOfListsOfScalars | None = None
    res_cross_join_last_col: JsonListOfListsOfScalars | None = None


@pc.case(id='table_pair_one_common_colname_all_match', tags=[''])
def case_table_pair_one_common_colname_all_match(
        table_age_firstname_lastname, table_weight_firstname_height_all_match) -> TablePairCase:
    res_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', 69.8, 171],
    ]
    res_cross_join: JsonListOfListsOfScalars = [
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
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join,
        res_inner_join=res_outer_join,
        res_inner_join_last_col=res_outer_join,
        res_left_join=res_outer_join,
        res_left_join_last_col=res_outer_join,
        res_right_join=res_outer_join,
        res_right_join_last_col=res_outer_join,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_one_common_colname_partial_match', tags=[''])
def case_table_pair_one_common_colname_partial_match(
        table_age_firstname_lastname, table_weight_firstname_height_partial_match) -> TablePairCase:
    res_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', None, None],
    ]
    res_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
    ]
    res_cross_join: JsonListOfListsOfScalars = [
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
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join,
        res_inner_join=res_inner_join,
        res_inner_join_last_col=res_inner_join,
        res_left_join=res_outer_join,
        res_left_join_last_col=res_outer_join,
        res_right_join=res_inner_join,
        res_right_join_last_col=res_inner_join,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_one_common_colname_partial_match_plus_extra', tags=[''])
def case_table_pair_one_common_colname_partial_match_plus_extra(
        table_age_firstname_lastname,
        table_weight_firstname_height_partial_match_plus_extra) -> TablePairCase:
    res_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', None, None],
        [None, 'Minnie', None, 71.1, 168],
    ]
    res_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
    ]
    res_left_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', None, None],
    ]
    res_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [None, 'Minnie', None, 71.1, 168],
    ]
    res_cross_join: JsonListOfListsOfScalars = [
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
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join,
        res_inner_join=res_inner_join,
        res_inner_join_last_col=res_inner_join,
        res_left_join=res_left_join,
        res_left_join_last_col=res_left_join,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_multiple_common_colnames_all_match', tags=[''])
def case_table_pair_multiple_common_colnames_all_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_all_match) -> TablePairCase:
    res_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
    ]
    res_outer_join_last_col: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
    ]
    res_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
        [7, 'Bob', 'Duck', False],
    ]
    res_right_join_last_col: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    res_cross_join: JsonListOfListsOfScalars = [
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
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join_last_col,
        res_inner_join=res_outer_join,
        res_inner_join_last_col=res_outer_join_last_col,
        res_left_join=res_outer_join,
        res_left_join_last_col=res_outer_join_last_col,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join_last_col,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_multiple_common_colnames_double_match', tags=[''])
def case_table_pair_multiple_common_colnames_double_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_double_match) -> TablePairCase:
    res_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', True],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
    ]
    res_outer_join_last_col: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Bob', True],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
    ]
    res_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', True],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', True],
        [7, 'Bob', 'Duck', False],
    ]
    res_right_join_last_col: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Bob', True],
        [39, 'Donald', 'Duck', 'Bob', True],
        [7, 'Bob', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [41, 'Mickey', 'Mouse', 'Mickey', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    res_cross_join: JsonListOfListsOfScalars = [
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
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join_last_col,
        res_inner_join=res_outer_join,
        res_inner_join_last_col=res_outer_join_last_col,
        res_left_join=res_outer_join,
        res_left_join_last_col=res_outer_join_last_col,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join_last_col,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_multiple_common_colnames_partial_match', tags=[''])
def case_table_pair_multiple_common_colnames_partial_match(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match) -> TablePairCase:
    res_outer_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
        [41, 'Mickey', 'Mouse', None],
    ]
    res_outer_join_last_col: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
        [41, 'Mickey', 'Mouse', None, None],
    ]
    res_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [7, 'Bob', 'Duck', False],
        [39, 'Donald', 'Duck', True],
    ]
    res_inner_join_last_col: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    res_right_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'adult'],
        [39, 'Donald', 'Duck', True],
        [7, 'Bob', 'Duck', False],
    ]
    res_right_join_last_col: JsonListOfListsOfScalars = [
        ['age', 'firstname_1', 'lastname', 'firstname_2', 'adult'],
        [7, 'Bob', 'Duck', 'Donald', True],
        [39, 'Donald', 'Duck', 'Donald', True],
        [7, 'Bob', 'Duck', 'Bob', False],
        [39, 'Donald', 'Duck', 'Bob', False],
    ]
    res_cross_join: JsonListOfListsOfScalars = [
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
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join_last_col,
        res_inner_join=res_inner_join,
        res_inner_join_last_col=res_inner_join_last_col,
        res_left_join=res_outer_join,
        res_left_join_last_col=res_outer_join_last_col,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join_last_col,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_multiple_common_colnames_partial_match_plus_extra', tags=[''])
def case_table_pair_multiple_common_colnames_partial_match_plus_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match_plus_extra) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join,
        res_inner_join=res_inner_join,
        res_inner_join_last_col=res_inner_join,
        res_left_join=res_left_join,
        res_left_join_last_col=res_left_join,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_multiple_common_colnames_all_match_plus_extra', tags=[''])
def case_table_pair_multiple_common_colnames_all_match_plus_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_all_match_plus_extra) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join,
        res_inner_join=res_inner_join,
        res_inner_join_last_col=res_inner_join,
        res_left_join=res_left_join,
        res_left_join_last_col=res_left_join,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_multiple_common_colnames_all_match_out_of_order', tags=[''])
def case_table_pair_multiple_common_colnames_all_match_out_of_order(
        table_age_firstname_lastname, table_lastname_firstname_adult_all_match) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_lastname_firstname_adult_all_match,
        common_colnames=('firstname', 'lastname'),
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join,
        res_inner_join=res_inner_join,
        res_inner_join_last_col=res_inner_join,
        res_left_join=res_left_join,
        res_left_join_last_col=res_left_join,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_multiple_common_colnames_no_match_when_paired', tags=[''])
def case_table_pair_multiple_common_colnames_no_match_when_paired(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_no_match_when_paired) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_no_match_when_paired,
        common_colnames=('firstname', 'lastname'),
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join,
        res_inner_join=res_inner_join,
        res_inner_join_last_col=res_inner_join,
        res_left_join=res_left_join,
        res_left_join_last_col=res_left_join,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join,
        res_cross_join=res_cross_join,
    )


@pc.case(id='table_pair_no_common_colnames', tags=[''])
def case_table_pair_no_common_colnames(table_age_firstname_lastname,
                                       table_weight_height) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_height,
        common_colnames=(),
        res_outer_join=res_outer_join,
        res_outer_join_last_col=res_outer_join,
        res_inner_join=res_inner_join,
        res_inner_join_last_col=res_inner_join,
        res_left_join=res_left_join,
        res_left_join_last_col=res_left_join,
        res_right_join=res_right_join,
        res_right_join_last_col=res_right_join,
        res_cross_join=res_cross_join,
    )
