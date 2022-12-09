import os
from typing import List, Optional, Tuple

from unifair import runtime
from unifair.compute.flow import FuncFlowTemplate, LinearFlowTemplate
from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model
from unifair.modules.general.tasks import import_directory, split_dataset
from unifair.modules.json.util import serialize_to_tarpacked_json_files
from unifair.modules.pandas.models import PandasDataset
from unifair.modules.pandas.tasks import (concat_dataframes_across_datasets,
                                          extract_columns_as_files,
                                          from_csv,
                                          to_csv)
from unifair.modules.pandas.util import serialize_to_tarpacked_csv_files
from unifair.modules.raw.tasks import modify_all_lines, modify_datafile_contents, modify_each_line
from unifair.modules.raw.util import serialize_to_tarpacked_raw_files
from unifair.modules.tables.models import JsonTableOfStrings

runtime.config.engine = 'local'
runtime.config.prefect.use_cached_results = False

# Tasks


def slice_lines(all_lines: List[str],
                start: Optional[int] = None,
                end: Optional[int] = None) -> List[str]:
    return all_lines[start:end]


slice_lines = modify_all_lines.refine(
    name='slice_lines',
    fixed_params=dict(modify_all_lines_func=slice_lines),
)


def transform_attr_line_to_json(_line_no: int, line: str) -> str:
    items = [item.strip().split('=') for item in line.strip().split(';') if item]
    json_obj_items = [f'"{key}": "{val}"' for key, val in items]
    return f'{{{", ".join(json_obj_items)}}},' + os.linesep


transform_all_lines_to_json = modify_each_line.refine(
    name='transform_all_lines_to_json',
    fixed_params=dict(modify_line_func=transform_attr_line_to_json),
)

transform_datafile_start_and_end_to_json = modify_datafile_contents.refine(
    name='transform_datafile_start_and_end_to_json',
    fixed_params=dict(modify_contents_func=lambda x: f'[{x[:-2]}]'),
)  # Brackets + strip comma and newline from end

# Constants

GFF_COLS = ['seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes']
ATTRIB_COL = GFF_COLS[-1]

# Functions


def attrib_df_names(dataset: Dataset[Model[object]]) -> List[str]:
    return [name for name in dataset.keys() if name.endswith(ATTRIB_COL)]


# Flow
@FuncFlowTemplate
def convert_gff_files(data: Dataset[Model[str]]) -> PandasDataset:
    data = import_directory('input/gff', suffix='.gff', model=Model[str])
    serialize_to_tarpacked_raw_files('1_data', data)

    data_2 = slice_lines(data, start=0, end=1000)
    serialize_to_tarpacked_raw_files('2_data', data_2)

    pd_data_3 = from_csv(data_2, delimiter='\t', first_row_as_col_names=False, col_names=GFF_COLS)
    serialize_to_tarpacked_csv_files('3_pd_data', pd_data_3)

    pd_data_4 = extract_columns_as_files(pd_data_3, [ATTRIB_COL])
    serialize_to_tarpacked_csv_files('4_pd_data', pd_data_4)

    pd_data_5_main, pd_data_3_attrib = split_dataset(pd_data_4, attrib_df_names(pd_data_4))
    serialize_to_tarpacked_csv_files('5_pd_data_main', pd_data_5_main)

    data_6_attrib = to_csv(pd_data_3_attrib, first_row_as_col_names=False)
    serialize_to_tarpacked_raw_files('6_raw_data_attributes', data_6_attrib)

    data_7_attrib = transform_all_lines_to_json(data_6_attrib)
    serialize_to_tarpacked_raw_files('7_raw_data_attributes', data_7_attrib)

    data_8_attrib = transform_datafile_start_and_end_to_json(data_7_attrib)
    serialize_to_tarpacked_raw_files('8_raw_data_attributes', data_8_attrib)

    data_9_attrib = Dataset[JsonTableOfStrings]()
    data_9_attrib.from_json(data_8_attrib.to_data())
    serialize_to_tarpacked_json_files('9_json_data_attributes', data_9_attrib)

    pd_data_7_attrib = PandasDataset()
    pd_data_7_attrib.from_data(data_9_attrib.to_data())

    pd_data_10 = concat_dataframes_across_datasets(
        [pd_data_5_main, pd_data_7_attrib],
        vertical=False,
    )
    serialize_to_tarpacked_csv_files('10_pd_data', pd_data_10)
    return pd_data_10


@FuncFlowTemplate
def import_gff_and_convert_to_pandas() -> PandasDataset:
    data: Dataset[Model[str]] = import_directory('input/gff', suffix='.gff', model=Model[str])
    return convert_gff_files(data)


import_gff_and_convert_to_pandas.run()
