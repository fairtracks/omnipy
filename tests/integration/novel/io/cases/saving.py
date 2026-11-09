"""Values whose serialized representation must survive save/load round trips."""

from typing import NamedTuple

import pytest_cases as pc

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.raw.datasets import StrictBytesDataset, StrictStrDataset
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..helpers.models import MergeObservations


class SaveCase(NamedTuple):
    value: Model | Dataset
    member_names: set[str]
    """Names of the saved archive members, without file suffixes"""


@pc.parametrize('values', [[], [1, 2]])
def case_model_list(values: list[int]) -> SaveCase:
    return SaveCase(value=Model[list[int]](values), member_names={'__model_list_int__'})


def case_model_mapping() -> SaveCase:
    return SaveCase(
        value=Model[dict[str, int]]({'first': 1, 'second': 2}),
        member_names={'__model_dict_str_int__'},
    )


def case_model_wrapping_dataset() -> SaveCase:
    return SaveCase(
        value=Model[JsonDataset](first=[1, 2], second=[3, 4]), member_names={'first', 'second'}
    )


def case_model_string() -> SaveCase:
    return SaveCase(value=Model[str]('"quoted"'), member_names={'__model_str__'})


def case_model_bytes() -> SaveCase:
    return SaveCase(value=Model[bytes](b'\x00\xff\x01'), member_names={'__model_bytes__'})


@pc.parametrize('value', ['123', '"quoted"', b'123'])
def case_model_object(value: str | bytes) -> SaveCase:
    return SaveCase(value=Model[object](value), member_names={'__model_object__'})


def case_dataset_single_entry() -> SaveCase:
    return SaveCase(value=JsonDataset(first=[1, 2]), member_names={'first'})


def case_dataset_multiple_entries() -> SaveCase:
    return SaveCase(
        value=JsonDataset(first=[1, 2], second=[3, 4]), member_names={'first', 'second'}
    )


def case_dataset_strings() -> SaveCase:
    return SaveCase(
        value=StrictStrDataset(first='"quoted"', second='null'), member_names={'first', 'second'}
    )


def case_dataset_bytes() -> SaveCase:
    return SaveCase(
        value=StrictBytesDataset(first=b'\x00\xff\x01', second=b'123'),
        member_names={'first', 'second'},
    )


def case_json_dataset_strings() -> SaveCase:
    dataset = JsonDataset(first='"123"', second='"quoted"', third='hello')
    return SaveCase(value=dataset, member_names={'first', 'second', 'third'})


def case_empty_dataset() -> SaveCase:
    return SaveCase(value=JsonDataset(), member_names=set())


def case_merged_records() -> SaveCase:
    return SaveCase(
        value=MergeObservations([[{'project': 'north', 'identity': 'a|b', 'value': 1}]]),
        member_names={'__merge_observations__'},
    )
