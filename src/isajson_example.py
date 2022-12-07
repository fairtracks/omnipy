from unifair import runtime
from unifair.modules.general.tasks import cast_dataset
from unifair.modules.json.models import JsonDictOfAnyModel
from unifair.modules.json.tasks import import_directory
from unifair.modules.json.util import serialize_to_tarpacked_json_files
from unifair.modules.pandas.util import serialize_to_tarpacked_csv_files
from unifair.modules.tables.models import JsonTableOfStrings
from unifair.modules.tables.tasks import (flatten_nested_json_to_list_of_dicts,
                                          transpose_dataset_of_dicts_to_lists)

runtime.config.engine = 'local'
runtime.config.prefect.use_cached_results = False

cast_to_json_dict_of_any = cast_dataset.refine(
    name='cast_to_json_dict_of_any', fixed_params=dict(cast_model=JsonDictOfAnyModel))
cast_to_table_of_strings_and_lists = cast_dataset.refine(
    name='cast_to_table_of_strings_and_lists', fixed_params=dict(cast_model=JsonTableOfStrings))

# Workflow
isa_json_per_infile_ds = import_directory.run(directory='input/isa-json')
isa_json_per_infile_dict_ds = cast_to_json_dict_of_any.run(isa_json_per_infile_ds)
isa_json_nested_list_ds = transpose_dataset_of_dicts_to_lists.run(isa_json_per_infile_dict_ds)
isa_json_unnested_list_ds = flatten_nested_json_to_list_of_dicts.run(isa_json_nested_list_ds)
isa_json_tabular = cast_to_table_of_strings_and_lists.run(isa_json_unnested_list_ds)

# output
serialize_to_tarpacked_json_files('1_isa_json_per_infile_ds', isa_json_per_infile_ds)
serialize_to_tarpacked_json_files('2_isa_json_per_infile_dict_ds', isa_json_per_infile_dict_ds)
serialize_to_tarpacked_json_files('3_isa_json_nested_list_ds', isa_json_nested_list_ds)
serialize_to_tarpacked_json_files('4_isa_json_unnested_list_ds', isa_json_unnested_list_ds)
serialize_to_tarpacked_json_files('5_isa_json_tabular_json', isa_json_tabular)

serialize_to_tarpacked_csv_files('6_isa_json_tabular_csv', isa_json_tabular)
