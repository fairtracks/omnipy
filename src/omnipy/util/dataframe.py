"""Helpers for slicing multi-index pandas dataframes by label groups.

This module provides small dataframe utilities for splitting a dataframe into
kept and moved row/column sections and for extracting subtables by index-level
labels.
"""

import pandas as pd


def split_dataframe(df, row_labels_to_move, col_labels_to_move, row_level=1, col_level=0):
    """Split a dataframe into kept and moved row/column sections.

    Args:
        df: Dataframe with multi-index rows and columns.
        row_labels_to_move: Labels to move out of the kept row group.
        col_labels_to_move: Labels to move out of the kept column group.
        row_level: Row index level used for label matching.
        col_level: Column index level used for label matching.

    Returns:
        A 4-tuple containing the kept subtable, the kept-rows/moved-columns
        subtable, the moved-rows/kept-columns subtable, and the moved-rows/
        moved-columns subtable.
    """
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
    """Return labels from a dataframe index level that match a filter.

    Args:
        df: Dataframe whose row or column index levels are inspected.
        labels: Labels to select or exclude.
        axis: ``0`` for row labels or ``1`` for column labels.
        level: Multi-index level to inspect.
        invert: When ``True``, return labels not present in ``labels``.

    Returns:
        A tuple of matching labels from the requested index level.
    """
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
    """Extract a subtable by row and column labels from selected index levels.

    Args:
        df: Dataframe to slice.
        row_labels: Optional row labels to keep.
        col_labels: Optional column labels to keep.
        row_level: Row index level used when selecting rows.
        col_level: Column index level used when selecting columns.

    Returns:
        A dataframe restricted to the requested rows and columns.
    """
    if row_labels:
        rows = [df.xs(row, axis=0, level=row_level, drop_level=False) for row in row_labels]
        df = pd.concat(rows)
    if col_labels:
        cols = [df.xs(col, axis=1, level=col_level, drop_level=False) for col in col_labels]
        df = pd.concat(cols, axis=1)
    return df
