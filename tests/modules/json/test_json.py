from pydantic import ValidationError
import pytest

from omnipy.modules.json.datasets import JsonDataset


def test_json_dataset_array_of_objects_same_keys():
    json_data = JsonDataset()
    json_data.from_json({'data_file': '[{"a": "abc", "b": 12}, {"a": "bcd", "b": 23}]'})
    assert json_data.to_data() == dict(data_file=[{'a': 'abc', 'b': 12}, {'a': 'bcd', 'b': 23}])


def test_json_dataset_array_of_objects_different_keys():
    json_data = JsonDataset()
    json_data.from_json({'data_file': '[{"a": "abc", "b": 12}, {"c": "bcd"}]'})
    assert json_data.to_data() == dict(data_file=[{'a': 'abc', 'b': 12}, {'c': 'bcd'}])


def test_json_dataset_array_of_nested_objects():
    json_data = JsonDataset()
    json_data.from_json({'data_file': '[{"a": "abc", "b": {"c": [1, 3]}}]'})
    assert json_data.to_data() == dict(data_file=[{'a': 'abc', 'b': {'c': [1, 3]}}])


def test_json_dataset_empty_array():
    json_data = JsonDataset()
    json_data.from_json({'data_file': '[]'})
    assert json_data.to_data() == dict(data_file=[])


def test_json_dataset_empty_object():
    json_data = JsonDataset()
    json_data.from_json({'data_file': '[{"a": "abc", "b": 12}, {}]'})
    assert json_data.to_data() == dict(data_file=[{'a': 'abc', 'b': 12}, {}])


def test_json_dataset_single_number():
    json_data = JsonDataset()
    json_data.from_json({'data_file': '1'})
    assert json_data.to_data() == dict(data_file=1)


def test_json_dataset_list_of_scalars():
    json_data = JsonDataset()
    json_data.from_json({'data_file': '[true, 234, 2.0, "12", null]'})
    assert json_data.to_data() == dict(data_file=[True, 234, 2.0, '12', None])


def test_json_dataset_nested():
    json_data = JsonDataset()
    json_data.from_json({'data_file': '{"a": {"b": [[true, 234, 2.0, "12", null], "c"]}}'})
    assert json_data.to_data() == dict(data_file={'a': {'b': [[True, 234, 2.0, '12', None], 'c']}})


def test_json_dataset_empty_array_with_whitespace():
    json_data = JsonDataset()
    json_data.from_json({'data_file': ' [] '})


def test_fail_json_dataset_no_json():
    json_data = JsonDataset()
    with pytest.raises(ValidationError):
        json_data.from_json({'data_file': ''})


def test_fail_json_dataset_malformed_json():
    json_data = JsonDataset()
    with pytest.raises(ValidationError):
        json_data.from_json({'data_file': '[{,'})
