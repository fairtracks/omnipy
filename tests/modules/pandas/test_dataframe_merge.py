from typing import Annotated, NamedTuple

from pandas import DataFrame
import pandas as pd
import pytest
import pytest_cases as pc

from modules.pandas.cases.table_pairs import TablePairCase
from modules.pandas.helpers.functions import convert_testcase_table_to_dataframe
from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.modules.pandas.helpers import extract_common_colnames
from omnipy.modules.pandas.models import PandasDataset, PandasModel
from omnipy.modules.pandas.tasks import join_tables
from omnipy.modules.tables.models import TableWithColNamesModel


class TableJoinTest(NamedTuple):
    type: str
    attr: str
    on_last_common_col: bool


@pc.parametrize_with_cases('case', cases='.cases.table_pairs')
def test_join_tables(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case: TablePairCase,
):
    table_1 = PandasModel(TableWithColNamesModel(case.table_1))
    table_2 = PandasModel(TableWithColNamesModel(case.table_2))

    common_colnames = extract_common_colnames(table_1, table_2)

    for test_info in [
            TableJoinTest(type='outer', attr='res_outer_join', on_last_common_col=False),
            TableJoinTest(type='outer', attr='res_outer_join_last_col', on_last_common_col=True),
            TableJoinTest(type='inner', attr='res_inner_join', on_last_common_col=False),
            TableJoinTest(type='inner', attr='res_inner_join_last_col', on_last_common_col=True),
            TableJoinTest(type='left', attr='res_left_join', on_last_common_col=False),
            TableJoinTest(type='left', attr='res_left_join_last_col', on_last_common_col=True),
            TableJoinTest(type='right', attr='res_right_join', on_last_common_col=False),
            TableJoinTest(type='right', attr='res_right_join_last_col', on_last_common_col=True),
            TableJoinTest(type='cross', attr='res_cross_join', on_last_common_col=False),
    ]:
        if len(common_colnames) == 0:
            with pytest.raises(ValueError):
                _run_join_tables(common_colnames, table_1, table_2, test_info)
        else:
            result = _run_join_tables(common_colnames, table_1, table_2, test_info)
            target = _get_target_as_pandas_model(case, test_info)
            pd.testing.assert_frame_equal(result.contents, target.contents, check_dtype=False)


def _get_target_as_pandas_model(case: TablePairCase, test_info: TableJoinTest):
    return PandasModel(convert_testcase_table_to_dataframe(getattr(case, test_info.attr)))


def _run_join_tables(common_colnames: tuple[str, ...],
                     table_1: PandasModel,
                     table_2: PandasModel,
                     test_info: TableJoinTest) -> PandasModel:
    return join_tables.run(
        table_1,
        table_2,
        join_type=test_info.type,
        on_cols=common_colnames[-1] if common_colnames and test_info.on_last_common_col else None)


def test_default_outer_join_tables_on_column_all_matching(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_dbe: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe'] = table_dbe

    joined_dataset = join_tables.run(dataset)

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_default_outer_join_tables_on_column_some_matching(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_dbe2: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe2'] = table_dbe2

    joined_dataset = join_tables.run(dataset)

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=None, E=None),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
            dict(A=None, B=432, C=None, D=3.4, E=23),
        ]
    }


def test_inner_join_tables_on_column_all_matching(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_dbe: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe'] = table_dbe

    joined_dataset = join_tables.run(dataset, type='inner')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_inner_join_tables_on_column_some_matching(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_dbe2: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe2'] = table_dbe2

    joined_dataset = join_tables.run(dataset, type='inner')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_left_join_tables_on_column_all_matching(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_dbe: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe'] = table_dbe

    joined_dataset = join_tables.run(dataset, type='left')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_left_join_tables_on_column_some_matching(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_dbe2: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe2'] = table_dbe2

    joined_dataset = join_tables.run(dataset, type='left')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=None, E=None),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_right_join_tables_on_column_all_matching(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_dbe: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe'] = table_dbe

    joined_dataset = join_tables.run(dataset, type='right')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe': [
            dict(A='cde', B=345, C=True, D=1.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='abc', B=123, C=True, D=3.2, E=34),
        ]
    }


def test_right_join_tables_on_column_some_matching(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_dbe2: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe2'] = table_dbe2

    joined_dataset = join_tables.run(dataset, type='right')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='cde', B=345, C=True, D=1.2, E=34),
            dict(A=None, B=432, C=None, D=3.4, E=23),
            dict(A='abc', B=123, C=True, D=3.2, E=34),
        ]
    }


def test_default_outer_join_tables_multiple_columns_same_name_error(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_bce_consistent: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_bce_consistent'] = table_bce_consistent

    with pytest.raises(ValueError):
        join_tables.run(dataset)


def test_default_outer_join_tables_multiple_columns_same_name_allow_multiple_consistent(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_bce_consistent: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_bce_consistent'] = table_bce_consistent

    joined_dataset = join_tables.run(dataset, allow_multiple_join_cols_if_consistent=True)

    assert joined_dataset.to_data() == {
        'table_abc_join_table_bce_consistent': [
            dict(A='abc', B=123, C=True, E=34),
            dict(A='bcd', B=234, C=False, E=23),
            dict(A='cde', B=345, C=True, E=34),
        ]
    }


def test_default_outer_join_tables_multiple_columns_same_name_allow_multiple_consistent_dupl_row(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_bce_consistent_dupl_row: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_bce_consistent_dupl_row'] = table_bce_consistent_dupl_row

    joined_dataset = join_tables.run(dataset, allow_multiple_join_cols_if_consistent=True)

    assert joined_dataset.to_data() == {
        'table_abc_join_table_bce_consistent_dupl_row': [
            dict(A='abc', B=123, C=True, E=34),
            dict(A='bcd', B=234, C=False, E=23),
            dict(A='bcd', B=234, C=False, E=45),
            dict(A='cde', B=345, C=True, E=34),
        ]
    }


def test_default_outer_join_tables_multiple_columns_same_name_allow_multiple_consistent_complex(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_abc: Annotated[DataFrame, pytest.fixture],
    table_bce_inconsistent: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_bce_inconsistent'] = table_bce_inconsistent

    with pytest.raises(ValueError):
        join_tables.run(dataset, allow_multiple_join_cols_if_consistent=True)


def test_default_outer_join_tables_multiple_columns_same_name_allow_multiple_inconsistent(
    runtime: Annotated[IsRuntime, pytest.fixture],
    table_adult_lastname_firstname_consistent: Annotated[DataFrame, pytest.fixture],
    table_firstname_lastname_age: Annotated[DataFrame, pytest.fixture],
):
    dataset = PandasDataset()
    dataset['table_adult_lastname_firstname_consistent'] = table_adult_lastname_firstname_consistent
    dataset['table_firstname_lastname_age'] = table_firstname_lastname_age

    joined_dataset = join_tables.run(dataset, allow_multiple_join_cols_if_consistent=True)
    pass


# def test_join_tables_on_column_missing_data(
#     runtime: Annotated[IsRuntime, pytest.fixture],
#     table_abc: Annotated[DataFrame, pytest.fixture],
#     table_dbe2: Annotated[DataFrame, pytest.fixture],
# ):
#     dataset = PandasDataset()
#     dataset['table_abc'] = table_abc
#     dataset['table_dbe2'] = table_dbe2
#
#     joined_dataset = join_tables.run(dataset)
#
#     assert joined_dataset.to_data() == {
#         'table_a_join_table_b': [
#             dict(A='abc', B=123, C=True, D=3.2, E=34),
#             dict(A='bcd', B=234, C=False, D=3.4, E=23),
#             dict(A='cde', B=345, C=True, D=1.2, E=34),
#         ]
#     }

# Further tests
# TODO: join_tables: Specify left/right columns to merge on
# TODO: join_tables: Specify left/right columns to merge on -> multiple columns with same name
# TODO: join_tables: Specify left/right columns to merge on -> specified columns do not exist
# TODO: join_tables: Empty dataframe
# TODO: join_tables: Multiple tables
