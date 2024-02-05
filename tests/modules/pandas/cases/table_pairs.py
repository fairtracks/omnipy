from dataclasses import dataclass

import pytest_cases as pc

from omnipy.modules.json.typedefs import JsonListOfListsOfScalars


@dataclass
class TablePairCase:
    table_1: JsonListOfListsOfScalars
    table_2: JsonListOfListsOfScalars
    common_colnames: tuple[str, ...]
    result_inner_join: JsonListOfListsOfScalars | None = None
    result_outer_join: JsonListOfListsOfScalars | None = None


@pc.case(id='table_pair_one_common_colname_all_match', tags=[''])
def case_table_pair_one_common_colname_all_match(
        table_age_firstname_lastname, table_weight_firstname_height_all_match) -> TablePairCase:
    result_inner_join: JsonListOfListsOfScalars = [
        ['age', 'firstname', 'lastname', 'weight', 'height'],
        [7, 'Bob', 'Duck', 37.2, 127],
        [39, 'Donald', 'Duck', 75.4, 165],
        [41, 'Mickey', 'Mouse', 69.8, 171],
    ]
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_all_match,
        common_colnames=('firstname',),
        result_inner_join=result_inner_join,
        result_outer_join=result_inner_join,
    )


@pc.case(id='table_pair_one_common_colname_partial_match', tags=[''])
def case_table_pair_one_common_colname_partial_match(
        table_age_firstname_lastname, table_weight_firstname_height_partial_match) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_partial_match,
        common_colnames=('firstname',),
        result_inner_join=[
            ['age', 'firstname', 'lastname', 'weight', 'height'],
            [7, 'Bob', 'Duck', 37.2, 127],
            [39, 'Donald', 'Duck', 75.4, 165],
        ],
        result_outer_join=[
            ['age', 'firstname', 'lastname', 'weight', 'height'],
            [7, 'Bob', 'Duck', 37.2, 127],
            [39, 'Donald', 'Duck', 75.4, 165],
            [41, 'Mickey', 'Mouse', None, None],
        ],
    )


@pc.case(id='table_pair_one_common_colname_partial_match_plus_extra', tags=[''])
def case_table_pair_one_common_colname_partial_match_plus_extra(
        table_age_firstname_lastname,
        table_weight_firstname_height_partial_match_plus_extra) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_firstname_height_partial_match_plus_extra,
        common_colnames=('firstname',),
        result_inner_join=[
            ['age', 'firstname', 'lastname', 'weight', 'height'],
            [7, 'Bob', 'Duck', 37.2, 127],
            [39, 'Donald', 'Duck', 75.4, 165],
        ],
        result_outer_join=[
            ['age', 'firstname', 'lastname', 'weight', 'height'],
            [7, 'Bob', 'Duck', 37.2, 127],
            [39, 'Donald', 'Duck', 75.4, 165],
            [41, 'Mickey', 'Mouse', None, None],
            [None, 'Minnie', None, 71.1, 168],
        ],
    )


@pc.case(id='table_pair_multiple_common_colnames_all_match', tags=[''])
def case_table_pair_multiple_common_colnames_all_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_all_match) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match,
        common_colnames=('firstname', 'lastname'),
    )


@pc.case(id='table_pair_multiple_common_colnames_double_match', tags=[''])
def case_table_pair_multiple_common_colnames_double_match(
        table_age_firstname_lastname, table_firstname_lastname_adult_double_match) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_double_match,
        common_colnames=('firstname', 'lastname'),
    )


@pc.case(id='table_pair_multiple_common_colnames_partial_match', tags=[''])
def case_table_pair_multiple_common_colnames_partial_match(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match,
        common_colnames=('firstname', 'lastname'),
    )


@pc.case(id='table_pair_multiple_common_colnames_partial_match_plus_extra', tags=[''])
def case_table_pair_multiple_common_colnames_partial_match_plus_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_partial_match_plus_extra) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_partial_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
    )


@pc.case(id='table_pair_multiple_common_colnames_all_match_plus_extra', tags=[''])
def case_table_pair_multiple_common_colnames_all_match_plus_extra(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_all_match_plus_extra) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_all_match_plus_extra,
        common_colnames=('firstname', 'lastname'),
    )


@pc.case(id='table_pair_multiple_common_colnames_all_match_out_of_order', tags=[''])
def case_table_pair_multiple_common_colnames_all_match_out_of_order(
        table_age_firstname_lastname, table_lastname_firstname_adult_all_match) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_lastname_firstname_adult_all_match,
        common_colnames=('firstname', 'lastname'),
    )


@pc.case(id='table_pair_multiple_common_colnames_no_match_when_paired', tags=[''])
def case_table_pair_multiple_common_colnames_no_match_when_paired(
        table_age_firstname_lastname,
        table_firstname_lastname_adult_no_match_when_paired) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_firstname_lastname_adult_no_match_when_paired,
        common_colnames=('firstname', 'lastname'),
    )


@pc.case(id='table_pair_no_common_colnames', tags=[''])
def case_table_pair_no_common_colnames(table_age_firstname_lastname,
                                       table_weight_height) -> TablePairCase:
    return TablePairCase(
        table_1=table_age_firstname_lastname,
        table_2=table_weight_height,
        common_colnames=(),
    )
