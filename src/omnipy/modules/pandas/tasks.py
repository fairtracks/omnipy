from io import StringIO
from typing import Dict, List, Optional

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from . import pd
from ..general.models import NotIteratorExceptStrings
from .models import ListOfPandasDatasetsWithSameNumberOfFiles, PandasDataset


@TaskTemplate
def convert_dataset_list_of_dicts_to_pandas(
        dataset: Dataset[Model[List[Dict[str, NotIteratorExceptStrings]]]]) -> PandasDataset:
    pandas_dataset = PandasDataset()
    pandas_dataset.from_data(dataset.to_data())
    return pandas_dataset


@TaskTemplate()
def convert_dataset_csv_to_pandas(dataset: Dataset[Model[bytes]],
                                  delimiter: str = ',',
                                  first_row_as_col_names=True,
                                  col_names: Optional[List[str]] = None,
                                  ignore_comments: bool = True,
                                  comments_char: str = '#') -> PandasDataset:
    out_dataset = PandasDataset()
    for key, item in dataset.items():
        df = pd.read_csv(
            StringIO(item),
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
    col_names: Optional[List[str]] = None,
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


@TaskTemplate()
def extract_columns_as_files(dataset: PandasDataset, col_names: List[str]) -> PandasDataset:
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
    # We know from the data type that there are at least two datasets and that there is an equal
    # amount of files/DataFrames in each dataset. This simplifies implementation.

    out_dataset = PandasDataset()
    out_datafile_names = tuple(dataset_list[0].keys())
    for df_index in range(len(out_datafile_names)):
        df = pd.concat([tuple(dataset.values())[df_index] for dataset in dataset_list],
                       axis=0 if vertical else 1)
        out_dataset[out_datafile_names[df_index]] = df
    return out_dataset
