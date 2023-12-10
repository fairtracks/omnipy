from copy import deepcopy

from omnipy.compute.task import TaskTemplate
from omnipy.compute.typing import mypy_fix_task_template
from omnipy.modules.json.datasets import JsonListOfDictsDataset


@mypy_fix_task_template
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


# @mypy_fix_task_template
# @TaskTemplate()
# def convert_to_1nf(input_dataset: Dataset[TableOfStringsAndLists]) -> Dataset[TableOfStrings]:
#     out_dataset = Dataset[TableOfStrings]()
#     for table_name, table in input_dataset.items():
#         # for record in table:
#         #     ...
#         out_dataset[table_name] = table
#     return out_dataset
