import pandas as pd

from omnipy import PandasModel
from omnipy.modules.json.typedefs import JsonListOfListsOfScalars


def convert_testcase_table_to_dataframe(testcase_table: JsonListOfListsOfScalars):
    if len(testcase_table) == 0:
        return pd.DataFrame([])

    return pd.DataFrame(testcase_table[1:], columns=testcase_table[0]).convert_dtypes()


def get_target_as_pandas_model(testcase_table: JsonListOfListsOfScalars):
    return PandasModel(convert_testcase_table_to_dataframe(testcase_table))
