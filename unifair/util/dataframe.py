import pandas as pd


def split_dataframe(df, row_labels_to_move, col_labels_to_move, row_level=1, col_level=0):
    mv_rows = select_from_labels(df, row_labels_to_move, axis=0, level=row_level)
    kp_rows = select_from_labels(df, row_labels_to_move, axis=0, level=row_level, invert=True)
    mv_cols = select_from_labels(df, col_labels_to_move, axis=1, level=col_level)
    kp_cols = select_from_labels(df, col_labels_to_move, axis=1, level=col_level, invert=True)

    kp_df = extract_subtable_by_labels(df, kp_rows, kp_cols, row_level, col_level)
    new_row_df = extract_subtable_by_labels(df, kp_rows, mv_cols, row_level, col_level)
    new_col_df = extract_subtable_by_labels(df, mv_rows, kp_cols, row_level, col_level)
    new_row_col_df = extract_subtable_by_labels(df, mv_rows, mv_cols, row_level, col_level)

    return kp_df, new_row_df, new_col_df, new_row_col_df


def select_from_labels(df, labels, axis, level, invert=False):
    assert axis in [0, 1]
    assert level in [0, 1]

    idx = df.index.levels[level] if axis == 0 else df.columns.levels[level]
    filtered_idx = idx[~idx.isin(labels)] if invert else idx[idx.isin(labels)]
    formatted_idx = tuple(filtered_idx)
    return formatted_idx


def extract_subtable_by_labels(df,
                               row_labels=None,
                               col_labels=None,
                               row_level=None,
                               col_level=None):
    if row_labels:
        rows = [df.xs(row, axis=0, level=row_level, drop_level=False) for row in row_labels]
        df = pd.concat(rows)
    if col_labels:
        cols = [df.xs(col, axis=1, level=col_level, drop_level=False) for col in col_labels]
        df = pd.concat(cols, axis=1)
    return df
