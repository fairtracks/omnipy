from io import StringIO
from typing import Mapping, Sequence

from omnipy.compute.task import TaskTemplate
from omnipy.compute.typing import mypy_fix_task_template
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from . import pd
from ..general.models import NotIterableExceptStrOrBytesModel
from .helpers import extract_common_colnames
from .models import ListOfPandasDatasetsWithSameNumberOfFiles, PandasDataset, PandasModel


@mypy_fix_task_template
@TaskTemplate()
def convert_dataset_list_of_dicts_to_pandas(
        dataset: Dataset[Model[list[dict[str, NotIterableExceptStrOrBytesModel]]]]) \
        -> PandasDataset:
    pandas_dataset = PandasDataset()
    pandas_dataset.from_data(dataset.to_data())
    return pandas_dataset


@mypy_fix_task_template
@TaskTemplate()
def convert_dataset_csv_to_pandas(dataset: Dataset[Model[bytes]],
                                  delimiter: str = ',',
                                  first_row_as_col_names=True,
                                  col_names: list[str] | None = None,
                                  ignore_comments: bool = True,
                                  comments_char: str = '#') -> PandasDataset:
    out_dataset = PandasDataset()
    for key, item in dataset.items():
        df = pd.read_csv(
            StringIO(item.contents),
            sep=delimiter,
            header='infer' if first_row_as_col_names else 0,
            names=col_names,
            comment=comments_char if ignore_comments else None,
            encoding='utf8',
        )
        out_dataset[key] = df
    return out_dataset


@mypy_fix_task_template
@TaskTemplate()
def convert_dataset_pandas_to_csv(
    dataset: PandasDataset,
    delimiter: str = ',',
    first_row_as_col_names=True,
    col_names: list[str] | None = None,
) -> Dataset[Model[str]]:
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


@mypy_fix_task_template
@TaskTemplate()
def extract_columns_as_files(dataset: PandasDataset, col_names: list[str]) -> PandasDataset:
    out_dataset = PandasDataset()
    for key, item in dataset.items():
        df = dataset[key]
        out_dataset[key] = df.loc[:, ~df.columns.isin(col_names)]

        for col_name in col_names:
            out_dataset[f'{key}.{col_name}'] = pd.DataFrame(df[col_name])
    return out_dataset


@mypy_fix_task_template
@TaskTemplate()
def concat_dataframes_across_datasets(dataset_list: ListOfPandasDatasetsWithSameNumberOfFiles,
                                      vertical=True) -> PandasDataset:
    # We know from the data type that there are at least two datasets and that there is an equal
    # amount of files/DataFrames in each dataset. This simplifies implementation.

    out_dataset = PandasDataset()
    out_datafile_names = tuple(dataset_list[0].keys())
    for df_index in range(len(out_datafile_names)):
        df = pd.concat([tuple(dataset.values())[df_index] for dataset in dataset_list],
                       axis=0 if vertical else 1)
        out_dataset[out_datafile_names[df_index]] = df
    return out_dataset


@mypy_fix_task_template
@TaskTemplate()
def join_tables(table_1: PandasModel,
                table_2: PandasModel,
                join_type: str = 'outer',
                on_cols: Sequence[str] | Mapping[str, str] | None = None) -> PandasModel:
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


@mypy_fix_task_template
@TaskTemplate()
def cartesian_product(table_1: PandasModel, table_2: PandasModel) -> PandasModel:
    merged_df = pd.merge(
        table_1.loc[:, :],
        table_2.loc[:, :],
        how='cross',
        suffixes=('_1', '_2'),
    ).convert_dtypes()

    return PandasModel(merged_df)
