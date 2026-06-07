from dataclasses import dataclass
from typing import Annotated

import pytest

from omnipy.components.json.models import JsonScalarModel
from omnipy.components.nested.datasets import NestedDataset
from omnipy.components.nested.models import (EnumeratedListModel,
                                             EnumeratedListOfTuplesModel,
                                             ListAsNestedDatasetModel)
from omnipy.data.dataset import Dataset
from omnipy.util.pydantic import ValidationError


def test_enumerated_list_of_tuples_model() -> None:
    data = [(0, 'a'), ('1', 'b'), (2, 'c')]
    expected = [(0, 'a'), (1, 'b'), (2, 'c')]
    enumerated = EnumeratedListOfTuplesModel(data)
    assert enumerated.content == expected
    assert enumerated.to_data() == expected

    data_empty: list[str] = []
    expected_empty: list[str] = []
    enumerated = EnumeratedListOfTuplesModel(data_empty)
    assert enumerated.content == expected_empty
    assert enumerated.to_data() == expected_empty


def test_enumerated_list_of_tuples_model_failures() -> None:
    data_not_sequential = [(3, 'a'), (5, 'b'), (1, 'c')]
    with pytest.raises(ValidationError):
        EnumeratedListOfTuplesModel(data_not_sequential)

    data_not_from_zero = [(1, 'a'), (2, 'b'), (3, 'c')]
    with pytest.raises(ValidationError):
        EnumeratedListOfTuplesModel(data_not_from_zero)


def test_enumerated_list_model() -> None:
    data = ['a', 'b', 'c']
    expected = [(0, 'a'), (1, 'b'), (2, 'c')]
    enumerated = EnumeratedListModel(data)
    assert enumerated.content == EnumeratedListOfTuplesModel(expected)
    assert enumerated.to_data() == expected

    @dataclass
    class MyClass:
        val: str

    data_complex = [(10, 'x'), {'abc': (20, 'y')}, (30, MyClass('something'))]
    expected_complex = [(0, (10, 'x')), (1, {'abc': (20, 'y')}), (2, (30, MyClass('something')))]
    enumerated_complex = EnumeratedListModel(data_complex)
    assert enumerated_complex.content == EnumeratedListOfTuplesModel(expected_complex)
    assert enumerated_complex.to_data() == expected_complex

    data_empty: list[str] = []
    expected_empty: list[str] = []
    enumerated = EnumeratedListModel(data_empty)
    assert enumerated.content == EnumeratedListOfTuplesModel(expected_empty)
    assert enumerated.to_data() == expected_empty


# TODO: Type NestedDataset correctly (perhaps inspired by JsonModel?)


def test_nested_dataset_only_dicts() -> None:
    nested_dict_data = {'id_0': {'name': 'Alice', 'age': 30}, 'id_1': {'name': 'Bob', 'age': 25}}
    nested_dict_dataset = NestedDataset(nested_dict_data)
    assert nested_dict_dataset.to_data() == nested_dict_data

    assert len(nested_dict_dataset) == 2
    assert isinstance(nested_dict_dataset['id_0'], Dataset)
    assert nested_dict_dataset['id_0'].to_data() == {'name': 'Alice', 'age': 30}

    assert nested_dict_dataset['id_0']['name'] == JsonScalarModel('Alice')  # pyright: ignore
    assert nested_dict_dataset['id_0']['name'].to_data() == 'Alice'  # pyright: ignore

    nested_dict_dataset['id_0']['age'] = 31  # pyright: ignore
    assert nested_dict_dataset['id_0']['age'].to_data() == 31  # pyright: ignore

    nested_dict_dataset['id_2'] = {'name': 'Charlie', 'age': 28}
    nested_dict_dataset['id_3'] = nested_dict_dataset['id_2']
    nested_dict_dataset['id_3']['name'] = nested_dict_dataset['id_2']['name']  # pyright: ignore
    nested_dict_dataset['id_0', 'id_1'] = nested_dict_dataset['id_2', 'id_3']

    with pytest.raises(ValidationError):
        nested_dict_dataset['id_2'] = 1 + 2j  # JsonScalarModel only accepts JSON-serializable data


def test_list_as_nested_dataset_model() -> None:
    list_data = [123, 'abc', 45.6, True, None, {'x': 1, 'y': 2}]
    list_data_expected_output = {
        '0': 123, '1': 'abc', '2': 45.6, '3': True, '4': None, '5': {
            'x': 1, 'y': 2
        }
    }

    list_as_nested_dataset_model = ListAsNestedDatasetModel(list_data)
    assert list(list_as_nested_dataset_model['5'].keys()) == ['x', 'y']
    assert list_as_nested_dataset_model['5']['x'] == JsonScalarModel(1)
    assert list_as_nested_dataset_model.to_data() == list_data_expected_output

    simple_nested_data = {'a': list_data}
    simple_nested_data_expected_output = {'a': list_data_expected_output}

    simple_nested_dataset = NestedDataset(simple_nested_data)
    assert simple_nested_dataset.to_data() == simple_nested_data_expected_output

    empty_list_data: list[object] = []

    empty_list_as_nested_dataset_model = ListAsNestedDatasetModel(empty_list_data)
    assert list(empty_list_as_nested_dataset_model.keys()) == []
    assert empty_list_as_nested_dataset_model.to_data() == {}


def test_nested_dataset_forward_ref_updates_with_table_model_variants() -> None:
    NestedDataset.update_forward_refs()


# Known issue: NestedDataset incompatibility with dynamic conversion of elements to models
def test_nested_dataset_lists_and_dicts(
        skip_test_if_dynamically_convert_elements_to_models: Annotated[None,
                                                                       pytest.fixture]) -> None:
    nested_lists_and_dict_data = {
        'id_0': {
            'name':
                'Alice',
            'age':
                30,
            'kids': [{
                'name': 'Charlie',
                'age': 5,
                'toys': ['car', 'doll'],
            }, {
                'name': 'Daisy', 'age': 3
            }, {
                'name': 'Eve', 'age': 1
            }]
        },
        'id_1': {
            'name':
                'Bob',
            'age':
                25,
            'kids': [{
                'name': 'Frank', 'age': 4, 'toys': ['ball']
            }, {
                'name': 'Grace', 'age': 2, 'toys': ['puzzle']
            }]
        }
    }

    expected_lists_and_dict_output = {
        'id_0': {
            'name': 'Alice',
            'age': 30,
            'kids': {
                '0': {
                    'name': 'Charlie', 'age': 5, 'toys': ['car', 'doll']
                },
                '1': {
                    'name': 'Daisy', 'age': 3
                },
                '2': {
                    'name': 'Eve', 'age': 1
                }
            }
        },
        'id_1': {
            'name': 'Bob',
            'age': 25,
            'kids': {
                '0': {
                    'name': 'Frank', 'age': 4, 'toys': ['ball']
                },
                '1': {
                    'name': 'Grace', 'age': 2, 'toys': ['puzzle']
                }
            }
        }
    }
    nested_lists_and_dict_dataset = NestedDataset(nested_lists_and_dict_data)
    assert nested_lists_and_dict_dataset.to_data() == expected_lists_and_dict_output

    assert len(nested_lists_and_dict_dataset) == 2
    assert list(nested_lists_and_dict_dataset['id_0'].keys()) == [  # pyright: ignore
        'name', 'age', 'kids'
    ]
    assert nested_lists_and_dict_dataset['id_0'].to_data() == expected_lists_and_dict_output['id_0']
    assert list(nested_lists_and_dict_dataset['id_0']['kids'].keys()) == [  # pyright: ignore
        '0', '1', '2'
    ]
    assert len(nested_lists_and_dict_dataset['id_0']['kids']) == 3  # pyright: ignore
    assert nested_lists_and_dict_dataset['id_0']['kids'][0].to_data() == {  # pyright: ignore
        'name': 'Charlie', 'age': 5, 'toys': ['car', 'doll']
    }
    assert (nested_lists_and_dict_dataset['id_0']['kids'][0]['name']  # pyright: ignore
            == JsonScalarModel('Charlie'))
    assert (nested_lists_and_dict_dataset['id_0']['kids'][0]['name'].to_data()  # pyright: ignore
            == 'Charlie')

    nested_lists_and_dict_dataset['id_0']['kids'][0]['age'] = 6  # pyright: ignore
    assert nested_lists_and_dict_dataset['id_0']['kids'][0]['age'].to_data() == 6  # pyright: ignore

    nested_lists_and_dict_dataset['id_2'] = {
        'name': 'Charlie',
        'age': 28,
        'kids': [{
            'name': 'Hannah', 'age': 2, 'toys': ['teddy bear']
        }]
    }
    assert nested_lists_and_dict_dataset['id_2']['kids'].to_data() == {  # pyright: ignore
        '0': {
            'name': 'Hannah', 'age': 2, 'toys': ['teddy bear']
        }
    }

    nested_lists_and_dict_dataset['id_2'][  # pyright: ignore
        'kids'] = nested_lists_and_dict_dataset['id_1']['kids']  # pyright: ignore
    nested_lists_and_dict_dataset['id_0']['kids'][  # pyright: ignore
        0, 2] = nested_lists_and_dict_dataset['id_2']['kids'][0, 1]  # pyright: ignore

    with pytest.raises(ValidationError):
        nested_lists_and_dict_dataset['id_1']['kids'][1]['age'] = 1 + 2j  # pyright: ignore
