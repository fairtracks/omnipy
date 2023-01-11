from json import JSONDecodeError
from types import NoneType
from typing import List, Union

from pydantic import ValidationError
import pytest

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.modules.json.models import JsonDataset, JsonModel, JsonScalarType, JsonType


def test_json_dataset_array_of_objects_same_keys():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'})
    assert json_data['obj_type'].to_data() == [{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]


def test_json_dataset_array_of_objects_different_keys():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': '[{"a": "abc", "b": 12}, {"c": "bcd"}]'})
    assert json_data['obj_type'].to_data() == [{'a': 'abc', 'b': 12}, {'c': 'bcd'}]


def test_json_dataset_array_of_nested_objects():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': '[{"a": "abc", "b": {"c": [1, 3]}}]'})
    assert json_data['obj_type'].to_data() == [{'a': 'abc', 'b': {'c': [1, 3]}}]


def test_json_dataset_empty_array():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': '[]'})
    assert json_data['obj_type'].to_data() == []


def test_json_dataset_empty_object():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': '[{"a": "abc", "b": 12}, {}]'})
    assert json_data['obj_type'].to_data() == [{'a': 'abc', 'b': 12}, {}]


def test_json_dataset_single_number():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': '1'})
    assert json_data['obj_type'].to_data() == 1


def test_json_dataset_list_of_scalars():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': '[true, 234, 2.0, "12", null]'})
    assert json_data['obj_type'].to_data() == [True, 234, 2.0, '12', None]


def test_json_dataset_nested():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': '{"a": {"b": [[true, 234, 2.0, "12", null], "c"]}}'})
    assert json_data['obj_type'].to_data() == {'a': {'b': [[True, 234, 2.0, '12', None], 'c']}}


def test_json_dataset_empty_array_with_whitespace():
    json_data = JsonDataset()
    json_data.from_json({'obj_type': ' [] '})


def test_fail_json_dataset_no_json():
    json_data = JsonDataset()
    with pytest.raises(ValidationError):
        json_data.from_json({'obj_type': ''})


def test_fail_json_dataset_malformed_json():
    json_data = JsonDataset()
    with pytest.raises(ValidationError):
        json_data.from_json({'obj_type': '[{,'})
