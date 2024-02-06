from typing import Annotated, NamedTuple

import pandas as pd
import pytest
import pytest_cases as pc

from modules.pandas.cases.tablepairs import TablePairCase
from modules.pandas.helpers.functions import (convert_testcase_table_to_dataframe,
                                              get_target_as_pandas_model)
from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.modules.pandas.models import PandasModel
from omnipy.modules.pandas.tasks import cartesian_product, join_tables


class TableJoinTest(NamedTuple):
    type: str
    attr: str


@pc.parametrize_with_cases('case', cases='.cases.tablepairs', has_tag='join')
def test_join_tables(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case: TablePairCase,
):
    table_1 = PandasModel(convert_testcase_table_to_dataframe(case.table_1))
    table_2 = PandasModel(convert_testcase_table_to_dataframe(case.table_2))

    for join_type in ['outer', 'inner', 'left', 'right']:
        if case.exception_cls:
            with pytest.raises(case.exception_cls):
                join_tables.run(table_1, table_2, join_type=join_type, on_cols=case.on_cols)
        else:
            result = join_tables.run(table_1, table_2, join_type=join_type, on_cols=case.on_cols)
            target = get_target_as_pandas_model(getattr(case, f'result_{join_type}_join'))
            pd.testing.assert_frame_equal(result.contents, target.contents, check_dtype=False)


@pc.parametrize_with_cases('case', cases='.cases.tablepairs', has_tag='cartesian')
def test_cartesian_product_of_tables(
    runtime: Annotated[IsRuntime, pytest.fixture],
    case: TablePairCase,
):
    table_1 = PandasModel(convert_testcase_table_to_dataframe(case.table_1))
    table_2 = PandasModel(convert_testcase_table_to_dataframe(case.table_2))

    if case.exception_cls:
        with pytest.raises(case.exception_cls):
            cartesian_product.run(table_1, table_2)
    else:
        result = cartesian_product.run(table_1, table_2)
        target = get_target_as_pandas_model(getattr(case, 'result_cartesian'))
        pd.testing.assert_frame_equal(result.contents, target.contents, check_column_type=False)


# Further tests
# TODO: join_tables: Multiple tables
