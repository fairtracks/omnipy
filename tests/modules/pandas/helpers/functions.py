import pandas as pd


def convert_testcase_table_to_dataframe(test_case_table):
    return pd.DataFrame(test_case_table[1:], columns=test_case_table[0]).convert_dtypes()
