from json import JSONDecodeError

from pydantic import ValidationError
import pytest

from unifair.dataset.json import JsonDataset


def test_json_dataset_array_of_objects_same_keys():
    json_data = JsonDataset()
    json_data['obj_type'] = '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'
    assert json_data['obj_type'] == [{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}]


def test_json_dataset_array_of_objects_different_keys():
    json_data = JsonDataset()
    json_data['obj_type'] = '[{"a": "abc", "b": 12}, {"c": "bcd"}]'
    assert json_data['obj_type'] == [{'a': 'abc', 'b': 12}, {'c': 'bcd'}]


def test_json_dataset_array_of_nested_objects():
    json_data = JsonDataset()
    json_data['obj_type'] = '[{"a": "abc", "b": {"c": [1, 3]}}]'
    assert json_data['obj_type'] == [{'a': 'abc', 'b': {'c': [1, 3]}}]


def test_json_dataset_empty_array():
    json_data = JsonDataset()
    json_data['obj_type'] = '[]'


def test_json_dataset_empty_array_with_whitespace():
    json_data = JsonDataset()
    json_data['obj_type'] = ' [] '


def test_json_dataset_error_no_json():
    json_data = JsonDataset()
    with pytest.raises(JSONDecodeError):
        json_data['obj_type'] = ''


def test_json_dataset_error_malformed_json():
    json_data = JsonDataset()
    with pytest.raises(JSONDecodeError):
        json_data['obj_type'] = '[{,'


def test_json_dataset_error_not_array():
    json_data = JsonDataset()
    with pytest.raises(ValidationError):
        json_data['obj_type'] = '1'


def test_json_dataset_error_array_elements_not_objects():
    json_data = JsonDataset()
    with pytest.raises(ValidationError):
        json_data['obj_type'] = '[123, 234]'


def test_json_dataset_error_empty_object():
    # We might want to reevaluate how to handle empty objects later
    json_data = JsonDataset()
    with pytest.raises(ValidationError):
        json_data['obj_type'] = '[{"a": "abc", "b": 12}, {}]'
