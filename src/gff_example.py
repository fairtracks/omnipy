import os
from typing import List, Optional

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

# TaskTemplates


def slice_lines(all_lines: List[str],
                start: Optional[int] = None,
                end: Optional[int] = None) -> List[str]:
    return all_lines[start:end]


slice_lines = modify_all_lines.refine(
    name='slice_lines',
    fixed_params=dict(modify_all_lines_func=slice_lines),
)


def transform_attr_line_to_json(_line_no: int, line: str) -> str:
    items = [item.split('=') for item in line.strip().split(';')]
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

data = import_directory.run('input/gff', suffix='.gff', model=Model[str])
data_2 = slice_lines.run(data, start=0, end=1000)

pd_data = from_csv.run(data_2, delimiter='\t', first_row_as_col_names=False, col_names=GFF_COLS)
pd_data_2 = extract_columns_as_files.run(pd_data, [ATTRIB_COL])
pd_data_3_main, pd_data_3_attrib = split_dataset.run(pd_data_2, attrib_df_names(pd_data_2))

data_4_attrib = to_csv.run(pd_data_3_attrib, first_row_as_col_names=False)
data_5_attrib = transform_all_lines_to_json.run(data_4_attrib)
data_6_attrib = transform_datafile_start_and_end_to_json.run(data_5_attrib)

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
