from textwrap import dedent

import pandas
import pytest

from omnipy.components.json.datasets import JsonDataset
from omnipy.components.pandas.datasets import PandasDataset
from omnipy.components.raw.datasets import StrDataset
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


@pytest.fixture
def pandas_dataset() -> PandasDataset:
    _pandas_dataset = PandasDataset()
    _pandas_dataset.from_data({
        'pandas_person':
            pandas.DataFrame((('John', 'Doe', 46), ('Jane', 'Doe', 42), ('Mr', 'Miyagi', 82)),
                             columns=('firstname', 'lastname', 'age')),
        'pandas_fruits':
            pandas.DataFrame((('apple', 'sweet'), ('orange', 'sweet and sour'), ('lemon', 'sour')),
                             columns=('fruit', 'taste'))
    })
    return _pandas_dataset


@pytest.fixture
def json_table_dataset() -> JsonDataset:
    _json_table_dataset = JsonDataset()
    _json_table_dataset['json_table_a'] = [
        dict(firstname='John', lastname='Doe', age=46),
        dict(firstname='Jane', lastname='Doe', age=42),
        dict(firstname='Mr.', lastname='Miyagi', age=82)
    ]
    _json_table_dataset['json_table_b'] = [
        dict(fruit='apple', taste='sweet'),
        dict(fruit='orange', taste='sweet and sour'),
        dict(fruit='lemon', taste='sour')
    ]
    return _json_table_dataset


@pytest.fixture
def json_nested_table_dataset() -> JsonDataset:
    _json_nested_table_dataset = JsonDataset()
    _json_nested_table_dataset['json_nested_table_a'] = [
        dict(name=dict(firstname='John', lastname='Doe'), age=46),
        dict(name=dict(firstname='Jane', lastname='Doe'), age=42),
        dict(name=dict(firstname='Mr.', lastname='Miyagi'), age=82)
    ]
    _json_nested_table_dataset['json_nested_table_b'] = [
        dict(name=dict(fruit='apple'), taste='sweet'),
        dict(name=dict(fruit='orange'), taste='sweet and sour'),
        dict(name=dict(fruit='lemon'), taste='sour')
    ]
    return _json_nested_table_dataset


# TODO: Switching `Dataset[Model[str]]` with `StrDataset` causes json to be evaluated
#       Also for `json_str_dataset` below
@pytest.fixture
def json_table_as_str_dataset() -> Dataset[Model[str]]:
    _json_table_as_str_dataset = Dataset[Model[str]]()
    _json_table_as_str_dataset['json_table_a'] = dedent("""
    [
        {"firstname": "John", "lastname": "Doe", "age": 46},
        {"firstname": "Jane", "lastname": "Doe", "age": 42},
        {"firstname": "Mr.", "lastname": "Miyagi", "age": 82}
    ]""")
    _json_table_as_str_dataset['json_table_b'] = dedent("""
    [
        {"fruit": "apple", "taste": "sweet"},
        {"fruit": "orange", "taste": "sweet and sour"},
        {"fruit": "lemon", "taste": "sour"}
    ]""")
    return _json_table_as_str_dataset


@pytest.fixture
def json_dataset() -> JsonDataset:
    _json_dataset = JsonDataset()
    _json_dataset['json_python_a'] = {'one': ['content', 1, True], 'two': None}
    _json_dataset['json_python_b'] = [1, 4, 9, {'options': {'verbose': False}}]
    return _json_dataset


@pytest.fixture
def json_str_dataset() -> Dataset[Model[str]]:
    _json_str_dataset = Dataset[Model[str]]()
    _json_str_dataset['json_str_a'] = '{"one": ["content", 1, true], "two": null}'
    _json_str_dataset['json_str_b'] = '[1, 4, 9, {"options": {"verbose": false}}]'
    return _json_str_dataset


@pytest.fixture
def csv_dataset() -> StrDataset:
    _csv_dataset = StrDataset()
    _csv_dataset['csv_person'] = 'firstname,lastname,age\nJohn,Doe,46\nJane,Doe,42\nMr,Miyagi,82\n'
    _csv_dataset['csv_fruits'] = 'fruit,taste\napple,sweet\norange,sweet and sour\nlemon,sour\n'
    return _csv_dataset


@pytest.fixture
def str_dataset() -> StrDataset:
    _str_dataset = StrDataset()
    _str_dataset['str_a'] = '1, 2, 4, 6 -> aa\n6, 3, 4, 2 -> ab\n'
    _str_dataset['str_b'] = '3, 5, 6, 3 -> ba\n2, 5, 6, 3 -> bb\n'
    return _str_dataset


@pytest.fixture
def str_unicode_dataset() -> StrDataset:
    _str_unicode_dataset = StrDataset()
    _str_unicode_dataset['str_unicode_a'] = b'\xef\xbb\xbf1, 2, 4, 6 -> aa\n6, 3, 4, 2 -> ab\n'
    _str_unicode_dataset['str_unicode_b'] = b'\xef\xbb\xbf3, 5, 6, 3 -> ba\n2, 5, 6, 3 -> bb\n'
    return _str_unicode_dataset


@pytest.fixture
def python_dataset() -> Dataset[Model[object]]:
    _python_dataset = Dataset[Model[object]]()
    _python_dataset['python_a'] = [{'a': 1, 'b': [2, 3, 4], 'c': {'yes': True, 'no': False}}]
    _python_dataset['python_b'] = lambda x: x + 1
    return _python_dataset
