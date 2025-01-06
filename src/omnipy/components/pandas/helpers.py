import pandas as pd

from .models import PandasModel


def extract_common_colnames(df_1: PandasModel | pd.DataFrame, df_2: PandasModel | pd.DataFrame):
    common_colnames_set = set(df_1.columns) & set(df_2.columns)
    common_colnames = tuple(col for col in df_1.columns if col in common_colnames_set)
    return common_colnames


# def _something(df: pd.DataFrame, common_colnames: tuple[str]):
#     df_common_cols = df[list(common_colnames)]
#     df_no_duplicates = df_common_cols.drop_duplicates()
#     df_no_duplicates_sorted = df_no_duplicates.sort_values(by=list(common_colnames))
#     df_no_duplicates_sorted_no_index = df_no_duplicates_sorted.reset_index(drop=True)
#     return df_no_duplicates_sorted_no_index
#
#
# def are_values_of_equally_named_columns_internally_consistent(df_1: pd.DataFrame,
#                                                               df_2: pd.DataFrame):
#     common_colnames = extract_common_colnames(df_1, df_2)
#     something_df_1 = _something(df_1, common_colnames)
#     something_df_2 = _something(df_2, common_colnames)
#     match len(common_colnames):
#         case 0:
#             raise ValueError('No common colnames found')
#         case 1:
#             return True
#         case _:
#             return something_df_1.shape == something_df_2.shape and (
#                 something_df_1 == something_df_2).all(axis=None)
