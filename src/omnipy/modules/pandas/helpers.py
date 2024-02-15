import pandas as pd

from .models import PandasModel


def extract_common_colnames(df_1: PandasModel | pd.DataFrame, df_2: PandasModel | pd.DataFrame):
    common_colnames_set = set(df_1.columns) & set(df_2.columns)
    common_colnames = tuple(col for col in df_1.columns if col in common_colnames_set)
    return common_colnames
