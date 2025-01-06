import pytest_cases as pc

from omnipy.components.pandas.helpers import extract_common_colnames

from .cases.tablepairs import TablePairCase
from .helpers.functions import convert_testcase_table_to_dataframe


@pc.parametrize_with_cases('case', cases='.cases.tablepairs', has_tag='on_all_cols')
def test_extract_common_colnames(case: TablePairCase):
    case_df_1 = convert_testcase_table_to_dataframe(case.table_1)
    case_df_2 = convert_testcase_table_to_dataframe(case.table_2)
    assert extract_common_colnames(case_df_1, case_df_2) == case.common_colnames
