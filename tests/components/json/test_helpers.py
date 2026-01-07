from typing import Annotated

import pydantic.fields
import pytest

from omnipy.components.json.helpers import (is_json_dict,
                                            is_json_list,
                                            is_json_scalar,
                                            parse_line_as_elements_of_dict,
                                            parse_line_as_elements_of_list,
                                            parse_str_as_json)


def test_is_json_scalar(skip_test_if_not_default_data_config_values: Annotated[None,
                                                                               pytest.fixture]):
    assert is_json_scalar('hello') is True
    assert is_json_scalar(42) is True
    assert is_json_scalar(3.14) is True
    assert is_json_scalar(True) is True
    assert is_json_scalar(None) is True
    assert is_json_scalar([]) is False
    assert is_json_scalar({}) is False
    assert is_json_scalar([1, 2, 3]) is False
    assert is_json_scalar({'key': 'value'}) is False


def test_is_json_dict(skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]):
    assert is_json_dict('hello') is False
    assert is_json_dict(42) is False
    assert is_json_dict(3.14) is False
    assert is_json_dict(True) is False
    assert is_json_dict(None) is False
    assert is_json_dict([]) is False
    assert is_json_dict({}) is True
    assert is_json_dict([1, 2, 3]) is False
    assert is_json_dict({'key': 'value'}) is True


def test_is_json_list(skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]):
    assert is_json_list('hello') is False
    assert is_json_list(42) is False
    assert is_json_list(3.14) is False
    assert is_json_list(True) is False
    assert is_json_list(None) is False
    assert is_json_list([]) is True
    assert is_json_list({}) is False
    assert is_json_list([1, 2, 3]) is True
    assert is_json_list({'key': 'value'}) is False


def test_parse_str_as_json(skip_test_if_not_default_data_config_values: Annotated[None,
                                                                                  pytest.fixture]):
    assert parse_str_as_json('"hello"') == 'hello'
    assert parse_str_as_json('42') == 42
    assert parse_str_as_json('3.14') == 3.14
    assert parse_str_as_json('true') is True
    assert parse_str_as_json('null') is None
    assert parse_str_as_json('[]') == []
    assert parse_str_as_json('{}') == {}
    assert parse_str_as_json('[1, 2, 3]') == [1, 2, 3]
    assert parse_str_as_json('{"key": "value"}') == {'key': 'value'}
    assert parse_str_as_json('(1, 2, 3)') is pydantic.fields.Undefined


def test_parse_line_as_elements_of_dict(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]):
    assert parse_line_as_elements_of_dict('"key": "value"') == {'key': 'value'}
    assert parse_line_as_elements_of_dict('"key1": "val1", "key2": "val2"') == {
        'key1': 'val1', 'key2': 'val2'
    }
    assert parse_line_as_elements_of_dict('":key1": "va:l1", "key\\\"2": "v\\\"al2"') == {
        ':key1': 'va:l1', 'key"2': 'v"al2'
    }
    assert parse_line_as_elements_of_dict('"key": "value",') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict(
        '"key1": "val1", "key2": "val2",') is pydantic.fields.Undefined

    assert parse_line_as_elements_of_dict('"hello"') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('42') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('3.14') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('true') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('null') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('[]') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('{}') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('[1, 2, 3]') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('{"key": "value"}') is pydantic.fields.Undefined
    assert parse_line_as_elements_of_dict('(1, 2, 3)') is pydantic.fields.Undefined


def test_parse_line_as_elements_of_list(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]):
    assert parse_line_as_elements_of_list('"hello"') == ['hello']
    assert parse_line_as_elements_of_list('42, 3.14, true, null, "hi:"') == [
        42, 3.14, True, None, 'hi:'
    ]
    assert parse_line_as_elements_of_list('[]') == [[]]
    assert parse_line_as_elements_of_list('{}') == [{}]
    assert parse_line_as_elements_of_list('[1, 2, 3]') == [[1, 2, 3]]
    assert parse_line_as_elements_of_list('{"key": "value"}') == [{'key': 'value'}]
    assert parse_line_as_elements_of_list('(1, 2, 3)') is pydantic.fields.Undefined
