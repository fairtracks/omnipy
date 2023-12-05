from types import NoneType
from typing import Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, PositiveInt, StrictInt, ValidationError
import pytest

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from .helpers.models import StringToLength


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


def test_parsing_none_allowed():
    class NoneModel(Model[NoneType]):
        ...

    assert Dataset[NoneModel]({'a': None}).to_data() == {'a': None}

    with pytest.raises(ValidationError):
        Dataset[NoneModel]({'a': 'None'})

    class MaybeNumberModelOptional(Model[Optional[int]]):
        ...

    class MaybeNumberModelUnion(Model[Union[int, None]]):
        ...

    class MaybeNumberModelUnionNew(Model[int | None]):
        ...

    for model_cls in [MaybeNumberModelOptional, MaybeNumberModelUnion, MaybeNumberModelUnionNew]:
        # for model_cls in [MaybeNumberModelOptional, MaybeNumberModelUnion]:
        assert Dataset[model_cls]({'a': None, 'b': 13}).to_data() == {'a': None, 'b': 13}

        with pytest.raises(ValidationError):
            Dataset[model_cls]({'a': 'None'})


def test_parsing_none_not_allowed():
    class IntListModel(Model[List[int]]):
        ...

    class IntDictModel(Model[Dict[int, int]]):
        ...

    for model_cls in [IntListModel, IntDictModel]:

        with pytest.raises(ValidationError):
            Dataset[model_cls]({'a': None})


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


def test_equality() -> None:
    assert Dataset[Model[list[int]]]({'file_1': [1, 2, 3], 'file_2': [1.0, 2.0, 3.0]}) == \
           Dataset[Model[list[int]]]({'file_1': [1.0, 2.0, 3.0], 'file_2': [1, 2, 3]})

    assert Dataset[Model[list[int]]]({'file_1': [1, 2, 3], 'file_2': [1, 2, 3]}) != \
           Dataset[Model[list[int]]]({'file_1': [1, 2, 3], 'file_2': [3, 2, 1]})

    assert Dataset[Model[list[int]]]({'1': [1, 2, 3]}) == \
           Dataset[Model[list[int]]]({1: [1, 2, 3]})

    assert Dataset[Model[list[int]]]({'file_1': [1, 2, 3]}) != \
           Dataset[Model[list[float]]]({'file_1': [1.0, 2.0, 3.0]})


def test_complex_equality() -> None:
    class MyIntList(Model[list[int]]):
        ...

    class MyInt(Model[int]):
        ...

    assert Dataset[Model[list[int]]]({'file_1': [1, 2, 3]}) != \
           Dataset[MyIntList]({'file_1': [1, 2, 3]})

    assert Dataset[Model[MyIntList]]({'file_1': [1, 2, 3]}) == \
           Dataset[Model[MyIntList]]({'file_1': MyIntList([1, 2, 3])})

    assert Dataset[Model[list[MyInt]]]({'file_1': [1, 2, 3]}) == \
           Dataset[Model[list[MyInt]]]({'file_1': list[MyInt]([1, 2, 3])})

    assert Dataset[Model[list[MyInt]]]({'file_1': [1, 2, 3]}) != \
           Dataset[Model[List[MyInt]]]({'file_1': [1, 2, 3]})

    # Had to be set to dict to trigger difference in data contents. Validation for some reason
    # harmonised the data contents to list[MyInt] even though the model itself keeps the data
    # as MyIntList if provided in that form
    as_list_of_myints_dataset = Dataset[Model[MyIntList | list[MyInt]]]({'file_1': [1, 2, 3]})
    as_myintlist_dataset = Dataset[Model[MyIntList | list[MyInt]]]()
    as_myintlist_dataset.data['file_1'] = MyIntList([1, 2, 3])

    assert as_list_of_myints_dataset != as_myintlist_dataset

    assert Dataset[Model[MyIntList | list[MyInt]]]({'file_1': [1, 2, 3]}) == \
           Dataset[Model[Union[MyIntList, list[MyInt]]]]({'file_1': [1, 2, 3]})

    assert Dataset[Model[MyIntList | list[MyInt]]]({'file_1': [1, 2, 3]}).to_data() == \
           Dataset[Model[MyIntList | list[MyInt]]]({'file_1': MyIntList([1, 2, 3])}).to_data()


def test_equality_with_pydantic() -> None:
    class PydanticModel(BaseModel):
        a: int = 0

    class EqualPydanticModel(BaseModel):
        a: int = 0

    assert Dataset[Model[PydanticModel]]({'file_1': {'a': 1}}) == \
           Dataset[Model[PydanticModel]]({'file_1': {'a': 1.0}})

    assert Dataset[Model[PydanticModel]]({'file_1': {'a': 1}}) != \
           Dataset[Model[EqualPydanticModel]]({'file_1': {'a': 1}})


def test_basic_validation():
    dataset_1 = Dataset[Model[PositiveInt]]()

    dataset_1['obj_type_1'] = 123

    with pytest.raises(ValueError):
        dataset_1['obj_type_2'] = -234

    with pytest.raises(ValueError):
        Dataset[Model[List[StrictInt]]]([12.4, 11])  # noqa


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

    assert dataset.to_json(pretty=False) == {
        'obj_type_1': '{"a": "123", "b": "234", "c": "345"}', 'obj_type_2': '{"c": "456"}'
    }
    assert dataset.to_json(pretty=True) == {
        'obj_type_1': '{\n    "a": "123",\n    "b": "234",\n    "c": "345"\n}',
        'obj_type_2': '{\n    "c": "456"\n}'
    }

    data = {'obj_type_1': {'a': 333, 'b': 555, 'c': 777}, 'obj_type_3': {'a': '99', 'b': '98'}}
    dataset.from_data(data)

    assert dataset.to_data() == {
        'obj_type_1': {
            'a': '333', 'b': '555', 'c': '777'
        },
        'obj_type_2': {
            'c': '456'
        },
        'obj_type_3': {
            'a': '99', 'b': '98'
        }
    }

    data = {'obj_type_1': {'a': 167, 'b': 761}}
    dataset.from_data(data, update=False)

    assert dataset.to_data() == {
        'obj_type_1': {
            'a': '167', 'b': '761'
        },
    }

    json_import = {'obj_type_2': '{"a": 987, "b": 654}'}

    dataset.from_json(json_import)
    assert dataset.to_data() == {
        'obj_type_1': {
            'a': '167', 'b': '761'
        }, 'obj_type_2': {
            'a': '987', 'b': '654'
        }
    }

    dataset.from_json(json_import, update=False)
    assert dataset.to_data() == {'obj_type_2': {'a': '987', 'b': '654'}}

    json_import = (
        ('obj_type_2', '{"a": 987, "b": 654}'),
        ('obj_type_3', '{"b": 222, "c": 333}'),
    )
    dataset.from_json(json_import)
    assert dataset.to_data() == {
        'obj_type_2': {
            'a': '987', 'b': '654'
        }, 'obj_type_3': {
            'b': '222', 'c': '333'
        }
    }

    assert dataset.to_json_schema(pretty=False) == (  # noqa
        '{"title": "Dataset[Model[Dict[str, str]]]", "description": "'
        + Dataset._get_standard_field_description()
        + '", "default": {}, "type": "object", "additionalProperties": '
        '{"$ref": "#/definitions/Model_Dict_str__str__"}, "definitions": '
        '{"Model_Dict_str__str__": {"title": "Model[Dict[str, str]]", '
        '"description": "' + Model._get_standard_field_description()
        + '", "type": "object", "additionalProperties": {"type": "string"}}}}')

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
            "type": "object",
            "additionalProperties": {
                "type": "string"
            }
        }
    }
}'''  # noqa

    assert dataset.to_json() == dataset.to_json(pretty=False)  # noqa
    assert dataset.to_json_schema() == dataset.to_json_schema(pretty=False)  # noqa


def test_import_export_custom_parser_to_other_type():
    dataset = Dataset[StringToLength]()

    dataset['obj_type_1'] = 'And we lived beneath the waves'
    assert dataset['obj_type_1'] == 30

    dataset.from_data({'obj_type_2': 'In our yellow submarine'}, update=True)  # noqa
    assert dataset['obj_type_1'] == 30
    assert dataset['obj_type_2'] == 23
    assert dataset.to_data() == {'obj_type_1': 30, 'obj_type_2': 23}

    dataset.from_json({'obj_type_2': '"In our yellow submarine!"'}, update=True)  # noqa
    assert dataset['obj_type_1'] == 30
    assert dataset['obj_type_2'] == 24
    assert dataset.to_json() == {'obj_type_1': '30', 'obj_type_2': '24'}

    assert dataset.to_json_schema(pretty=True) == '''
{
    "title": "Dataset[StringToLength]",
    "description": "'''[1:] + Dataset._get_standard_field_description() + '''",
    "default": {},
    "type": "object",
    "additionalProperties": {
        "$ref": "#/definitions/StringToLength"
    },
    "definitions": {
        "StringToLength": {
            "title": "StringToLength",
            "description": "''' + Model._get_standard_field_description() + '''",
            "type": "string"
        }
    }
}'''  # noqa


def test_complex_models():
    #
    # Model subclass
    #

    class MyRangeList(Model[List[PositiveInt]]):
        """
        Transforms a pair of min and max ints to an inclusive range
        """
        @classmethod
        def _parse_data(cls, data: List[PositiveInt]) -> List[PositiveInt]:
            if not data:
                return []
            else:
                assert len(data) == 2
                return list(range(data[0], data[1] + 1))

    #
    # Generic model subclass
    #

    ListT = TypeVar('ListT', bound=List)  # noqa

    # Note that the TypeVars need to be bound to a type who in itself, or whose origin_type
    # produces a default value when called without parameters. Here, `listT` is bound to List,
    # and `typing.get_origin(List)() == []`.

    class MyReversedListModel(Model[ListT], Generic[ListT]):
        # Commented out docstring, due to test_json_schema_generic_models_known_issue in test_model
        # in order to make this test independent on that issue.
        #
        # TODO: Revisit MyReversedListModel comment if test_json_schema_generic_models_known_issue
        #       is fixed
        #
        # """
        # Generic model that sorts any list in reverse order.
        # """
        @classmethod
        def _parse_data(cls, data: List) -> List:
            if isinstance(data, Model):
                data = data.to_data()
            return list(reversed(sorted(data)))

    #
    # Nested complex model
    #

    class MyReversedRangeList(Dataset[MyReversedListModel[MyRangeList]]):
        ...

    dataset = MyReversedRangeList()

    with pytest.raises(ValidationError):
        dataset.from_data([(i, [0, i]) for i in range(0, 5)])  # noqa

    dataset.from_data([(i, [1, i]) for i in range(1, 5)])  # noqa
    assert dataset['4'] == [4, 3, 2, 1]

    assert dataset.to_data() == {'1': [1], '2': [2, 1], '3': [3, 2, 1], '4': [4, 3, 2, 1]}

    assert dataset.to_json(pretty=False) == {
        '1': '[1]', '2': '[2, 1]', '3': '[3, 2, 1]', '4': '[4, 3, 2, 1]'
    }

    assert dataset.to_json(pretty=True) == {
        '1': '[\n    1\n]',
        '2': '[\n    2,\n    1\n]',
        '3': '[\n    3,\n    2,\n    1\n]',
        '4': '[\n    4,\n    3,\n    2,\n    1\n]'
    }

    assert dataset.to_json_schema(pretty=True) == '''
{
    "title": "MyReversedRangeList",
    "description": "'''[1:] + Dataset._get_standard_field_description() + '''",
    "default": {},
    "type": "object",
    "additionalProperties": {
        "$ref": "#/definitions/MyReversedListModel_MyRangeList_"
    },
    "definitions": {
        "MyRangeList": {
            "title": "MyRangeList",
            "description": "Transforms a pair of min and max ints to an inclusive range",
            "type": "array",
            "items": {
                "type": "integer",
                "exclusiveMinimum": 0
            }
        },
        "MyReversedListModel_MyRangeList_": {
            "title": "MyReversedListModel[MyRangeList]",
            "description": "''' + Model._get_standard_field_description() + '''",
            "allOf": [
                {
                    "$ref": "#/definitions/MyRangeList"
                }
            ]
        }
    }
}'''  # noqa


def test_dataset_model_class():
    assert Dataset[Model[int]]().get_model_class() == Model[int]
    assert Dataset[Model[str]]().get_model_class() == Model[str]
    assert Dataset[Model[List[float]]]().get_model_class() == Model[List[float]]
    assert Dataset[Model[Dict[int, str]]]().get_model_class() == Model[Dict[int, str]]


# TODO: Add unit tests for MultiModelDataset
