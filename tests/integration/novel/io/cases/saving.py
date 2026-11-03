"""Values whose serialized representation must survive save/load round trips."""

import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.raw.datasets import StrictBytesDataset, StrictStrDataset
from omnipy.data.model import Model


@pc.parametrize('values', [[], [1, 2]])
def case_model_list(values):
    return Model[list[int]](values), {'data'}


def case_model_mapping():
    return Model[dict[str, int]]({'first': 1, 'second': 2}), {'data'}


def case_model_wrapping_dataset():
    return Model[JsonDataset](first=[1, 2], second=[3, 4]), {'data'}


def case_model_string():
    return Model[str]('"quoted"'), {'data'}


def case_model_bytes():
    return Model[bytes](b'\x00\xff\x01'), {'data'}


def case_dataset_single_entry():
    return JsonDataset(first=[1, 2]), {'first'}


def case_dataset_multiple_entries():
    return JsonDataset(first=[1, 2], second=[3, 4]), {'first', 'second'}


def case_dataset_strings():
    return StrictStrDataset(first='"quoted"', second='null'), {'first', 'second'}


def case_dataset_bytes():
    return StrictBytesDataset(first=b'\x00\xff\x01', second=b'123'), {'first', 'second'}


def case_empty_dataset():
    return JsonDataset(), set()
