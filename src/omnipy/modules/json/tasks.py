from collections import defaultdict
from typing import cast

from omnipy.compute.flow import FuncFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.compute.typing import mypy_fix_func_flow_template, mypy_fix_task_template
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from .datasets import (JsonDataset,
                       JsonDictDataset,
                       JsonDictOfDictsDataset,
                       JsonDictOfListsOfDictsDataset,
                       JsonListDataset,
                       JsonListOfDictsDataset,
                       JsonListOfDictsOfScalarsDataset)
from .functions import flatten_outer_level_of_nested_record
from .models import JsonListModel
from .typedefs import (JsonDictOfListsOfDicts,
                       JsonDictOfScalars,
                       JsonListOfDicts,
                       JsonListOfDictsOfScalars)

ID_KEY = '_omnipy_id'
REF_KEY = '_omnipy_ref'
DEFAULT_KEY = '__root__'


@mypy_fix_task_template
@TaskTemplate()
def convert_dataset_string_to_json(dataset: Dataset[Model[str]]) -> JsonDataset:
    json_dataset = JsonDataset()
    json_dataset.from_json(dataset.to_data())
    return json_dataset


@mypy_fix_task_template
@TaskTemplate()
def transpose_dicts_2_lists(dataset: JsonDictDataset, id_key: str = ID_KEY) -> JsonListDataset:
    output_dataset = JsonListDataset()

    for name, item in dataset.items():
        for key, val in item.items():
            if key not in output_dataset:
                output_dataset[key] = []

            if not val.outer_type() == list:
                val = JsonListModel([val])

            for item_index, val_item in enumerate(val):
                if val_item.outer_type() == dict:
                    output_dataset[key].append({id_key: f'{name}_{item_index}'})
                    assert id_key not in val_item
                    output_dataset[key][-1] |= val_item
                else:
                    output_dataset[key].append(val_item)

    return output_dataset


@mypy_fix_func_flow_template
@FuncFlowTemplate()
def transpose_dict_of_dicts_2_list_of_dicts(
    dataset: JsonDictOfDictsDataset,
    id_key: str = ID_KEY,
) -> JsonListOfDictsDataset:
    output_dataset = JsonListOfDictsDataset()
    output_dataset |= transpose_dicts_2_lists(dataset, id_key=id_key)
    return output_dataset


@mypy_fix_func_flow_template
@FuncFlowTemplate()
def transpose_dicts_of_lists_of_dicts_2_lists_of_dicts(
    dataset: JsonDictOfListsOfDictsDataset,
    id_key: str = ID_KEY,
) -> JsonListOfDictsDataset:
    output_dataset = JsonListOfDictsDataset()
    output_dataset |= transpose_dicts_2_lists(dataset, id_key=id_key)
    return output_dataset


@mypy_fix_task_template
@TaskTemplate()
def flatten_outer_level_of_all_data_files(
        dataset: JsonListOfDictsDataset, id_key: str, ref_key: str,
        default_key: str) -> tuple[JsonListOfDictsOfScalarsDataset, JsonListOfDictsDataset]:

    data_files_of_scalar_records: defaultdict[str, JsonListOfDictsOfScalars] = \
        defaultdict(JsonListOfDictsOfScalars)
    data_files_of_any: defaultdict[str, JsonListOfDicts] = defaultdict(JsonListOfDicts)

    dataset_as_data: JsonDictOfListsOfDicts = \
        cast(JsonDictOfListsOfDicts, dataset.to_data())

    for data_file_title, item in dataset_as_data.items():
        data_file: JsonListOfDicts = item

        if len(data_file) == 0:
            data_files_of_scalar_records[data_file_title] = JsonListOfDictsOfScalars()

        for record_id, nested_record in enumerate(data_file):
            record_of_scalars: JsonDictOfScalars
            new_data_files_of_any: JsonDictOfListsOfDicts
            record_of_scalars, new_data_files_of_any = flatten_outer_level_of_nested_record(
                nested_record,
                str(record_id),
                data_file_title,
                id_key,
                ref_key,
                default_key,
            )

            new_data_file_title: str
            new_data_file_of_any: JsonListOfDicts
            for new_data_file_title, new_data_file_of_any in new_data_files_of_any.items():
                data_files_of_any[new_data_file_title] += new_data_file_of_any
            data_files_of_scalar_records[data_file_title].append(record_of_scalars)

    data_files_of_scalar_records_ds = JsonListOfDictsOfScalarsDataset(data_files_of_scalar_records)
    data_files_of_any_ds = JsonListOfDictsDataset(data_files_of_any)

    return data_files_of_scalar_records_ds, data_files_of_any_ds
