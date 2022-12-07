from collections import defaultdict
from copy import copy
from functools import lru_cache
from typing import Dict, List, Tuple

import jq

from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset

from ..json.models import (JsonDataset,
                           JsonDictOfAnyModel,
                           JsonDictOfListOfDictOfAnyModel,
                           JsonListOfDictOfAnyModel,
                           JsonListOfNestedDictsModel)
from .models import TableOfStrings, TableOfStringsAndLists

ID_KEY = '_unifair_id'
REF_KEY = '_unifair_ref'
DEFAULT_KEY = '__root__'


@TaskTemplate
def remove_columns(
        json_dataset: JsonDataset,
        column_keys_for_data_items: Dict[str, List[str]]) -> Dataset[TableOfStringsAndLists]:
    # TODO: implement general solution to make sure that one does not modify input data by
    #       automatically copying or otherwise
    #
    # dataset_copy = deepcopy(json_dataset)
    for data_item_key, column_keys in column_keys_for_data_items.items():
        for record in json_dataset[data_item_key]:
            for column in column_keys:
                if column in record:
                    del record[column]
    return Dataset[TableOfStringsAndLists](json_dataset.to_data())


@TaskTemplate
def convert_to_1nf(input_dataset: Dataset[TableOfStringsAndLists]) -> Dataset[TableOfStrings]:
    out_dataset = Dataset[TableOfStrings]()
    for table_name, table in input_dataset.items():
        # for record in table:
        #     ...
        out_dataset[table_name] = table
    return out_dataset


@lru_cache(maxsize=1)
def get_filter_all_top_level_parents_of_subtrees_compiler():
    return jq.compile('map_values(arrays,objects)')


def filter_all_top_level_parents_of_subtrees(data: JsonDictOfAnyModel) -> JsonDictOfAnyModel:
    return get_filter_all_top_level_parents_of_subtrees_compiler().input(data).first()


def delete_element_from_dict(data, path):
    path_list = path.split('.')
    for i in path_list[:-1]:
        data = data[i]
    del data[path_list[-1]]


def update_dict_from_front(dict_a: Dict, dict_b: Dict) -> None:
    dict_a_copy = copy(dict_a)
    dict_a.clear()
    dict_a.update(dict_b)
    dict_a.update(dict_a_copy)


def flatten_outer_level_of_nested_record(nested_record: JsonDictOfAnyModel,
                                         record_id: str,
                                         data_file_title: str,
                                         id_key: str,
                                         ref_key: str,
                                         default_key: str) -> JsonDictOfListOfDictOfAnyModel:
    all_top_level_parents_of_subtrees = filter_all_top_level_parents_of_subtrees(nested_record)
    record_id = ensure_item_first_in_nested_record(
        nested_record, key=id_key, default_value=record_id, update=False)

    new_data_files = {}
    for key, value in all_top_level_parents_of_subtrees.items():
        new_data_file_title: str = f'{data_file_title}.{key}'
        new_data_file = value

        if isinstance(new_data_file, dict):
            new_data_file = [new_data_file]

        add_reference_to_parent_from_child(
            child=new_data_file,
            parent_title=data_file_title,
            ident=record_id,
            ref_key=ref_key,
            default_key=default_key)

        new_data_files[new_data_file_title] = new_data_file
        delete_element_from_dict(nested_record, key)

    return new_data_files


def get_ref_value(data_file_title, ident):
    return f'{data_file_title}.{ident}'


def add_reference_to_parent_from_child(
    child: JsonListOfDictOfAnyModel,
    parent_title: str,
    ident: str,
    ref_key: str,
    default_key: str,
):
    ref_value = get_ref_value(parent_title, ident)
    for i, new_nested_record in enumerate(child):
        if not isinstance(new_nested_record, dict):
            new_nested_record = {default_key: new_nested_record}
            child[i] = new_nested_record
        ensure_item_first_in_nested_record(
            new_nested_record, key=ref_key, default_value=ref_value, fail_if_present=True)


def ensure_item_first_in_nested_record(
    nested_record,
    key,
    default_value,
    update=True,
    fail_if_present=False,
):
    value = default_value

    if key in nested_record:
        assert not fail_if_present, f'Key "{key}" already present in dict'
        if not update:
            value = nested_record[key]
        del nested_record[key]

    update_dict_from_front(nested_record, {key: value})

    return value


def split_outer_lists_from_dataset_as_new_data_files(
    dataset: Dataset[JsonListOfDictOfAnyModel], id_key: str, ref_key: str, default_key: str
) -> Tuple[Dataset[JsonListOfNestedDictsModel], Dataset[JsonListOfDictOfAnyModel]]:

    data_files_without_nested_lists = defaultdict(list)
    data_files_maybe_with_nested_lists = defaultdict(list)
    for data_file_title, item in dataset.items():
        data_file = item.to_data()

        if len(data_file) == 0:
            data_files_without_nested_lists[data_file_title] = []

        for record_id, nested_record in enumerate(data_file):
            new_data_files = flatten_outer_level_of_nested_record(
                nested_record,
                str(record_id),
                data_file_title,
                id_key,
                ref_key,
                default_key,
            )

            for new_data_file_title, new_data_file in new_data_files.items():
                data_files_maybe_with_nested_lists[new_data_file_title] += new_data_file
            data_files_without_nested_lists[data_file_title].append(nested_record)

    all_data_files_without_nested_lists_ds = Dataset[JsonListOfNestedDictsModel](
        data_files_without_nested_lists)
    all_data_files_maybe_with_nested_lists_ds = Dataset[JsonListOfDictOfAnyModel](
        data_files_maybe_with_nested_lists)

    return all_data_files_without_nested_lists_ds, all_data_files_maybe_with_nested_lists_ds


@TaskTemplate(fixed_params=dict(id_key=ID_KEY, ref_key=REF_KEY, default_key=DEFAULT_KEY))
def flatten_nested_json_to_list_of_dicts(
    dataset: Dataset[JsonListOfDictOfAnyModel],
    id_key: str,
    ref_key: str,
    default_key: str,
) -> Dataset[JsonListOfNestedDictsModel]:
    data_files_maybe_with_nested_lists_ds = dataset
    all_data_files_without_nested_lists_ds = Dataset[JsonListOfNestedDictsModel]()

    while len(data_files_maybe_with_nested_lists_ds) > 0:
        data_files_without_nested_lists_ds, data_files_maybe_with_nested_lists_ds = \
            split_outer_lists_from_dataset_as_new_data_files(
                data_files_maybe_with_nested_lists_ds, id_key, ref_key, default_key)
        all_data_files_without_nested_lists_ds.update(data_files_without_nested_lists_ds)

    return all_data_files_without_nested_lists_ds


@TaskTemplate
def transpose_dataset_of_dicts_to_lists(dataset: Dataset[JsonDictOfAnyModel],
                                        id_key: str = ID_KEY) -> Dataset[JsonListOfDictOfAnyModel]:
    output_dataset = Dataset[JsonListOfDictOfAnyModel]()
    output_data = defaultdict(list)
    for name, item in dataset.items():
        for key, val in item.to_data().items():
            if not isinstance(val, list):
                val = [val]

            for item_index, item in enumerate(val):
                if isinstance(item, dict):
                    data = {id_key: f'{name}_{item_index}'}
                    assert id_key not in item
                    data.update(item)
                else:
                    data = item
                output_data[key].append(data)
    output_dataset.update(output_data.items())
    return output_dataset
