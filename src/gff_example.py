from io import StringIO
import os
from typing import Any, List, Optional, Tuple

from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model
from unifair.modules.fairtracks.util import (serialize_to_tarpacked_csv_files,
                                             serialize_to_tarpacked_raw_files)
from unifair.modules.json.util import serialize_to_tarpacked_json_files
from unifair.modules.pandas import pd
from unifair.modules.pandas.models import PandasDataset
from unifair.modules.raw.tasks import (import_directory,
                                       modify_all_lines,
                                       modify_datafile_contents,
                                       modify_each_line)
from unifair.modules.tables.models import JsonTableOfStrings


@TaskTemplate
def from_csv(dataset: Dataset[Model[bytes]],
             delimiter: str = ',',
             first_row_as_col_names=True,
             col_names: Optional[List[str]] = None,
             ignore_comments: bool = True,
             comments_char: str = '#') -> PandasDataset:
    for key, item in dataset.items():
        out_dataset = PandasDataset()
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


@TaskTemplate
def to_csv(
    dataset: PandasDataset,
    delimiter: str = ',',
    first_row_as_col_names=True,
    col_names: Optional[List[str]] = None,
) -> Dataset[Model[str]]:
    for key, df in dataset.items():
        out_dataset = Dataset[Model[str]]()
        csv_stream = StringIO()
        df.to_csv(
            csv_stream,
            sep=delimiter,
            header=col_names if col_names else True if first_row_as_col_names else False,
            encoding='utf8',
            index=False)
        out_dataset[key] = csv_stream.getvalue()
    return out_dataset


@TaskTemplate
def extract_columns_as_files(dataset: PandasDataset, col_names: List[str]) -> PandasDataset:
    out_dataset = PandasDataset()
    for key, item in dataset.items():
        df = dataset[key]
        out_dataset[key] = df.loc[:, ~df.columns.isin(col_names)]

        for col_name in col_names:
            out_dataset[f'{key}.{col_name}'] = pd.DataFrame(df[col_name])
    return out_dataset


def slice_lines(all_lines: List[str],
                start: Optional[int] = None,
                end: Optional[int] = None) -> List[str]:
    return all_lines[start:end]


slice_lines = modify_all_lines.refine(
    name='slice_lines', fixed_params=dict(modify_all_lines_func=slice_lines))


@TaskTemplate
def split_dataset(
        dataset: Dataset[Model[object]],
        datafile_names_for_b: List[str]) -> Tuple[Dataset[Model[object]], Dataset[Model[object]]]:
    model_cls = dataset.get_model_class()
    datafile_names_for_a = set(dataset.keys()) - set(datafile_names_for_b)
    dataset_a = Dataset[model_cls]({name: dataset[name] for name in datafile_names_for_a})
    dataset_b = Dataset[model_cls]({name: dataset[name] for name in datafile_names_for_b})
    return dataset_a, dataset_b


class ListOfPandasDatasetsWithSameNumberOfFiles(Model[List[PandasDataset]]):
    @classmethod
    def _parse_data(cls, dataset_list: List[PandasDataset]) -> Any:
        assert len(dataset_list) >= 2
        assert all(len(dataset) for dataset in dataset_list)


@TaskTemplate
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


GFF_COLS = ['seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes']
ATTRIB_COL = GFF_COLS[-1]


def attrib_df_names(dataset: Dataset[Model[object]]) -> List[str]:
    return [name for name in dataset.keys() if name.endswith(ATTRIB_COL)]


def transform_attr_line_to_json(_line_no: int, line: str) -> str:
    items = [item.split('=') for item in line.strip().split(';')]
    json_obj_items = [f'"{key}": "{val}"' for key, val in items]
    return f'{{{", ".join(json_obj_items)}}},' + os.linesep


data = import_directory.run('input/gff', suffix='.gff', model=Model[str])
data_2 = slice_lines.run(data, start=0, end=1000)

pd_data = from_csv.run(data_2, delimiter='\t', first_row_as_col_names=False, col_names=GFF_COLS)
pd_data_2 = extract_columns_as_files.run(pd_data, [ATTRIB_COL])
pd_data_3_main, pd_data_3_attrib = split_dataset.run(pd_data_2, attrib_df_names(pd_data_2))

data_4_attrib = to_csv.run(pd_data_3_attrib, first_row_as_col_names=False)
data_5_attrib = modify_each_line.run(data_4_attrib, transform_attr_line_to_json)
data_6_attrib = modify_datafile_contents.run(data_5_attrib, lambda x: f'[{x[:-2]}]')

data_7_attrib = Dataset[JsonTableOfStrings]()
data_7_attrib.from_json(data_6_attrib.to_data())

pd_data_7_attrib = PandasDataset()
pd_data_7_attrib.from_data(data_7_attrib.to_data())

pd_data_8 = concat_dataframes_across_datasets.run(
    [pd_data_3_main, pd_data_7_attrib],
    vertical=False,
)

serialize_to_tarpacked_csv_files('1_pd_data', pd_data)
serialize_to_tarpacked_csv_files('2_pd_data', pd_data_2)
serialize_to_tarpacked_csv_files('3_pd_data_main', pd_data_3_main)
serialize_to_tarpacked_raw_files('4_raw_data_attributes', data_4_attrib)
serialize_to_tarpacked_raw_files('5_raw_data_attributes', data_5_attrib)
serialize_to_tarpacked_raw_files('6_raw_data_attributes', data_6_attrib)
serialize_to_tarpacked_json_files('7_json_data_attributes', data_7_attrib)
serialize_to_tarpacked_csv_files('8_pd_data', pd_data_8)
