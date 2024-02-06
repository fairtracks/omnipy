from dataclasses import dataclass
from typing import Annotated

from pandas import DataFrame
import pytest
import pytest_cases as pc

from modules.pandas.cases.table_pairs import TablePairCase
from modules.pandas.helpers.functions import convert_testcase_table_to_dataframe
from omnipy.modules.pandas.helpers import (
    are_values_of_equally_named_columns_internally_consistent, extract_common_colnames)


@pc.parametrize_with_cases('case', cases='.cases.table_pairs')
def test_extract_common_colnames(case: TablePairCase):
    case_df_1 = convert_testcase_table_to_dataframe(case.table_1)
    case_df_2 = convert_testcase_table_to_dataframe(case.table_2)
    assert extract_common_colnames(case_df_1, case_df_2) == case.common_colnames


# @pc.parametrize_with_cases('case', cases='.cases.dataframe_pairs')
# def test_are_values_of_equally_named_columns_internally_consistent(case: DataFramePairCase):
#     if case.common_colnames == ():
#         with pytest.raises(ValueError):
#             are_values_of_equally_named_columns_internally_consistent(case.df_1, case.df_2)
#     else:
#         print(are_values_of_equally_named_columns_internally_consistent(case.df_1, case.df_2))
#         assert are_values_of_equally_named_columns_internally_consistent(case.df_1, case.df_2) \
#             == case.common_cols_internally_consistent
