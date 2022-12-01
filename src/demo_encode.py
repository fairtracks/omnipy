from unifair.compute.flow import FuncFlowTemplate
from unifair.config.runtime import Runtime
from unifair.modules.fairtracks.tasks import import_dataset_from_encode
from unifair.modules.fairtracks.util import serialize_to_tarpacked_csv_files
from unifair.modules.json.models import JsonDictOfAnyModel
from unifair.modules.json.tasks import cast_dataset, split_all_nested_lists_from_dataset
from unifair.modules.json.util import serialize_to_tarpacked_json_files
from unifair.modules.tables.tasks import remove_columns

runtime = Runtime()
runtime.config.engine = 'local'
runtime.config.prefect.use_cached_results = False

# Temporarily, as flow support are not finalized
import_some_data_from_encode = import_dataset_from_encode.refine(
    name='import_some_data_from_encode',).apply()

# cast_to_dict_on_top = cast_dataset.refine(
#     name='cast_to_dict_on_top',
#     fixed_params=dict(cast_model=JsonDictOfAnyModel),
# ).apply()
split_all_nested_lists = split_all_nested_lists_from_dataset.refine(
    name='split_all_nested_lists').apply()

remove_columns = remove_columns.apply()

encode_json = import_some_data_from_encode(
    endpoints=[
        'experiment',
        'biosample',
    ],
    max_data_item_count=25,
)
# encode_json_pruned = remove_columns(
#     encode_json, column_keys_for_data_items=dict(
#         experiment=['audit'],
#         biosample=['audit'],
#     ))
# encode_json_dict = cast_to_dict_on_top(encode_json)
splitted_encode_json = split_all_nested_lists(encode_json)

serialize_to_tarpacked_json_files('encode_json', encode_json)
serialize_to_tarpacked_json_files('splitted_encode_json', splitted_encode_json)
# serialize_to_tarpacked_csv_files('encode_json', encode_json)
serialize_to_tarpacked_csv_files('splitted_encode_csv', splitted_encode_json)
# serialize_to_tarpacked_csv_files('encode_json_pruned', encode_json_pruned)

# runtime = Runtime()
# runtime.config.engine = 'prefect'
# runtime.config.prefect.use_cached_results = True
#
#
# @FuncFlowTemplate
# def import_encode_data_tmpl():
#     encode_json = import_dataset_from_encode(
#         endpoints=[
#             'experiment',
#             'biosample',
#         ],
#         max_data_item_count=25,
#         serialize_as='csv',
#     )
#     encode_json_pruned = remove_columns(
#         encode_json,
#         column_keys_for_data_items=dict(
#             experiment=['audit'],
#             biosample=['audit'],
#         ),
#         serialize_as='csv',
#     )
#     return encode_json_pruned
#
#
# import_encode_data = import_encode_data_tmpl.apply()
# import_encode_data()
