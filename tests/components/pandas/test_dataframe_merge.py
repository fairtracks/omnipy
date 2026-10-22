"""Tests for pandas table merge tasks."""

import pytest
import pytest_cases as pc

from omnipy.components.pandas.models import PandasModel
from omnipy.components.pandas.tasks import cartesian_product, join_tables

from .cases.tablepairs import TablePairCase
from .helpers.functions import convert_testcase_table_to_dataframe, get_target_as_pandas_model


@pytest.mark.usefixtures('runtime')
@pc.parametrize_with_cases('case', cases='.cases.tablepairs', has_tag='join')
def test_join_tables(
    case: TablePairCase,
):
    from omnipy.components.pandas.lazy_import import pd

    table_1 = PandasModel(convert_testcase_table_to_dataframe(case.table_1))
    table_2 = PandasModel(convert_testcase_table_to_dataframe(case.table_2))

    for join_type in ['outer', 'inner', 'left', 'right']:
        if case.exception_cls:
            with pytest.raises(case.exception_cls):
                join_tables.run(table_1, table_2, join_type=join_type, on_cols=case.on_cols)
        else:
            result = join_tables.run(table_1, table_2, join_type=join_type, on_cols=case.on_cols)
            target = get_target_as_pandas_model(
                getattr(case, f'result_{join_type}_join'), col_dtypes=case.col_dtypes
            )
            pd.testing.assert_frame_equal(result.content, target.content, check_dtype=False)


@pytest.mark.usefixtures('runtime')
@pc.parametrize_with_cases('case', cases='.cases.tablepairs', has_tag='cartesian')
def test_cartesian_product_of_tables(
    case: TablePairCase,
):
    from omnipy.components.pandas.lazy_import import pd

    table_1 = PandasModel(convert_testcase_table_to_dataframe(case.table_1))
    table_2 = PandasModel(convert_testcase_table_to_dataframe(case.table_2))

    if case.exception_cls:
        with pytest.raises(case.exception_cls):
            cartesian_product.run(table_1, table_2)
    else:
        result = cartesian_product.run(table_1, table_2)
        target = get_target_as_pandas_model(getattr(case, 'result_cartesian'))
        pd.testing.assert_frame_equal(result.content, target.content, check_column_type=False)


# Further tests
# TODO: join_tables: Multiple tables
