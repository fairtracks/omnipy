import pytest_cases as pc

from modules.pandas.cases.tablepairs import TablePairCase
from modules.pandas.helpers.functions import convert_testcase_table_to_dataframe
from omnipy.modules.pandas.helpers import extract_common_colnames


@pc.parametrize_with_cases('case', cases='.cases.tablepairs', has_tag='on_all_cols')
def test_extract_common_colnames(case: TablePairCase):
    case_df_1 = convert_testcase_table_to_dataframe(case.table_1)
    case_df_2 = convert_testcase_table_to_dataframe(case.table_2)
    assert extract_common_colnames(case_df_1, case_df_2) == case.common_colnames
