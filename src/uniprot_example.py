from typing import Any

import requests

from unifair import runtime
from unifair.compute.flow import FuncFlowTemplate
from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset
from unifair.data.model import Model
from unifair.modules.general.tasks import cast_dataset
from unifair.modules.json.models import JsonDataset, JsonDictOfAnyModel, JsonModel
from unifair.modules.json.util import serialize_to_tarpacked_json_files
from unifair.modules.pandas.models import PandasDataset
from unifair.modules.pandas.util import serialize_to_tarpacked_csv_files
from unifair.modules.tables.models import JsonTableOfStrings
from unifair.modules.tables.tasks import (flatten_nested_json_to_list_of_dicts,
                                          transpose_dataset_of_dicts_to_lists)

runtime.config.engine = 'local'
runtime.config.prefect.use_cached_results = False


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

# serialize_to_tarpacked_json_files('1_import_unipro', uniprot_dataset)

uniprot_1_ds = import_uniprot.run()
uniprot_2_ds = cast_dataset.run(uniprot_1_ds, cast_model=JsonDictOfAnyModel)
uniprot_3_ds = transpose_dataset_of_dicts_to_lists.run(uniprot_2_ds)
uniprot_4_ds = flatten_nested_json_to_list_of_dicts.run(uniprot_3_ds)
uniprot_5_ds = cast_dataset.refine(name="cast_dataset_copy").run(
    uniprot_4_ds, cast_model=JsonTableOfStrings)


@TaskTemplate
def to_pandas(dataset: Dataset[JsonTableOfStrings]) -> PandasDataset:
    pandas = PandasDataset()
    pandas.from_data(dataset.to_data())
    return pandas


uniprot_6_ds = to_pandas.run(uniprot_5_ds)


@TaskTemplate
def pandas_magic(pandas: PandasDataset) -> PandasDataset:
    df = pandas['results.genes.synonyms']
    df['_unifair_ref'] = df['_unifair_ref'].str.strip('results.genes.')
    out_dataset = PandasDataset()
    out_dataset['my_table'] = df
    return out_dataset


# @TaskTemplate
# def join_a_with_b(pandas_ds: PandasDataset,
#                   table_a_name: str,
#                   a_ref_column: str,
#                   table_b_name: str,
#                   b_id_column: str,
#                   join_table_name: str) -> PandasDataset:
#     ...
#
#
# join_a_with_b(uniprot_6_ds,
#               'results.genes.synonyms',
#               '_unifair_ref',
#               'results.genes',
#               '_unifair_id',
#               'merged_table')

uniprot_7_ds = pandas_magic.run(uniprot_6_ds)

# output
serialize_to_tarpacked_json_files('1_uniprot_per_infile_ds', uniprot_1_ds)
serialize_to_tarpacked_json_files('2_uniprot_per_infile_dict_ds', uniprot_2_ds)
serialize_to_tarpacked_json_files('3_uniprot_nested_list_ds', uniprot_3_ds)
serialize_to_tarpacked_json_files('4_uniprot_unnested_list_ds', uniprot_4_ds)
serialize_to_tarpacked_json_files('5_uniprot_tabular_json', uniprot_5_ds)
serialize_to_tarpacked_csv_files('6_uniprot_tabular_csv', uniprot_5_ds)

serialize_to_tarpacked_csv_files('7_output_csv', uniprot_7_ds)
# results
#     uniProtkbId
#     primaryAccession
# results.keywords
#     name
# results.gene.synonyms
#     value
