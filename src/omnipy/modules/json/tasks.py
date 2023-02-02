from collections import defaultdict
from typing import cast, Tuple

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.modules.json.datasets import (JsonDataset,
                                          JsonDictOfAnyDataset,
                                          JsonListOfDictsOfAnyDataset,
                                          JsonListOfDictsOfScalarsDataset)
from omnipy.modules.json.functions import flatten_outer_level_of_nested_record
from omnipy.modules.json.types import (JsonDictOfListsOfDictsOfAny,
                                       JsonDictOfScalars,
                                       JsonListOfDictsOfAny,
                                       JsonListOfDictsOfScalars)

ID_KEY = '_omnipy_id'
REF_KEY = '_omnipy_ref'
DEFAULT_KEY = '__root__'


@TaskTemplate()
def convert_dataset_string_to_json(dataset: Dataset[Model[str]]) -> JsonDataset:
    json_dataset = JsonDataset()
    json_dataset.from_json(dataset.to_data())
    return json_dataset


@TaskTemplate()
def transpose_dataset_of_dicts_to_lists(dataset: JsonDictOfAnyDataset,
                                        id_key: str = ID_KEY) -> JsonListOfDictsOfAnyDataset:
    output_dataset = JsonListOfDictsOfAnyDataset()
    output_data = defaultdict(list)

    for name, item in dataset.items():
        for key, val in item.to_data().items():
            if not isinstance(val, list):
                val = [val]

            for item_index, val_item in enumerate(val):
                if isinstance(val_item, dict):
                    data = {id_key: f'{name}_{item_index}'}
                    assert id_key not in val_item
                    data |= val_item
                else:
                    data = val_item
                output_data[key].append(data)
    output_dataset |= output_data.items()
    return output_dataset


@TaskTemplate()
def flatten_outer_level_of_all_data_files(
        dataset: JsonListOfDictsOfAnyDataset, id_key: str, ref_key: str,
        default_key: str) -> Tuple[JsonListOfDictsOfScalarsDataset, JsonListOfDictsOfAnyDataset]:

    data_files_of_scalar_records: defaultdict[str, JsonListOfDictsOfScalars] = \
        defaultdict(JsonListOfDictsOfScalars)
    data_files_of_any: defaultdict[str, JsonListOfDictsOfAny] = defaultdict(JsonListOfDictsOfAny)

    dataset_as_data: JsonDictOfListsOfDictsOfAny = \
        cast(JsonDictOfListsOfDictsOfAny, dataset.to_data())

    for data_file_title, item in dataset_as_data.items():
        data_file: JsonListOfDictsOfAny = item

        if len(data_file) == 0:
            data_files_of_scalar_records[data_file_title] = JsonListOfDictsOfScalars()

        for record_id, nested_record in enumerate(data_file):
            record_of_scalars: JsonDictOfScalars
            new_data_files_of_any: JsonDictOfListsOfDictsOfAny
            record_of_scalars, new_data_files_of_any = flatten_outer_level_of_nested_record(
                nested_record,
                str(record_id),
                data_file_title,
                id_key,
                ref_key,
                default_key,
            )

            new_data_file_title: str
            new_data_file_of_any: JsonListOfDictsOfAny
            for new_data_file_title, new_data_file_of_any in new_data_files_of_any.items():
                data_files_of_any[new_data_file_title] += new_data_file_of_any
            data_files_of_scalar_records[data_file_title].append(record_of_scalars)

    data_files_of_scalar_records_ds = JsonListOfDictsOfScalarsDataset(data_files_of_scalar_records)
    data_files_of_any_ds = JsonListOfDictsOfAnyDataset(data_files_of_any)

    return data_files_of_scalar_records_ds, data_files_of_any_ds
