from typing import Dict, List

from unifair.compute.task import TaskTemplate
from unifair.data.dataset import Dataset

from ..json.models import JsonDataset
from .models import TableOfStrings, TableOfStringsAndLists


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
