"""Values whose serialized representation must survive save/load round trips."""

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.raw.datasets import StrictBytesDataset, StrictStrDataset


def case_dataset_single_entry():
    return JsonDataset(first=[1, 2]), {'first'}


def case_dataset_multiple_entries():
    return JsonDataset(first=[1, 2], second=[3, 4]), {'first', 'second'}


def case_dataset_strings():
    return StrictStrDataset(first='"quoted"', second='null'), {'first', 'second'}


def case_dataset_bytes():
    return StrictBytesDataset(first=b'\x00\xff\x01', second=b'123'), {'first', 'second'}


def case_json_dataset_strings():
    dataset = JsonDataset(first='"123"', second='"quoted"', third='hello')
    return dataset, {'first', 'second', 'third'}


def case_empty_dataset():
    return JsonDataset(), set()
