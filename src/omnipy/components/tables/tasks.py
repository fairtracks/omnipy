from copy import copy, deepcopy
from typing import cast

from omnipy.compute.task import TaskTemplate

from ..json.datasets import JsonListOfDictsDataset
from ..json.typedefs import JsonScalar
from .datasets import TableWithColNamesDataset
from .models import (TableDictOfDictsOfJsonScalarsModel,
                     TableListOfDictsOfJsonScalarsModel,
                     TableWithColNamesModel)


@TaskTemplate()
def remove_columns(json_dataset: JsonListOfDictsDataset,
                   column_keys_for_data_items: dict[str, list[str]]) -> JsonListOfDictsDataset:
    # TODO: implement general solution to make sure that one does not modify input data by
    #       automatically copying or otherwise. Perhaps setting immutable/frozen option in pydantic,
    #       if available?
    #
    dataset_copy = deepcopy(json_dataset)
    for data_item_key, column_keys in column_keys_for_data_items.items():
        for record in dataset_copy[data_item_key]:
            for column in column_keys:
                if column in record:
                    del record[column]
    return JsonListOfDictsDataset(json_dataset.to_data())


@TaskTemplate(iterate_over_data_files=True, output_dataset_cls=TableWithColNamesDataset)
def rename_col_names(data_file: TableWithColNamesModel,
                     prev2new_keymap: dict[str, str]) -> TableWithColNamesModel:
    return TableWithColNamesModel([{
        prev2new_keymap[key] if key in prev2new_keymap else key: val for key, val in row.items()
    } for row in data_file])


@TaskTemplate()
def transpose_columns_with_data_files(dataset: TableWithColNamesDataset,
                                      exclude_cols: tuple[str]) -> None:
    output_dataset = JsonListOfDictsDataset()

    max_len = max(len(data_file) for data_file in dataset.values())

    # TODO: Make Dataset behave like a defaultDict, possibly also with auto-expanding lists?
    for column_name in dataset.col_names:
        if column_name not in exclude_cols:
            output_dataset[column_name] = [{}] * max_len

    for data_file_name, data_file in dataset.items():
        for row_i, el in enumerate(data_file):
            for key, val in el.items():
                if key in exclude_cols:
                    for data_file in output_dataset.values():
                        data_file[row_i][key] = val
                else:
                    output_dataset[key][row_i][data_file_name] = val

    return output_dataset


# @TaskTemplate()
# def convert_to_1nf(input_dataset: Dataset[TableOfStringsAndLists]) -> Dataset[TableOfStrings]:
#     out_dataset = Dataset[TableOfStrings]()
#     for table_name, table in input_dataset.items():
#         # for record in table:
#         #     ...
#         out_dataset[table_name] = table
#     return out_dataset

# TODO: Somehow fix so that we do not need to call Model.content within a task


@TaskTemplate(iterate_over_data_files=True)
def create_row_index_from_column(list_of_dicts: TableListOfDictsOfJsonScalarsModel,
                                 column_key: str) -> TableDictOfDictsOfJsonScalarsModel:
    output_dict = {}
    input_table = cast(list[dict[str, JsonScalar]], list_of_dicts.to_data())
    for item in input_table:
        item_copy = copy(item)
        new_key = item[column_key]
        del item_copy[column_key]
        output_dict[new_key] = item_copy
    return TableDictOfDictsOfJsonScalarsModel(output_dict)
