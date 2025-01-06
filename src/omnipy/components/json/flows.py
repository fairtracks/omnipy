from omnipy.compute.flow import FuncFlowTemplate

from .constants import DEFAULT_KEY, ID_KEY, REF_KEY
from .datasets import (JsonDictOfDictsDataset,
                       JsonDictOfListsOfDictsDataset,
                       JsonListOfDictsDataset,
                       JsonListOfDictsOfScalarsDataset)
from .tasks import _flatten_outer_level_of_all_data_files, transpose_dicts_2_lists


@FuncFlowTemplate(fixed_params=dict(id_key=ID_KEY, ref_key=REF_KEY, default_key=DEFAULT_KEY))
def flatten_nested_json(
    dataset: JsonListOfDictsDataset,
    id_key: str,
    ref_key: str,
    default_key: str,
) -> JsonListOfDictsOfScalarsDataset:
    all_data_files_of_scalar_records_ds = JsonListOfDictsOfScalarsDataset()
    data_files_of_any_ds = dataset

    while len(data_files_of_any_ds) > 0:
        data_files_of_scalar_records_ds, data_files_of_any_ds = \
            _flatten_outer_level_of_all_data_files(
                data_files_of_any_ds, id_key, ref_key, default_key)

        all_data_files_of_scalar_records_ds |= data_files_of_scalar_records_ds

    return all_data_files_of_scalar_records_ds


@FuncFlowTemplate()
def transpose_dict_of_dicts_2_list_of_dicts(
    dataset: JsonDictOfDictsDataset,
    id_key: str = ID_KEY,
) -> JsonListOfDictsDataset:
    output_dataset = JsonListOfDictsDataset()
    output_dataset |= transpose_dicts_2_lists(dataset, id_key=id_key)
    return output_dataset


@FuncFlowTemplate()
def transpose_dicts_of_lists_of_dicts_2_lists_of_dicts(
    dataset: JsonDictOfListsOfDictsDataset,
    id_key: str = ID_KEY,
) -> JsonListOfDictsDataset:
    output_dataset = JsonListOfDictsDataset()
    output_dataset |= transpose_dicts_2_lists(dataset, id_key=id_key)
    return output_dataset
