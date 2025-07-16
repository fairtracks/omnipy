from omnipy.components.json.typedefs import JsonListOfListsOfScalars
from omnipy.components.pandas.models import PandasModel


def convert_testcase_table_to_dataframe(
    testcase_table: JsonListOfListsOfScalars,
    col_dtypes: dict[str, str] | None = None,
):
    from omnipy.components.pandas.lazy_import import pd

    if len(testcase_table) == 0:
        return pd.DataFrame([])

    df = pd.DataFrame(testcase_table[1:], columns=testcase_table[0])
    if col_dtypes:
        df = df.astype(col_dtypes)
    return df.convert_dtypes()


def get_target_as_pandas_model(
    testcase_table: JsonListOfListsOfScalars,
    col_dtypes: dict[str, str] | None = None,
) -> PandasModel:
    return PandasModel(convert_testcase_table_to_dataframe(testcase_table, col_dtypes=col_dtypes))
