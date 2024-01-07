import os
from textwrap import dedent
from types import NoneType
from typing import Any, Generic, List, Optional, TypeAlias, TypeVar, Union

from pydantic import BaseModel, PositiveInt, StrictInt, ValidationError
import pytest

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from .helpers.datasets import DefaultStrDataset, UpperStrDataset
from .helpers.models import StringToLength


def test_no_model():
    with pytest.raises(TypeError):
        Dataset()

    with pytest.raises(TypeError):
        Dataset({'file_1': 123, 'file_2': 234})

    with pytest.raises(TypeError):

        class MyDataset(Dataset):
            ...

        MyDataset()

    with pytest.raises(TypeError):
        Dataset[int]()

    with pytest.raises(TypeError):

        class MyDataset(Dataset[list[str]]):
            ...

        MyDataset()


def test_init_with_basic_parsing() -> None:
    dataset_1 = Dataset[Model[int]]()

    dataset_1['data_file_1'] = 123
    dataset_1['data_file_2'] = 456

    assert len(dataset_1) == 2
    assert dataset_1['data_file_1'] == Model[int](123)
    assert dataset_1['data_file_2'].contents == 456

    dataset_2 = Dataset[Model[int]]({
        'data_file_1': 456.5, 'data_file_2': '789', 'data_file_3': True
    })

    assert len(dataset_2) == 3
    assert dataset_2['data_file_1'].contents == 456
    assert dataset_2['data_file_2'].contents == 789
    assert dataset_2['data_file_3'].contents == 1

    dataset_3 = Dataset[Model[str]]([('data_file_1', 'abc'), ('data_file_2', 123),
                                     ('data_file_3', True)])

    assert len(dataset_3) == 3
    assert dataset_3['data_file_1'].contents == 'abc'
    assert dataset_3['data_file_2'].contents == '123'
    assert dataset_3['data_file_3'].contents == 'True'

    dataset_4 = Dataset[Model[dict[int, int]]](
        data_file_1={
            1: 1234, 2: 2345
        }, data_file_2={
            2: 2345, 3: 3456
        })

    assert len(dataset_4) == 2
    assert dataset_4['data_file_1'].contents == {1: 1234, 2: 2345}
    assert dataset_4['data_file_2'].contents == {2: 2345, 3: 3456}


def test_init_errors():
    with pytest.raises(TypeError):
        Dataset[Model[int]]({'data_file_1': 123}, {'data_file_2': 234})

    with pytest.raises(AssertionError):
        Dataset[Model[int]]({'data_file_1': 123}, data={'data_file_2': 234})

    with pytest.raises(AssertionError):
        Dataset[Model[int]]({'data_file_1': 123}, data_file_2=234)

    with pytest.raises(AssertionError):
        Dataset[Model[int]](data={'data_file_1': 123}, data_file_2=234)

    with pytest.raises(ValidationError):
        Dataset[Model[int]](data=123)


def test_parsing_none_allowed():
    class NoneModel(Model[NoneType]):
        ...

    assert Dataset[NoneModel]({'a': None}).to_data() == {'a': None}

    with pytest.raises(ValidationError):
        Dataset[NoneModel]({'a': 'None'})

    class MaybeNumberModelOptional(Model[Optional[int]]):
        ...

    class MaybeNumberModelUnion(Model[int | None]):
        ...

    class MaybeNumberModelUnionNew(Model[int | None]):
        ...

    for model_cls in [MaybeNumberModelOptional, MaybeNumberModelUnion, MaybeNumberModelUnionNew]:
        # for model_cls in [MaybeNumberModelOptional, MaybeNumberModelUnion]:
        assert Dataset[model_cls]({'a': None, 'b': 13}).to_data() == {'a': None, 'b': 13}

        with pytest.raises(ValidationError):
            Dataset[model_cls]({'a': 'None'})


def test_parsing_none_not_allowed():
    class IntListModel(Model[list[int]]):
        ...

    class IntDictModel(Model[dict[int, int]]):
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

    dataset = Dataset[Model[str]]({'data_file_1': 123, 'data_file_2': 234})

    assert list(dataset.keys()) == ['data_file_1', 'data_file_2']
    assert list(dataset.values()) == [Model[str]('123'), Model[str]('234')]
    assert list(dataset.items()) == [('data_file_1', Model[str]('123')),
                                     ('data_file_2', Model[str]('234'))]

    dataset['data_file_2'] = 345

    assert len(dataset) == 2
    assert dataset['data_file_1'].contents == '123'
    assert dataset['data_file_2'].contents == '345'

    del dataset['data_file_1']
    assert len(dataset) == 1
    assert dataset['data_file_2'].contents == '345'

    with pytest.raises(KeyError):
        assert dataset['data_file_3']

    dataset.update({'data_file_2': 456, 'data_file_3': 567})
    assert dataset['data_file_2'].contents == '456'
    assert dataset['data_file_3'].contents == '567'

    dataset.setdefault('data_file_3', 789)
    assert dataset.get('data_file_3').contents == '567'

    dataset.setdefault('data_file_4', 789)
    assert dataset.get('data_file_4').contents == '789'

    assert dataset.fromkeys(['data_file_1', 'data_file_2'], 321) == \
        Dataset[Model[str]](data_file_1='321', data_file_2='321')

    assert len(dataset) == 3

    dataset.pop('data_file_3')
    assert len(dataset) == 2

    # UserDict() implementation of popitem pops items FIFO contrary of the LIFO specified
    # in the standard library: https://docs.python.org/3/library/stdtypes.html#dict.popitem
    dataset.popitem()
    assert len(dataset) == 1
    assert dataset.to_data() == {'data_file_4': '789'}

    dataset.clear()
    assert len(dataset) == 0
    assert dataset.to_data() == {}


def test_get_item_with_int_and_slice() -> None:
    dataset = Dataset[Model[int]](data_file_1=123, data_file_2=456, data_file_3=789)
    assert dataset[0] == dataset['data_file_1'] == Model[int](123)
    assert dataset[1] == dataset['data_file_2'] == Model[int](456)
    assert dataset[2] == dataset[-1] == dataset['data_file_3'] == Model[int](789)

    assert dataset[0:2] == Dataset[Model[int]](data_file_1=dataset['data_file_1'],
                                               data_file_2=dataset['data_file_2']) \
           == Dataset[Model[int]](data_file_1=123, data_file_2=456)
    assert dataset[-1:] == dataset[2:3] == Dataset[Model[int]](data_file_3=dataset['data_file_3']) \
           == Dataset[Model[int]](data_file_3=789)
    assert dataset[:] == dataset
    assert dataset[1:1] == Dataset[Model[int]]()

    with pytest.raises(IndexError):
        dataset[3]

    assert dataset[2:4] == Dataset[Model[int]](data_file_3=dataset['data_file_3']) \
           == Dataset[Model[int]](data_file_3=789)


def test_get_items_with_tuple_or_list() -> None:
    dataset = Dataset[Model[int]](data_file_1=123, data_file_2=456, data_file_3=789)

    assert dataset[()] == dataset[[]] == Dataset[Model[int]]()
    assert dataset[0,] == dataset[(0,)] == dataset[[0]] \
           == dataset['data_file_1',] == dataset[('data_file_1',)] == dataset[['data_file_1']] \
           == Dataset[Model[int]](data_file_1=123)
    assert dataset[0, 2] == dataset[(0, 2)] == dataset[[0, 2]] \
           == dataset['data_file_1', 'data_file_3'] == dataset[('data_file_1', 'data_file_3')] \
           == dataset[['data_file_1', 'data_file_3']] == dataset[[0, 'data_file_3']] \
           == Dataset[Model[int]](data_file_1=dataset['data_file_1'],
                                  data_file_3=dataset['data_file_3']) \
           == Dataset[Model[int]](data_file_1=123, data_file_3=789)

    with pytest.raises(IndexError):
        dataset[0, 3]

    with pytest.raises(KeyError):
        dataset[0, 'data_file_4']

    with pytest.raises(IndexError):
        dataset[[0, 3]]


def test_equality() -> None:
    assert Dataset[Model[list[int]]]({'data_file_1': [1, 2, 3], 'data_file_2': [1.0, 2.0, 3.0]}) \
           == Dataset[Model[list[int]]]({'data_file_1': [1.0, 2.0, 3.0], 'data_file_2': [1, 2, 3]})

    assert Dataset[Model[list[int]]]({'data_file_1': [1, 2, 3], 'data_file_2': [1, 2, 3]}) \
           != Dataset[Model[list[int]]]({'data_file_1': [1, 2, 3], 'data_file_2': [3, 2, 1]})

    assert Dataset[Model[list[int]]]({'1': [1, 2, 3]}) \
           == Dataset[Model[list[int]]]({1: [1, 2, 3]})

    assert Dataset[Model[list[int]]]({'data_file_1': [1, 2, 3]}) \
           != Dataset[Model[list[float]]]({'data_file_1': [1.0, 2.0, 3.0]})


def test_complex_equality() -> None:
    class MyIntList(Model[list[int]]):
        ...

    class MyInt(Model[int]):
        ...

    assert Dataset[Model[list[int]]]({'data_file_1': [1, 2, 3]}) != \
           Dataset[MyIntList]({'data_file_1': [1, 2, 3]})

    assert Dataset[Model[MyIntList]]({'data_file_1': [1, 2, 3]}) == \
           Dataset[Model[MyIntList]]({'data_file_1': MyIntList([1, 2, 3])})

    assert Dataset[Model[list[MyInt]]]({'data_file_1': [1, 2, 3]}) == \
           Dataset[Model[list[MyInt]]]({'data_file_1': list[MyInt]([1, 2, 3])})

    assert Dataset[Model[list[MyInt]]]({'data_file_1': [1, 2, 3]}) != \
           Dataset[Model[List[MyInt]]]({'data_file_1': [1, 2, 3]})

    # Had to be set to dict to trigger difference in data contents. Validation for some reason
    # harmonised the data contents to list[MyInt] even though the model itself keeps the data
    # as MyIntList if provided in that form
    as_list_of_myints_dataset = Dataset[Model[MyIntList | list[MyInt]]]({'data_file_1': [1, 2, 3]})
    as_myintlist_dataset = Dataset[Model[MyIntList | list[MyInt]]]()
    as_myintlist_dataset.data['data_file_1'] = MyIntList([1, 2, 3])

    assert as_list_of_myints_dataset != as_myintlist_dataset

    assert Dataset[Model[MyIntList | list[MyInt]]]({'data_file_1': [1, 2, 3]}) == \
           Dataset[Model[Union[MyIntList, list[MyInt]]]]({'data_file_1': [1, 2, 3]})

    assert Dataset[Model[MyIntList | list[MyInt]]]({'data_file_1': [1, 2, 3]}).to_data() == \
           Dataset[Model[MyIntList | list[MyInt]]]({'data_file_1': MyIntList([1, 2, 3])}).to_data()


def test_equality_with_pydantic() -> None:
    class PydanticModel(BaseModel):
        a: int = 0

    class EqualPydanticModel(BaseModel):
        a: int = 0

    assert Dataset[Model[PydanticModel]]({'data_file_1': {'a': 1}}) == \
           Dataset[Model[PydanticModel]]({'data_file_1': {'a': 1.0}})

    assert Dataset[Model[PydanticModel]]({'data_file_1': {'a': 1}}) != \
           Dataset[Model[EqualPydanticModel]]({'data_file_1': {'a': 1}})


ChildT = TypeVar('ChildT', bound=object)


class ParentGenericDataset(Dataset[Model[Optional[ChildT]]], Generic[ChildT]):
    ...


ParentDataset: TypeAlias = ParentGenericDataset['NumberModel']
ParentDatasetNested: TypeAlias = ParentGenericDataset[Union[Model[str], 'NumberModel']]


class NumberModel(Model[int]):
    ...


ParentDataset.update_forward_refs(NumberModel=NumberModel)
ParentDatasetNested.update_forward_refs(NumberModel=NumberModel)


def test_qualname():
    assert Model[int].__qualname__ == 'Model[int]'
    assert Model[Model[int]].__qualname__ == 'Model[omnipy.data.model.Model[int]]'
    assert ParentDataset.__qualname__ == 'ParentGenericDataset[NumberModel]'
    assert ParentDatasetNested.__qualname__ \
           == 'ParentGenericDataset[Union[Model[str], NumberModel]]'


def test_repr():
    assert repr(Dataset[Model[int]]) == \
           "<class 'omnipy.data.dataset.Dataset[omnipy.data.model.Model[int]]'>"
    assert repr(Dataset[Model[int]](a=5, b=7)) == 'Dataset[Model[int]](a=5, b=7)'
    assert repr(Dataset[Model[int]]({'a': 5, 'b': 7})) == 'Dataset[Model[int]](a=5, b=7)'
    assert repr(Dataset[Model[int]](data={'a': 5, 'b': 7})) == 'Dataset[Model[int]](a=5, b=7)'
    assert repr(Dataset[Model[int]]([('a', 5), ('b', 7)])) == 'Dataset[Model[int]](a=5, b=7)'
    assert repr(Dataset[Model[int]](data=[('a', 5), ('b', 7)])) == 'Dataset[Model[int]](a=5, b=7)'

    assert repr(Dataset[Model[Model[int]]]) \
           == "<class 'omnipy.data.dataset.Dataset[omnipy.data.model.Model[Model[int]]]'>"
    assert repr(Dataset[Model[Model[int]]](a=Model[int](5))) \
           == 'Dataset[Model[Model[int]]](a=Model[int](5))'

    assert repr(ParentDataset) \
           == "<class 'tests.data.test_dataset.ParentGenericDataset[NumberModel]'>"
    assert repr(ParentDataset(a=NumberModel(5))) \
           == 'ParentGenericDataset[NumberModel](a=NumberModel(5))'

    assert repr(ParentDatasetNested) == ("<class 'tests.data.test_dataset.ParentGenericDataset"
                                         "[Union[Model[str], NumberModel]]'>")
    assert repr(ParentDatasetNested(a='abc')) \
           == "ParentGenericDataset[Union[Model[str], NumberModel]](a=Model[str]('abc'))"


def test_basic_validation():
    dataset_1 = Dataset[Model[PositiveInt]]()

    dataset_1['data_file_1'] = 123

    with pytest.raises(ValueError):
        dataset_1['data_file_2'] = -234

    with pytest.raises(ValueError):
        Dataset[Model[list[StrictInt]]]([12.4, 11])  # noqa


def test_import_and_export():
    dataset = Dataset[Model[dict[str, str]]]()

    data = {'data_file_1': {'a': 123, 'b': 234, 'c': 345}, 'data_file_2': {'c': 456}}
    dataset.from_data(data)

    assert dataset['data_file_1'].contents == {'a': '123', 'b': '234', 'c': '345'}
    assert dataset['data_file_2'].contents == {'c': '456'}

    assert dataset.to_data() == {
        'data_file_1': {
            'a': '123', 'b': '234', 'c': '345'
        }, 'data_file_2': {
            'c': '456'
        }
    }

    assert dataset.to_json(pretty=False) == {
        'data_file_1': '{"a": "123", "b": "234", "c": "345"}', 'data_file_2': '{"c": "456"}'
    }
    assert dataset.to_json(pretty=True) == {
        'data_file_1':
            dedent("""\
            {
              "a": "123",
              "b": "234",
              "c": "345"
            }"""),
        'data_file_2':
            dedent("""\
            {
              "c": "456"
            }""")
    }

    data = {'data_file_1': {'a': 333, 'b': 555, 'c': 777}, 'data_file_3': {'a': '99', 'b': '98'}}
    dataset.from_data(data)

    assert dataset.to_data() == {
        'data_file_1': {
            'a': '333', 'b': '555', 'c': '777'
        },
        'data_file_2': {
            'c': '456'
        },
        'data_file_3': {
            'a': '99', 'b': '98'
        }
    }

    data = {'data_file_1': {'a': 167, 'b': 761}}
    dataset.from_data(data, update=False)

    assert dataset.to_data() == {
        'data_file_1': {
            'a': '167', 'b': '761'
        },
    }

    json_import = {'data_file_2': '{"a": 987, "b": 654}'}

    dataset.from_json(json_import)
    assert dataset.to_data() == {
        'data_file_1': {
            'a': '167', 'b': '761'
        }, 'data_file_2': {
            'a': '987', 'b': '654'
        }
    }

    dataset.from_json(json_import, update=False)
    assert dataset.to_data() == {'data_file_2': {'a': '987', 'b': '654'}}

    json_import = (
        ('data_file_2', '{"a": 987, "b": 654}'),
        ('data_file_3', '{"b": 222, "c": 333}'),
    )
    dataset.from_json(json_import)
    assert dataset.to_data() == {
        'data_file_2': {
            'a': '987', 'b': '654'
        }, 'data_file_3': {
            'b': '222', 'c': '333'
        }
    }

    assert dataset.to_json_schema(pretty=False) == (  # noqa
        '{"title": "Dataset[Model[dict[str, str]]]", "description": "'
        + Dataset._get_standard_field_description()
        + '", "default": {}, "type": "object", "additionalProperties": '
        '{"$ref": "#/definitions/Model_dict_str__str__"}, "definitions": '
        '{"Model_dict_str__str__": {"title": "Model[dict[str, str]]", '
        '"description": "' + Model._get_standard_field_description()
        + '", "type": "object", "additionalProperties": {"type": "string"}}}}')

    assert dataset.to_json_schema(pretty=True) == dedent('''\
    {
      "title": "Dataset[Model[dict[str, str]]]",
      "description": "''' + Dataset._get_standard_field_description() + '''",
      "default": {},
      "type": "object",
      "additionalProperties": {
        "$ref": "#/definitions/Model_dict_str__str__"
      },
      "definitions": {
        "Model_dict_str__str__": {
          "title": "Model[dict[str, str]]",
          "description": "''' + Model._get_standard_field_description() + '''",
          "type": "object",
          "additionalProperties": {
            "type": "string"
          }
        }
      }
    }''')  # noqa: Q001

    assert dataset.to_json() == dataset.to_json(pretty=True)  # noqa
    assert dataset.to_json_schema() == dataset.to_json_schema(pretty=True)  # noqa


def test_import_export_custom_parser_to_other_type():
    dataset = Dataset[StringToLength]()

    dataset['data_file_1'] = 'And we lived beneath the waves'
    assert dataset['data_file_1'].contents == 30

    dataset.from_data({'data_file_2': 'In our yellow submarine'}, update=True)  # noqa
    assert dataset['data_file_1'].contents == 30
    assert dataset['data_file_2'].contents == 23
    assert dataset.to_data() == {'data_file_1': 30, 'data_file_2': 23}

    dataset.from_json({'data_file_2': '"In our yellow submarine!"'}, update=True)  # noqa
    assert dataset['data_file_1'].contents == 30
    assert dataset['data_file_2'].contents == 24
    assert dataset.to_json() == {'data_file_1': '30', 'data_file_2': '24'}

    assert dataset.to_json_schema(pretty=True) == dedent('''\
    {
      "title": "Dataset[StringToLength]",
      "description": "''' + Dataset._get_standard_field_description() + '''",
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
    }''')  # noqa: Q001


def test_generic_dataset_unbound_typevar():
    # Note that the TypeVars for generic Dataset classes do not need to be bound, in contrast to
    # TypeVars used for generic Model classes (see test_generic_dataset_bound_typevar() below).
    # Here the TypeVar is used to specialize `tuple` and `list`, not `Model`, and does not need to
    # be bound.
    _DatasetValT = TypeVar('DatasetValT')

    class MyTupleOrListDataset(Dataset[Model[tuple[_DatasetValT, ...] | list[_DatasetValT]]],
                               Generic[_DatasetValT]):
        ...

    # Without further restrictions

    assert MyTupleOrListDataset().to_data() == {}
    assert MyTupleOrListDataset({'a': (123, 'a')})['a'].contents == (123, 'a')
    assert MyTupleOrListDataset({'a': [True, False]})['a'].contents == [True, False]

    with pytest.raises(ValidationError):
        MyTupleOrListDataset({'a': 123})

    with pytest.raises(ValidationError):
        MyTupleOrListDataset({'a': 'abc'})

    with pytest.raises(ValidationError):
        MyTupleOrListDataset({'a': {'x': 123}})

    # Restricting the contents of the tuples and lists

    assert MyTupleOrListDataset[int]({'a': (123, '456')})['a'].contents == (123, 456)
    assert MyTupleOrListDataset[bool]({'a': [False, 1, '0']})['a'].contents == [False, True, False]

    with pytest.raises(ValidationError):
        MyTupleOrListDataset[int]({'a': (123, 'abc')})


def test_generic_dataset_bound_typevar():
    # Note that the TypeVars for generic Model classes need to be bound to a type who in itself, or
    # whose origin_type produces a default value when called without parameters. Here, `ValT` is
    # bound to `int | str`, and `typing.get_origin(int | str)() == 0`.
    _ModelValT = TypeVar('_ModelValT', bound=int | str)

    class MyListOfIntsOrStringsModel(Model[list[_ModelValT]], Generic[_ModelValT]):
        ...

    # Since we in this case are just passing on the TypeVar to the Model, mypy will complain if the
    # TypeVar is also not bound for the Dataset, however Dataset in itself do not require the
    # TypeVar to be bound (see test_generic_dataset_unbound_typevar() above).
    class MyListOfIntsOrStringsDataset(Dataset[MyListOfIntsOrStringsModel[_ModelValT]],
                                       Generic[_ModelValT]):
        ...

    assert MyListOfIntsOrStringsDataset().to_data() == {}

    assert MyListOfIntsOrStringsDataset({'a': (123, 'a')})['a'].contents == [123, 'a']
    assert MyListOfIntsOrStringsDataset({'a': [True, False]})['a'].contents == [1, 0]

    with pytest.raises(ValidationError):
        MyListOfIntsOrStringsDataset({'a': 123})

    with pytest.raises(ValidationError):
        MyListOfIntsOrStringsDataset({'a': 'abc'})

    with pytest.raises(ValidationError):
        MyListOfIntsOrStringsDataset({'a': {'x': 123}})

    # Further restricting the contents of the tuples and lists
    assert MyListOfIntsOrStringsDataset[str]({'a': (123, '456')})['a'].contents == ['123', '456']
    assert MyListOfIntsOrStringsDataset[int]({'a': (123, '456')})['a'].contents == [123, 456]

    with pytest.raises(ValidationError):
        MyListOfIntsOrStringsDataset[int]({'a': (123, 'abc')})

    # Note that the following override of the TypeVar binding will work in runtime, but mypy will
    # produce an error
    assert MyListOfIntsOrStringsDataset[list]().to_data() == {}  # type: ignore


def test_generic_dataset_two_typevars():
    # Here the TypeVars do not need to be bound, as they are used to specialize `dict`, not `Model`.
    _KeyT = TypeVar('_KeyT')
    _ValT = TypeVar('_ValT')

    class MyFilledDictModel(Model[dict[_KeyT, _ValT]], Generic[_KeyT, _ValT]):
        @classmethod
        def _parse_data(cls, data: dict[_KeyT, _ValT]) -> Any:
            assert len(data) > 0
            return data

    class MyFilledDictDataset(Dataset[MyFilledDictModel[_KeyT, _ValT]], Generic[_KeyT, _ValT]):
        ...

    # Without further restrictions

    assert MyFilledDictDataset().to_data() == {}
    assert MyFilledDictDataset({'a': {1: 123}, 'b': {'x': 'abc', 'y': '123'}}).to_data() == \
           {'a': {1: 123}, 'b': {'x': 'abc', 'y': '123'}}

    with pytest.raises(ValidationError):
        MyFilledDictDataset({'a': 123})

    with pytest.raises(ValidationError):
        MyFilledDictDataset({'a': 'abc'})

    with pytest.raises(ValidationError):
        MyFilledDictDataset({'a': {'x': 123}, 'b': {}})

    # Restricting the key and value types

    assert MyFilledDictDataset[int, int]({'a': {1: 123}, 'b': {'2': '456'}}).to_data() == \
           {'a': {1: 123}, 'b': {2: 456}}
    assert MyFilledDictDataset[int, str]({'a': {1: 123}, 'b': {'2': '456'}}).to_data() == \
           {'a': {1: '123'}, 'b': {2: '456'}}
    assert MyFilledDictDataset[str, int]({'a': {1: 123}, 'b': {'2': '456'}}).to_data() == \
           {'a': {'1': 123}, 'b': {'2': 456}}
    assert MyFilledDictDataset[str, str]({'a': {1: 123}, 'b': {'2': '456'}}).to_data() == \
           {'a': {'1': '123'}, 'b': {'2': '456'}}


def test_complex_models():
    #
    # Model subclass
    #

    class MyRangeList(Model[list[PositiveInt]]):
        """
        Transforms a pair of min and max ints to an inclusive range
        """
        @classmethod
        def _parse_data(cls, data: list[PositiveInt]) -> list[PositiveInt]:
            if not data:
                return []
            else:
                assert len(data) == 2
                return list(range(data[0], data[1] + 1))

    #
    # Generic model subclass
    #

    ListT = TypeVar('ListT', bound=list)  # noqa

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
        def _parse_data(cls, data: list) -> list:
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
    assert dataset['4'].contents == [4, 3, 2, 1]

    assert dataset.to_data() == {'1': [1], '2': [2, 1], '3': [3, 2, 1], '4': [4, 3, 2, 1]}

    assert dataset.to_json(pretty=False) == {
        '1': '[1]', '2': '[2, 1]', '3': '[3, 2, 1]', '4': '[4, 3, 2, 1]'
    }

    assert dataset.to_json(pretty=True) == {
        '1':
            dedent("""\
            [
              1
            ]"""),
        '2':
            dedent("""\
            [
              2,
              1
            ]"""),
        '3':
            dedent("""\
            [
              3,
              2,
              1
            ]"""),
        '4':
            dedent("""\
            [
              4,
              3,
              2,
              1
            ]""")
    }

    assert dataset.to_json_schema(pretty=True) == dedent('''\
    {
      "title": "MyReversedRangeList",
      "description": "''' + Dataset._get_standard_field_description() + '''",
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
    }''')  # noqa: Q001


def test_dataset_model_class():
    assert Dataset[Model[int]]().get_model_class() == Model[int]
    assert Dataset[Model[str]]().get_model_class() == Model[str]
    assert Dataset[Model[list[float]]]().get_model_class() == Model[list[float]]
    assert Dataset[Model[dict[int, str]]]().get_model_class() == Model[dict[int, str]]


def test_dataset_switch_models_issue():
    dataset = Dataset[Model[int]]({'a': 123, 'b': 234})
    dataset['a'], dataset['b'] = dataset['b'], dataset['a']

    dataset = Dataset[Model[Model[int]]]({'a': 123, 'b': 234})
    dataset['a'], dataset['b'] = dataset['b'], dataset['a']

    dataset = Dataset[Model[list[int]]]({'a': [123], 'b': [234]})
    dataset['a'], dataset['b'] = dataset['b'], dataset['a']

    dataset = Dataset[Model[Model[list[int]]]]({'a': [123], 'b': [234]})
    dataset['a'], dataset['b'] = dataset['b'], dataset['a']


# TODO: Add unit tests for MultiModelDataset


def test_parametrized_dataset():
    assert UpperStrDataset(dict(x='foo'))['x'].contents == 'foo'
    assert UpperStrDataset(dict(x='bar'), upper=True)['x'].contents == 'BAR'
    assert UpperStrDataset(dict(x='foo', y='bar'), upper=True).to_data() == dict(x='FOO', y='BAR')

    dataset = UpperStrDataset()
    dataset['x'] = 'foo'
    assert dataset['x'].contents == 'foo'

    dataset.from_data(dict(y='bar', z='foobar'), upper=True)
    assert dataset.to_data() == dict(x='foo', y='BAR', z='FOOBAR')

    dataset.from_data(dict(y='bar', z='foobar'), update=False)
    assert dataset.to_data() == dict(y='bar', z='foobar')

    dataset.from_json(dict(x='"foo"'), upper=True)
    assert dataset.to_data() == dict(x='FOO', y='bar', z='foobar')

    dataset.from_json(dict(x='"foo"'), update=False)
    assert dataset.to_data() == dict(x='foo')

    with pytest.raises(KeyError):
        UpperStrDataset(dict(x='bar'), upper=True)['upper']
    with pytest.raises(AssertionError):
        assert UpperStrDataset(x='bar', upper=True)


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason='ParamDataset does not support None values yet. Wait until pydantic v2 removes the'
    'Annotated hack to simplify implementation')
def test_parametrized_dataset_with_none():
    with pytest.raises(ValidationError):
        UpperStrDataset(dict(x=None))
    with pytest.raises(ValidationError):
        UpperStrDataset(dict(x=None), upper=True)

    assert DefaultStrDataset(dict(x=None))['x'].contents == 'default'
    assert DefaultStrDataset(dict(x=None), default='other')['x'].contents == 'other'
