from typing import Any

import requests

from unifair import runtime
from unifair.compute.flow import FuncFlowTemplate
from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model
from unifair.modules.fairtracks.util import serialize_to_tarpacked_csv_files
from unifair.modules.json.models import JsonDataset, JsonDictOfAnyModel, JsonModel
from unifair.modules.json.tasks import (cast_dataset,
                                        split_all_nested_lists_from_dataset,
                                        transpose_dataset_of_dicts_to_lists,)
from unifair.modules.json.util import serialize_to_tarpacked_json_files
from unifair.modules.tables.models import JsonTableOfStrings

runtime.config.engine = 'local'
runtime.config.prefect.use_cached_results = False

transpose_dataset_of_dicts_to_lists = transpose_dataset_of_dicts_to_lists.apply()
cast_dataset_new = cast_dataset.refine(name="cast_dataset_copy").apply()
cast_dataset = cast_dataset.apply()
split_all_nested_lists_from_dataset = split_all_nested_lists_from_dataset.apply()


@TaskTemplate
def import_uniprot():
    HEADERS = {'accept': 'application/json'}
    api_url = 'https://rest.uniprot.org/uniprotkb/search?query=human%20cdc7'
    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        # dataset = JsonDataset
        dataset = Dataset[JsonModel]()
        dataset['uniprotkb'] = response.json()
        return dataset
    else:
        raise RuntimeError('No result found')


# @FuncFlowTemplate
# def uniprot():
#     uniprot_ds = import_uniprot()
#     uniprot_ds = cast_dataset(uniprot_ds, cast_model=JsonDictOfAnyModel)
#     uniprot_ds = transpose_dataset_of_dicts_to_lists(uniprot_ds)
#     uniprot_ds = extract_all_nested_lists(uniprot_ds)
#     return cast_to_table_of_strings_and_lists(uniprot_ds)
#

# @LinearFlowTemplate(
#     import_uniprot,
#     cast_dataset.refine(fixed_params=dict(
#         cast_model=JsonDictOfAnyModel)),  # should be made automatic
#     transpose_dataset_of_dicts_to_lists,
#     extract_all_nested_lists,
#     cast_dataset.refine(fixed_params=dict(
#         cast_model=JsonTableOfStrings)),  # should be made automatic
# )
# def uniprot() -> Dataset[JsonTableOfStrings]:
#     ...

import_uniprot = import_uniprot.apply()

# serialize_to_tarpacked_json_files('1_import_unipro', uniprot_dataset)

uniprot_1_ds = import_uniprot()
uniprot_2_ds = cast_dataset(uniprot_1_ds, cast_model=JsonDictOfAnyModel)
uniprot_3_ds = transpose_dataset_of_dicts_to_lists(uniprot_2_ds)
uniprot_4_ds = split_all_nested_lists_from_dataset(uniprot_3_ds)
uniprot_5_ds = cast_dataset_new(uniprot_4_ds, cast_model=JsonTableOfStrings)

# output
serialize_to_tarpacked_json_files('1_uniprot_per_infile_ds', uniprot_1_ds)
serialize_to_tarpacked_json_files('2_uniprot_per_infile_dict_ds', uniprot_2_ds)
serialize_to_tarpacked_json_files('3_uniprot_nested_list_ds', uniprot_3_ds)
serialize_to_tarpacked_json_files('4_uniprot_unnested_list_ds', uniprot_4_ds)
serialize_to_tarpacked_json_files('5_uniprot_tabular_json', uniprot_5_ds)
serialize_to_tarpacked_csv_files('6_uniprot_tabular', uniprot_5_ds)
