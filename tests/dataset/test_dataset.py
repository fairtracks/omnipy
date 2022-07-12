from typing import Any, Dict, Generic, List, TypeVar

from pydantic import PositiveInt, StrictInt, ValidationError
import pytest

from unifair.dataset.dataset import Dataset
from unifair.dataset.model import Model


def test_no_model():
    with pytest.raises(TypeError):
        Dataset()

    with pytest.raises(TypeError):
        Dataset({'obj_type_1': 123, 'obj_type_2': 234})

    with pytest.raises(TypeError):

        class MyDataset(Dataset):
            ...

        MyDataset()

    with pytest.raises(TypeError):
        Dataset[int]()

    with pytest.raises(TypeError):

        class MyDataset(Dataset[List[str]]):
            ...

        MyDataset()


def test_init_with_basic_parsing():
    dataset_1 = Dataset[Model[int]]()

    dataset_1['obj_type_1'] = 123
    dataset_1['obj_type_2'] = 456

    assert len(dataset_1) == 2
    assert dataset_1['obj_type_1'] == 123
    assert dataset_1['obj_type_2'] == 456

    dataset_2 = Dataset[Model[int]]({'obj_type_1': 456.5, 'obj_type_2': '789', 'obj_type_3': True})

    assert len(dataset_2) == 3
    assert dataset_2['obj_type_1'] == 456
    assert dataset_2['obj_type_2'] == 789
    assert dataset_2['obj_type_3'] == 1

    dataset_3 = Dataset[Model[str]]([('obj_type_1', 'abc'), ('obj_type_2', 123),
                                     ('obj_type_3', True)])

    assert len(dataset_3) == 3
    assert dataset_3['obj_type_1'] == 'abc'
    assert dataset_3['obj_type_2'] == '123'
    assert dataset_3['obj_type_3'] == 'True'


def test_more_dict_methods_with_parsing():
    dataset_1 = Dataset[Model[int]]()

    assert len(dataset_1) == 0
    assert list(dataset_1.keys()) == []
    assert list(dataset_1.values()) == []
    assert list(dataset_1.items()) == []

    dataset = Dataset[Model[str]]({'obj_type_1': 123, 'obj_type_2': 234})

    assert list(dataset.keys()) == ['obj_type_1', 'obj_type_2']
    assert list(dataset.values()) == ['123', '234']
    assert list(dataset.items()) == [('obj_type_1', '123'), ('obj_type_2', '234')]

    dataset['obj_type_2'] = 345

    assert len(dataset) == 2
    assert dataset['obj_type_1'] == '123'
    assert dataset['obj_type_2'] == '345'

    del dataset['obj_type_1']
    assert len(dataset) == 1
    assert dataset['obj_type_2'] == '345'

    with pytest.raises(KeyError):
        assert dataset['obj_type_3']

    dataset.update({'obj_type_2': 456, 'obj_type_3': 567})
    assert dataset['obj_type_2'] == '456'
    assert dataset['obj_type_3'] == '567'

    dataset.setdefault('obj_type_3', 789)
    assert dataset.get('obj_type_3') == '567'

    dataset.setdefault('obj_type_4', 789)
    assert dataset.get('obj_type_4') == '789'

    assert len(dataset) == 3

    dataset.pop('obj_type_3')
    assert len(dataset) == 2

    # UserDict() implementation of popitem pops items FIFO contrary of the LIFO specified
    # in the standard library: https://docs.python.org/3/library/stdtypes.html#dict.popitem
    dataset.popitem()
    assert len(dataset) == 1
    assert dataset.to_data() == {'obj_type_4': '789'}

    dataset.clear()
    assert len(dataset) == 0
    assert dataset.to_data() == {}


def test_basic_validation():
    dataset_1 = Dataset[Model[PositiveInt]]()

    dataset_1['obj_type_1'] = 123

    with pytest.raises(ValueError):
        dataset_1['obj_type_2'] = -234

    with pytest.raises(ValueError):
        Dataset[Model[List[StrictInt]]]([12.4, 11])


def test_import_and_export():
    dataset = Dataset[Model[Dict[str, str]]]()

    data = {'obj_type_1': {'a': 123, 'b': 234, 'c': 345}, 'obj_type_2': {'c': 456}}
    dataset.from_data(data)

    assert dataset['obj_type_1'] == {'a': '123', 'b': '234', 'c': '345'}
    assert dataset['obj_type_2'] == {'c': '456'}

    assert dataset.to_data() == {
        'obj_type_1': {
            'a': '123', 'b': '234', 'c': '345'
        }, 'obj_type_2': {
            'c': '456'
        }
    }

    assert dataset.to_json(pretty=False) == {  # noqa
        'obj_type_1': '{"a": "123", "b": "234", "c": "345"}', 'obj_type_2': '{"c": "456"}'
    }  # noqa
    assert dataset.to_json(pretty=True) == {
        'obj_type_1': """
{
    "a": "123",
    "b": "234",
    "c": "345"
}"""[1:],
        'obj_type_2': """
{
    "c": "456"
}"""[1:]
    }

    assert dataset.to_json_schema(pretty=False) == (  # noqa
        '{"title": "Dataset[Model[Dict[str, str]]]", "description": "'
        + Dataset._get_standard_field_description()
        + '", "default": {}, "type": "object", "additionalProperties": '
        '{"$ref": "#/definitions/Model_Dict_str__str__"}, "definitions": '
        '{"Model_Dict_str__str__": {"title": "Model[Dict[str, str]]", '
        '"description": "' + Model._get_standard_field_description()
        + '", "default": {}, "type": "object", "additionalProperties": '
        '{"type": "string"}}}}')

    assert dataset.to_json_schema(pretty=True) == '''
{
    "title": "Dataset[Model[Dict[str, str]]]",
    "description": "'''[1:] + Dataset._get_standard_field_description() + '''",
    "default": {},
    "type": "object",
    "additionalProperties": {
        "$ref": "#/definitions/Model_Dict_str__str__"
    },
    "definitions": {
        "Model_Dict_str__str__": {
            "title": "Model[Dict[str, str]]",
            "description": "''' + Model._get_standard_field_description() + '''",
            "default": {},
            "type": "object",
            "additionalProperties": {
                "type": "string"
            }
        }
    }
}'''  # noqa

    assert dataset.to_json() == dataset.to_json(pretty=False)  # noqa
    assert dataset.to_json_schema() == dataset.to_json_schema(pretty=False)  # noqa


def test_complex_models():
    listT = TypeVar('listT', bound=List)

    class MyReversedListModel(Model[listT], Generic[listT]):
        @classmethod
        def _parse_data(cls, data: List) -> List:
            print(data)
            if isinstance(data, Model):
                data = data.to_data()
            return list(reversed(data))

    class MyRangeList(Model[List[PositiveInt]]):
        @classmethod
        def _parse_data(cls, data: List[PositiveInt]) -> Any:
            if not data:
                return []
            else:
                assert len(data) == 2
                return list(range(data[0], data[1]))

    class MyDictOfStringsDataset(Dataset[MyReversedListModel[MyRangeList]]):
        ...

    dataset = MyDictOfStringsDataset()

    with pytest.raises(ValidationError):
        dataset.from_data([(i, [0, i]) for i in range(0, 5)])  # noqa

    dataset.from_data([(i, [1, i + 1]) for i in range(1, 5)])  # noqa
    assert dataset['4'] == [4, 3, 2, 1]

    assert dataset.to_data() == {'1': [1], '2': [2, 1], '3': [3, 2, 1], '4': [4, 3, 2, 1]}

    assert dataset.to_json(pretty=False) == {
        '1': '[1]', '2': '[2, 1]', '3': '[3, 2, 1]', '4': '[4, 3, 2, 1]'
    }

    print(dataset.to_json_schema(pretty=True))
