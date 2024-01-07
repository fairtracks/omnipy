from typing import Annotated

from pandas import DataFrame
import pytest

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.modules.pandas.models import PandasDataset
from omnipy.modules.pandas.tasks import join_tables


@pytest.fixture
def table_abc():
    return DataFrame(
        [
            ['abc', 123, True],
            ['bcd', 234, False],
            ['cde', 345, True],
        ],
        columns=['A', 'B', 'C'],
    )


@pytest.fixture
def table_dbe():
    return DataFrame(
        [
            [1.2, 345, 34],
            [3.4, 234, 23],
            [3.2, 123, 34],
        ],
        columns=['D', 'B', 'E'],
    )


@pytest.fixture
def table_dbe2():
    return DataFrame(
        [
            [1.2, 345, 34],
            [3.4, 432, 23],
            [3.2, 123, 34],
        ],
        columns=['D', 'B', 'E'],
    )


@pytest.fixture
def table_bce():
    return DataFrame(
        [
            [345, True, 34],
            [234, False, 23],
            [123, True, 34],
        ],
        columns=['B', 'C', 'E'],
    )


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

    joined_dataset = join_tables.run(dataset, join_type='inner')

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

    joined_dataset = join_tables.run(dataset, join_type='inner')

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

    joined_dataset = join_tables.run(dataset, join_type='left')

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

    joined_dataset = join_tables.run(dataset, join_type='left')

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

    joined_dataset = join_tables.run(dataset, join_type='right')

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

    joined_dataset = join_tables.run(dataset, join_type='right')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='cde', B=345, C=True, D=1.2, E=34),
            dict(A=None, B=432, C=None, D=3.4, E=23),
            dict(A='abc', B=123, C=True, D=3.2, E=34),
        ]
    }


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
