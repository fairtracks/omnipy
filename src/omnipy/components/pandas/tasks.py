"""Tasks for converting, combining, and reshaping pandas-backed datasets."""

from io import StringIO
from typing import Mapping, Sequence

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..general.models import NotIterableExceptStrOrBytesModel
from .datasets import ListOfPandasDatasetsWithSameNumberOfFiles, PandasDataset
from .helpers import extract_common_colnames
from .models import PandasModel


@TaskTemplate()
def convert_dataset_list_of_dicts_to_pandas(
        dataset: Dataset[Model[list[dict[str, NotIterableExceptStrOrBytesModel]]]]) \
        -> PandasDataset:
    """Convert list-of-dicts files to a pandas-backed dataset.

    Args:
        dataset: Dataset where each file contains a list of row dictionaries.

    Returns:
        A dataset with the same file keys, where each file is represented as a
        ``PandasModel`` table.

    Raises:
        Exception: Propagates validation or conversion errors raised while
            constructing pandas-backed files.

    Example:
        >>> from omnipy.data.dataset import Dataset
        >>> from omnipy.data.model import Model
        >>> input_ds = Dataset[Model[list[dict[str, int]]]]({'rows': [{'a': 1}, {'a': 2}]})
        >>> out_ds = convert_dataset_list_of_dicts_to_pandas.run(input_ds)
        >>> tuple(out_ds.keys())
        ('rows',)
    """

    pandas_dataset = PandasDataset()
    pandas_dataset.from_data(dataset.to_data())
    return pandas_dataset


@TaskTemplate()
def convert_dataset_csv_to_pandas(dataset: Dataset[Model[bytes]],
                                  delimiter: str = ',',
                                  first_row_as_col_names=True,
                                  col_names: list[str] | None = None,
                                  ignore_comments: bool = True,
                                  comments_char: str = '#') -> PandasDataset:
    """Parse CSV-like files into a pandas-backed dataset.

    Args:
        dataset: Dataset with CSV content in each file.
        delimiter: Field delimiter used in the CSV content.
        first_row_as_col_names: Whether to infer column names from the first
            row.
        col_names: Explicit column names to use when parsing.
        ignore_comments: Whether to ignore comment lines.
        comments_char: Character marking the beginning of comment lines.

    Returns:
        A ``PandasDataset`` with one parsed table per input file.

    Raises:
        Exception: Propagates parsing errors raised by ``pandas.read_csv``.

    Example:
        >>> from omnipy.data.dataset import Dataset
        >>> from omnipy.data.model import Model
        >>> ds = Dataset[Model[bytes]]({'table.csv': b'a,b\n1,2\n'})
        >>> out_ds = convert_dataset_csv_to_pandas.run(ds)
        >>> tuple(out_ds.keys())
        ('table.csv',)
    """

    from .lazy_import import pd

    out_dataset = PandasDataset()
    for key, item in dataset.items():
        df = pd.read_csv(
            StringIO(item.content),
            sep=delimiter,
            header='infer' if first_row_as_col_names else 0,
            names=col_names,
            comment=comments_char if ignore_comments else None,
            encoding='utf8',
        )
        out_dataset[key] = df
    return out_dataset


@TaskTemplate()
def convert_dataset_pandas_to_csv(
    dataset: PandasDataset,
    delimiter: str = ',',
    first_row_as_col_names=True,
    col_names: list[str] | None = None,
) -> Dataset[Model[str]]:
    """Serialize pandas-backed files in a dataset to CSV text files.

    Args:
        dataset: Dataset containing pandas-backed table files.
        delimiter: Field delimiter to use in output CSV text.
        first_row_as_col_names: Whether to include column names in the output
            header row.
        col_names: Explicit header names to write when provided.

    Returns:
        Dataset mapping each input file key to CSV text.

    Raises:
        Exception: Propagates serialization errors raised by pandas.

    Example:
        >>> csv_ds = convert_dataset_pandas_to_csv.run(pandas_dataset)
        >>> isinstance(csv_ds, Dataset)
        True
    """

    out_dataset = Dataset[Model[str]]()
    for key, df in dataset.items():
        csv_stream = StringIO()
        df.to_csv(
            csv_stream,
            sep=delimiter,
            header=col_names if col_names else True if first_row_as_col_names else False,
            encoding='utf8',
            index=False)
        out_dataset[key] = csv_stream.getvalue()
    return out_dataset


@TaskTemplate()
def extract_columns_as_files(dataset: PandasDataset, col_names: list[str]) -> PandasDataset:
    """Split selected columns into separate one-column files.

    Args:
        dataset: Input dataset with tabular files.
        col_names: Column names to extract into their own files.

    Returns:
        A new dataset containing modified original tables (without extracted
        columns) plus additional one-column files named ``<file>.<column>``.

    Raises:
        KeyError: If one or more requested columns do not exist in a file.

    Example:
        >>> out_ds = extract_columns_as_files.run(pandas_dataset, ['name'])
        >>> any(key.endswith('.name') for key in out_ds.keys())
        True
    """

    from .lazy_import import pd

    out_dataset = PandasDataset()
    for key, item in dataset.items():
        df = dataset[key]
        out_dataset[key] = df.loc[:, ~df.columns.isin(col_names)]

        for col_name in col_names:
            out_dataset[f'{key}.{col_name}'] = pd.DataFrame(df[col_name])
    return out_dataset


@TaskTemplate()
def concat_dataframes_across_datasets(dataset_list: ListOfPandasDatasetsWithSameNumberOfFiles,
                                      vertical=True) -> PandasDataset:
    """Concatenate aligned files across multiple pandas datasets.

    Args:
        dataset_list: List model containing at least two datasets with aligned
            file counts and ordering.
        vertical: When ``True``, concatenate by rows. When ``False``,
            concatenate by columns.

    Returns:
        A dataset whose files are concatenations of corresponding files from
        each input dataset.

    Raises:
        Exception: Propagates concatenation errors raised by pandas.

    Example:
        >>> combined = concat_dataframes_across_datasets.run(dataset_list)
        >>> isinstance(combined, PandasDataset)
        True
    """

    from .lazy_import import pd

    # We know from the data type that there are at least two datasets and that there is an equal
    # amount of files/DataFrames in each dataset. This simplifies implementation.

    out_dataset = PandasDataset()
    out_datafile_names = tuple(dataset_list[0].keys())
    for df_index in range(len(out_datafile_names)):
        df = pd.concat([tuple(dataset.values())[df_index] for dataset in dataset_list],
                       axis=0 if vertical else 1)
        out_dataset[out_datafile_names[df_index]] = df
    return out_dataset


@TaskTemplate()
def join_tables(table_1: PandasModel,
                table_2: PandasModel,
                join_type: str = 'outer',
                on_cols: Sequence[str] | Mapping[str, str] | None = None) -> PandasModel:
    """Join two tables by shared or explicitly mapped columns.

    Args:
        table_1: Left input table.
        table_2: Right input table.
        join_type: Join strategy. Supported values are ``inner``, ``outer``,
            ``left``, and ``right``.
        on_cols: Optional join columns. Provide a sequence for same-name
            columns or a mapping from left to right column names.

    Returns:
        A merged table wrapped in ``PandasModel``.

    Raises:
        ValueError: If ``join_type`` is ``cross`` or if no join columns can be
            determined.
        AssertionError: If ``join_type`` is not one of the supported values.

    Example:
        >>> joined = join_tables.run(left_table, right_table, join_type='inner', on_cols=['id'])
        >>> isinstance(joined, PandasModel)
        True
    """

    from .lazy_import import pd

    if join_type == 'cross':
        raise ValueError('join_type="cross" not supported. Please use "cartesian_product" task.')
    assert join_type in ['inner', 'outer', 'left', 'right']

    common_colnames = extract_common_colnames(table_1, table_2)

    if (on_cols is None and len(common_colnames) == 0) \
            or (on_cols is not None and len(on_cols) == 0):
        raise ValueError(f'No common column names were found. '
                         f'table_1: {tuple(table_1.columns)}. '
                         f'table_2: {tuple(table_2.columns)}. '
                         f'on_cols: {on_cols}')

    on = None
    left_on = None
    right_on = None

    if on_cols is None:
        on = common_colnames
    elif isinstance(on_cols, Mapping):
        left_on = tuple(on_cols.keys())
        right_on = tuple(on_cols.values())
    else:
        on = on_cols

    column_info = f'common columns: {on}' if on is not None \
        else f'column mappings: {tuple(on_cols.items())}'
    print(f'Joining tables on {column_info}, using join type: {join_type}...')

    merged_df = pd.merge(
        table_1.loc[:, :],
        table_2.loc[:, :],
        on=on,
        left_on=left_on,
        right_on=right_on,
        how=join_type,
        suffixes=('_1', '_2'),
    ).convert_dtypes()

    return PandasModel(merged_df)


@TaskTemplate()
def cartesian_product(table_1: PandasModel, table_2: PandasModel) -> PandasModel:
    """Return the cartesian product of two tables.

    Args:
        table_1: Left input table.
        table_2: Right input table.

    Returns:
        A ``PandasModel`` containing the cross join result.

    Raises:
        Exception: Propagates merge errors raised by pandas.

    Example:
        >>> result = cartesian_product.run(left_table, right_table)
        >>> isinstance(result, PandasModel)
        True
    """

    from .lazy_import import pd

    merged_df = pd.merge(
        table_1.loc[:, :],
        table_2.loc[:, :],
        how='cross',
        suffixes=('_1', '_2'),
    ).convert_dtypes()

    return PandasModel(merged_df)
