import pandas as pd


# not pairwise, can be more than two columns
def is_pairwise_consistent_values(df_1: pd.DataFrame,
                                  df_2: pd.DataFrame,
                                  common_headers: tuple[str, ...]):
    df_1_common_cols = pd.DataFrame(df_1, columns=common_headers)
    df_2_common_cols = pd.DataFrame(df_2, columns=common_headers)
    return (df_1_common_cols.drop_duplicates().sort_values(by=list(common_headers)).reset_index(drop=True) == \
        df_2_common_cols.drop_duplicates().sort_values(by=list(common_headers)).reset_index(drop=True)).all(axis=None)
