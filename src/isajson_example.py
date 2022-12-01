import os
from typing import cast

from unifair.compute.flow import FuncFlowTemplate
from unifair.config.runtime import Runtime
from unifair.data.dataset import Dataset
from unifair.data.model import Model
from unifair.modules.fairtracks.util import serialize_to_tarpacked_csv_files
from unifair.modules.json.models import (JsonDataset,
                                         JsonDict,
                                         JsonDictOfAnyModel,
                                         JsonListOfNestedDictsModel,
                                         JsonModel,
                                         JsonType)
from unifair.modules.json.tasks import (cast_dataset,
                                        import_directory,
                                        split_all_nested_lists_from_dataset,
                                        transpose_dataset_of_dicts_to_lists)
from unifair.modules.json.util import serialize_to_tarpacked_json_files
from unifair.modules.tables.models import JsonTableOfStrings, TableOfStrings, TableOfStringsAndLists

# from unifair.modules.tables.tasks import remove_columns

runtime = Runtime()
runtime.config.engine = 'local'
runtime.config.prefect.use_cached_results = False

cast_to_json_dict_of_any = cast_dataset.refine(
    name='cast_to_json_dict_of_any', fixed_params=dict(cast_model=JsonDictOfAnyModel)).apply()
cast_to_table_of_strings_and_lists = cast_dataset.refine(
    name='cast_to_table_of_strings_and_lists',
    fixed_params=dict(cast_model=JsonTableOfStrings)).apply()
import_data_from_dir = import_directory.refine(name='import_data_from_dir').apply()
transpose_dataset_of_dicts_to_lists = transpose_dataset_of_dicts_to_lists.apply()
extract_all_nested_lists = split_all_nested_lists_from_dataset.apply()

# Workflow
isa_json_per_infile_ds = import_data_from_dir(directory='input/isa-json')
isa_json_per_infile_dict_ds = cast_to_json_dict_of_any(isa_json_per_infile_ds)
isa_json_nested_list_ds = transpose_dataset_of_dicts_to_lists(isa_json_per_infile_dict_ds)
isa_json_unnested_list_ds = extract_all_nested_lists(isa_json_nested_list_ds)
isa_json_tabular = cast_to_table_of_strings_and_lists(isa_json_unnested_list_ds)

# output
serialize_to_tarpacked_json_files('isa_json_per_infile_ds', isa_json_per_infile_ds)
serialize_to_tarpacked_json_files('isa_json_per_infile_dict_ds', isa_json_per_infile_dict_ds)
serialize_to_tarpacked_json_files('isa_json_nested_list_ds', isa_json_nested_list_ds)
serialize_to_tarpacked_json_files('isa_json_unnested_list_ds', isa_json_unnested_list_ds)
serialize_to_tarpacked_json_files('isa_json_tabular_json', isa_json_tabular)

serialize_to_tarpacked_csv_files('isa_json_tabular_csv', isa_json_tabular)
