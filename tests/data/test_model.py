from types import NoneType
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union

from pydantic import PositiveInt, StrictInt, ValidationError
import pytest

from unifair.data.model import Model


@pytest.mark.skip(reason="""
This test needs to be run as the first test in the test suite in order
not to fail. This is cumbersome. More importantly, it implies that the
functionality is not working correctly. However, it is not meant to work.
Thus, this test is here for documentation purposes only. """)
def test_no_model_known_issue():
    # Note:
    #
    # No model specified defaults to Model[str], but in a highly unstable state that only
    # seem to work until the first typed model is run, after which at least type conversion breaks
    # down. This is due to the fact that typed models interfere through the class variables of
    # the Model class.
    with pytest.raises(TypeError):
        assert Model(12).to_data() == '12'

    with pytest.raises(TypeError):

        class ModelSubclass(Model):
            ...

        assert ModelSubclass(True).to_data() == 'True'

    with pytest.raises(TypeError):
        model = Model()
        model.from_data(12)
        assert model.to_data() == '12'


def test_init_and_data():
    model = Model[int]()
    assert (isinstance(model, Model))
    assert (model.__class__.__name__ == 'Model[int]')

    class StrModel(Model[str]):
        ...

    str_model = StrModel()
    assert (isinstance(str_model, StrModel))
    assert (isinstance(str_model, Model))
    assert (str_model.__class__.__name__ == StrModel.__name__)

    assert Model[int]().to_data() == 0
    assert Model[str]().to_data() == ''
    assert Model[Dict]().to_data() == {}
    assert Model[List]().to_data() == []

    assert Model[int](12).to_data() == 12
    assert Model[str]('test').to_data() == 'test'
    assert Model[Dict]({'a': 2}).to_data() == {'a': 2}
    assert Model[List]([2, 4, 'b', {}]).to_data() == [2, 4, 'b', {}]


def test_load():
    model = Model[int]()
    model.from_data(12)
    assert model.to_data() == 12

    model.from_data(123)
    assert model.to_data() == 123

    assert Model[int](-234).to_data() == -234

    assert Model[int](__root__=-1).to_data() == -1  # for pydantic internals

    with pytest.raises(RuntimeError):
        Model[int](5).__root__ = 12  # noqa

    with pytest.raises(RuntimeError):
        Model[int](5).something = True  # noqa


def test_equality():
    assert Model[int]() == Model[int]()

    model = Model[int]()
    model.from_data(123)
    assert model == Model[int](123)
    assert model != Model[int](234)

    # Equality is only dependent on the data, not the types/model
    assert Model[int](1).to_data() == 1
    assert Model[PositiveInt](1).to_data() == 1
    assert Model[int](1) == Model[PositiveInt](1)


def test_parse_convertible_data():
    NumberModel = Model[int]  # noqa

    model_1 = NumberModel(123.3)
    assert model_1.to_data() == 123

    model_2 = NumberModel()
    model_2.from_data(123.9)
    assert model_2.to_data() == 123

    model_3 = NumberModel('-123')
    assert model_3.to_data() == -123

    model_4 = NumberModel(True)
    assert model_4.to_data() == 1

    assert model_1 == model_2
    assert model_1 != model_3
    assert model_2 != model_4
    assert model_3 != model_4


def test_parse_inconvertible_data():
    class NumberModel(Model[int]):
        ...

    model = NumberModel()

    with pytest.raises(ValidationError):
        model.from_data('fifteen')

    with pytest.raises(ValidationError):
        NumberModel([])


def test_load_data_no_conversion():
    class StrictNumberModel(Model[StrictInt]):
        ...

    model = StrictNumberModel()

    with pytest.raises(ValidationError):
        model.from_data(123.4)

    with pytest.raises(ValidationError):
        model.from_data('234')

    with pytest.raises(ValidationError):
        StrictNumberModel(234.9)

    model.from_data(123)
    assert model == StrictNumberModel(123)


def test_error_invalid_model():

    with pytest.raises(TypeError):

        class DoubleTypesModel(Model[int, str]):  # noqa
            ...


def test_tuple_of_anything():
    class TupleModel(Model[Tuple]):
        ...

    assert TupleModel().to_data() == ()
    assert TupleModel((1, 's', True)).to_data() == (1, 's', True)
    with pytest.raises(ValidationError):
        TupleModel(1)


def test_tuple_of_single_type():
    class TupleModel(Model[Tuple[int]]):
        ...

    assert TupleModel().to_data() == (0,)
    with pytest.raises(ValidationError):
        TupleModel(1)

    with pytest.raises(ValidationError):
        TupleModel((1, 2, 3))

    with pytest.raises(ValidationError):
        TupleModel((1, 's', True))


def test_tuple_of_single_type_repeated():
    class TupleModel(Model[Tuple[int, ...]]):
        ...

    assert TupleModel().to_data() == ()
    assert TupleModel((1, 2, 3)).to_data() == (1, 2, 3)
    with pytest.raises(ValidationError):
        TupleModel(1)

    with pytest.raises(ValidationError):
        TupleModel((1, 's', True))


def test_fixed_tuple_of_different_types():
    class TupleModel(Model[Tuple[int, str]]):
        ...

    assert TupleModel().to_data() == (0, '')
    assert TupleModel((123, 'abc')).to_data() == (123, 'abc')
    assert TupleModel(('123', 123)).to_data() == (123, '123')

    with pytest.raises(ValidationError):
        TupleModel(1)

    with pytest.raises(ValidationError):
        TupleModel((1, 2, 3))

    with pytest.raises(ValidationError):
        TupleModel((1, 's', True))


def test_basic_union():
    # Note: Python 3.10 introduced a shorthand form for Union[TypeA, TypeB]:
    #
    #   TypeA | TypeB
    #
    # The requirements for unifair is currently Python 3.8, so the shorthand should
    # currently be avoided.
    #
    # TODO: Consider whether uniFAIR should require Python 3.9 or 3.10 as type-related
    #       notation and functionality is undergoing large changes. Another example is
    #       the move towards lowercase int, list, dict instead of Int, List, Dict in
    #       Python 3.9. Another possibility is to use
    #       "from __future__ import annotations", which is already used a few places.
    #       Consider also versions requirements for pydantic and mypy (as well as
    #       prefect)
    class UnionModel(Model[Union[int, str, List]]):
        ...

    assert UnionModel(15).to_data() == 15
    assert UnionModel('abc').to_data() == 'abc'
    assert UnionModel([]).to_data() == []


@pytest.mark.skip(reason="""
Known issue due to bug in pydantic (https://github.com/pydantic/pydantic/issues/4474). 
The main functionality tested is working, but the test revealed a bug in pydantic
where the first initiation of Model with a Union of float and int is cached by 
pydantic and defines the order of the second initiation (even though the order of
int and float is the opposite. Works when split into individual tests.
""")
def test_union_default_value_from_first_type_known_issue():
    class IntFirstUnionModel(Model[Union[int, str]]):
        ...

    assert IntFirstUnionModel().to_data() == 0

    class StrFirstUnionModel(Model[Union[str, int]]):
        ...

    assert StrFirstUnionModel().to_data() == ''

    with pytest.raises(TypeError):

        class FirstTypeNotCallableUnionModel(Model[Union[Any, str]]):
            ...


@pytest.mark.skip(reason="""
Fails due to the same pydantic bug as in 'test_union_default_value_from_first_type'
(https://github.com/pydantic/pydantic/issues/4474). Works when split into individual tests.
""")
def test_parsing_independent_on_union_type_order_known_issue():
    class FloatIntUnionModel(Model[Union[float, int]]):
        ...

    assert FloatIntUnionModel(2.0).to_data() == 2.0
    assert type(FloatIntUnionModel(2.0).to_data()) == float

    assert FloatIntUnionModel(15).to_data() == 15
    assert type(FloatIntUnionModel(15).to_data()) == int

    assert FloatIntUnionModel('2.0').to_data() == 2.0
    assert type(FloatIntUnionModel('2.0').to_data()) == float

    assert FloatIntUnionModel('15').to_data() == 15.0
    assert type(FloatIntUnionModel('15').to_data()) == float

    class IntFloatUnionModel(Model[Union[int, float]]):
        ...

    assert IntFloatUnionModel(2.0).to_data() == 2.0
    assert type(IntFloatUnionModel(2.0).to_data()) == float

    assert IntFloatUnionModel(15).to_data() == 15
    assert type(IntFloatUnionModel(15).to_data()) == int

    assert IntFloatUnionModel('2.0').to_data() == 2.0
    assert type(IntFloatUnionModel('2.0').to_data()) == float

    assert IntFloatUnionModel('15').to_data() == 15
    assert type(IntFloatUnionModel('15').to_data()) == int

    class FloatIntStrUnionModel(Model[Union[float, int, str]]):
        ...

    assert FloatIntStrUnionModel(2.0).to_data() == 2.0
    assert type(FloatIntStrUnionModel(2.0).to_data()) == float

    assert FloatIntStrUnionModel(15).to_data() == 15
    assert type(FloatIntStrUnionModel(15).to_data()) == int

    assert FloatIntStrUnionModel('2.0').to_data() == '2.0'
    assert type(FloatIntStrUnionModel('2.0').to_data()) == str

    assert FloatIntStrUnionModel('15').to_data() == '15'
    assert type(FloatIntStrUnionModel('15').to_data()) == str


def test_union_default_value_if_any_none():
    class NoneFirstUnionModel(Model[Union[None, str]]):
        ...

    assert NoneFirstUnionModel().to_data() is None

    class NoneSecondUnionModel(Model[Union[str, None]]):
        ...

    assert NoneFirstUnionModel().to_data() is None


def test_optional():
    class OptionalIntModel(Model[Optional[int]]):
        ...

    assert OptionalIntModel().to_data() is None
    assert OptionalIntModel(None).to_data() is None
    assert OptionalIntModel(13).to_data() == 13
    assert OptionalIntModel('12').to_data() == 12

    with pytest.raises(ValidationError):
        OptionalIntModel([None])

    with pytest.raises(ValidationError):
        OptionalIntModel('None')


def test_nested_union_default_value():
    class NestedUnion(Model[Union[Union[str, int], float]]):
        ...

    assert NestedUnion().to_data() == ''

    class NestedUnionWithOptional(Model[Union[Union[Optional[str], int], float]]):
        ...

    assert NestedUnionWithOptional().to_data() is None

    class NestedUnionWithSingleTypeTuple(Model[Union[Union[Tuple[str], int], float]]):
        ...

    assert NestedUnionWithSingleTypeTuple().to_data() == ('',)


def test_nonetype():
    class NoneModel(Model[NoneType]):
        ...

    assert NoneModel().to_data() is None
    assert NoneModel(None).to_data() is None

    with pytest.raises(ValidationError):
        NoneModel(13)

    with pytest.raises(ValidationError):
        NoneModel('None')


def test_import_export_methods():
    assert Model[int](12).to_data() == 12
    assert Model[str]('test').to_data() == 'test'
    assert Model[Dict]({'a': 2}).to_data() == {'a': 2}
    assert Model[List]([2, 4, 'b']).to_data() == [2, 4, 'b']

    assert Model[int](12).contents == 12
    assert Model[str]('test').contents == 'test'
    assert Model[Dict]({'a': 2}).contents == {'a': 2}
    assert Model[List]([2, 4, 'b']).contents == [2, 4, 'b']

    assert Model[int](12).to_json() == '12'
    assert Model[str]('test').to_json() == '"test"'
    assert Model[Dict]({'a': 2}).to_json() == '{"a": 2}'
    assert Model[List]([2, 4, 'b']).to_json() == '[2, 4, "b"]'

    model_int = Model[int]()
    model_int.from_json('12')
    assert model_int.to_data() == 12

    model_int.contents = '13'
    assert model_int.contents == 13
    assert model_int.to_data() == 13

    model_str = Model[str]()
    model_str.from_json('"test"')
    assert model_str.to_data() == 'test'

    model_str.contents = 13
    assert model_str.contents == '13'
    assert model_str.to_data() == '13'

    model_dict = Model[Dict]()
    model_dict.from_json('{"a": 2}')
    assert model_dict.to_data() == {'a': 2}

    model_dict.contents = {'b': 3}
    assert model_dict.contents == {'b': 3}
    assert model_dict.to_data() == {'b': 3}

    model_list = Model[List]()
    model_list.from_json('[2, 4, "b"]')
    assert model_list.to_data() == [2, 4, 'b']

    model_list.contents = [True, 'text', -47.9]
    assert model_list.contents == [True, 'text', -47.9]
    assert model_list.to_data() == [True, 'text', -47.9]

    std_description = Model._get_standard_field_description()
    assert Model[int].to_json_schema(pretty=True) == '''
{
    "title": "Model[int]",
    "description": "'''[1:] + std_description + '''",
    "type": "integer"
}'''  # noqa:Q001

    assert Model[str].to_json_schema(pretty=True) == '''
{
    "title": "Model[str]",
    "description": "'''[1:] + std_description + '''",
    "type": "string"
}'''  # noqa:Q001

    assert Model[Dict].to_json_schema(pretty=True) == '''
{
    "title": "Model[Dict]",
    "description": "'''[1:] + std_description + '''",
    "type": "object"
}'''  # noqa:Q001

    assert Model[List].to_json_schema(pretty=True) == '''
{
    "title": "Model[List]",
    "description": "'''[1:] + std_description + '''",
    "type": "array",
    "items": {}
}'''  # noqa:Q001


def test_json_schema_generic_model_one_level():
    ListT = TypeVar('ListT', bound=List)  # noqa

    class MyList(Model[ListT], Generic[ListT]):
        """My very interesting list model!"""

    assert MyList.to_json_schema(pretty=True) == """
{
    "title": "MyList",
    "description": "My very interesting list model!",
    "type": "array",
    "items": {}
}"""[1:]

    assert MyList[List].to_json_schema(pretty=True) == """
{
    "title": "MyList[List]",
    "description": "My very interesting list model!",
    "type": "array",
    "items": {}
}"""[1:]


def test_json_schema_generic_model_two_levels():
    StrT = TypeVar('StrT', bound=str)  # noqa

    class MyListOfStrings(Model[List[StrT]], Generic[StrT]):
        """My very own list of strings!"""

    assert MyListOfStrings.to_json_schema(pretty=True) == """
{
    "title": "MyListOfStrings",
    "description": "My very own list of strings!",
    "type": "array",
    "items": {
        "type": "string"
    }
}"""[1:]

    assert MyListOfStrings[str].to_json_schema(pretty=True) == """
{
    "title": "MyListOfStrings[str]",
    "description": "My very own list of strings!",
    "type": "array",
    "items": {
        "type": "string"
    }
}"""[1:]


@pytest.mark.skip(reason="""
Known issue due to shortcomings of the typing standard library.
Class variables of generic classes are not all available in
in runtime (see: https://github.com/python/typing/issues/629)
In this case, the description of the generic class MyList
is not available from MyListOfStrings to_json_schema method.
Any workarounds should best be implemented in pydantic,
possibly in uniFAIR if this becomes a real issue.
""")
def test_json_schema_generic_models_known_issue():
    ListT = TypeVar('ListT', bound=List)  # noqa

    class MyList(Model[ListT], Generic[ListT]):
        """My very interesting list model!"""

    class MyListOfStrings(Model[MyList[List[str]]]):
        """MyList. What more can you ask for?"""

    assert MyListOfStrings.to_json_schema(pretty=True) == """
{
    "title": "MyListOfStrings",
    "description": "MyList. What more can you ask for?",
    "$ref": "#/definitions/MyList_List_str__",
    "definitions": {
        "MyList_List_str__": {
            "title": "MyList[List[str]]",
            "description": "My very interesting list model!.",
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}"""[1:]


def test_custom_parser():
    class UpperCaseStr(Model[str]):
        @classmethod
        def _parse_data(cls, data: str) -> str:
            return data.upper()

    assert UpperCaseStr('help').to_data() == 'HELP'

    model = UpperCaseStr()
    assert model.to_data() == ''

    model.from_data('I need somebody!')
    assert model.to_data() == 'I NEED SOMEBODY!'


def test_custom_parser_and_validation():
    class OnlyUpperCaseLettersStr(Model[str]):
        @classmethod
        def _parse_data(cls, data: str) -> str:
            assert data == '' or data.isalpha()
            return data.upper()

    assert OnlyUpperCaseLettersStr('help').to_data() == 'HELP'

    model = OnlyUpperCaseLettersStr()
    model.from_data('Notjustanybody')  # noqa
    assert model.to_data() == 'NOTJUSTANYBODY'  # noqa

    with pytest.raises(ValidationError):
        OnlyUpperCaseLettersStr('Help!')

    with pytest.raises(ValidationError):
        model = OnlyUpperCaseLettersStr()
        model.from_data('Not just anybody! Call 911!!')


def test_custom_parser_to_other_type(StringToLength):  # noqa
    assert StringToLength('So we sailed up to the sun').to_data() == 26
    string_to_length = StringToLength()
    string_to_length.from_data('Till we found the sea of green')
    assert string_to_length.to_data() == 30


def test_nested_model():
    class DictToListOfPositiveInts(Model[Dict[PositiveInt, List[PositiveInt]]]):
        """This model is perfect for a mapping product numbers to factor lists"""

    model_1 = DictToListOfPositiveInts()
    assert model_1.to_data() == {}

    product_factors = {
        2: [2], 3: [3], 4: [2, 2], 5: [5], 6: [2, 3], 7: [7], 8: [2, 2, 2], 9: [3, 3]
    }
    model_1.from_data(product_factors)
    assert model_1.to_data() == product_factors

    unloaded_data = model_1.to_data()
    unloaded_data[10] = [-2, -5]

    with pytest.raises(ValidationError):
        model_1.from_data(unloaded_data)

    unloaded_data[10] = [2, 5]
    model_1.from_data(unloaded_data)
    assert model_1.to_data() == unloaded_data

    assert model_1.to_json() == ('{"2": [2], "3": [3], "4": [2, 2], "5": [5], "6": [2, 3], '
                                 '"7": [7], "8": [2, 2, 2], "9": [3, 3], "10": [2, 5]}')

    model_2 = DictToListOfPositiveInts()
    model_2.from_json('{"2": [2], "3": [3], "4": [2, 2], "5": [5], "6": [2, 3], '
                      '"7": [7], "8": [2, 2, 2], "9": [3, 3], "10": [2, 5]}')
    assert sorted(model_2.to_data()) == sorted({
        2: [2], 3: [3], 4: [2, 2], 5: [5], 6: [2, 3], 7: [7], 8: [2, 2, 2], 9: [3, 3], 10: [2, 5]
    })

    assert model_1.to_json_schema(pretty=True) == """
{
    "title": "DictToListOfPositiveInts",
    "description": "This model is perfect for a mapping product numbers to factor lists",
    "type": "object",
    "additionalProperties": {
        "type": "array",
        "items": {
            "type": "integer",
            "exclusiveMinimum": 0
        }
    }
}"""[1:]


def test_complex_nested_models():
    class ProductFactorsTuple(Model[Tuple[PositiveInt, List[PositiveInt]]]):
        """This model maps a single product to its product_factors, including validation"""
        @classmethod
        def _parse_data(
                cls, data: Tuple[PositiveInt,
                                 List[PositiveInt]]) -> Tuple[PositiveInt, List[PositiveInt]]:
            from functools import reduce
            from operator import mul

            product, factors = data
            assert reduce(mul, factors) == product
            return data

    class ListOfProductFactorsTuples(Model[List[ProductFactorsTuple]]):
        """A list of ProductFactorsTuples"""

    model = ListOfProductFactorsTuples()
    assert model.to_data() == []

    product_factors_as_tuples = [(2, [2]), (3, [3]), (4, [2, 2]), (5, [5]), (6, [2, 3]), (7, [7]),
                                 (8, [2, 2, 2]), (9, [3, 3])]

    model.from_data(product_factors_as_tuples)
    assert model.to_data() == product_factors_as_tuples

    unloaded_data = model.to_data()
    unloaded_data.append((10, [3, 5]))

    with pytest.raises(ValidationError):
        model.from_data(unloaded_data)

    unloaded_data[-1] = (10, [2, 5])
    model.from_data(unloaded_data)

    assert model.to_data() == unloaded_data

    roman_numerals = ('I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X')

    class RomanNumeral(Model[str]):
        """A roman numeral"""
        @classmethod
        def _parse_data(cls, data: str) -> str:
            number = int(data)
            assert 0 < number <= 10
            return roman_numerals[number - 1]

    class ListOfProductFactorsTuplesRoman(Model[List[Tuple[RomanNumeral, List[RomanNumeral]]]]):
        """A list of ProductFactorsTuples with RomanNumerals"""

    class ProductFactorDictInRomanNumerals(Model[Dict[str, List[str]]]):
        """Extremely useful model"""

    roman_tuple_model = ListOfProductFactorsTuplesRoman(unloaded_data)
    roman_dict_model_1 = ProductFactorDictInRomanNumerals(roman_tuple_model.to_data())

    assert roman_dict_model_1.to_json() == (
        '{"II": ["II"], "III": ["III"], "IV": ["II", "II"], "V": ["V"], '
        '"VI": ["II", "III"], "VII": ["VII"], "VIII": ["II", "II", "II"], '
        '"IX": ["III", "III"], "X": ["II", "V"]}')

    roman_dict_model_2 = ProductFactorDictInRomanNumerals()
    roman_dict_model_2.from_json('{"II": ["II"], "III": ["III"], "IV": ["II", "II"], "V": ["V"], '
                                 '"VI": ["II", "III"], "VII": ["VII"], "VIII": ["II", "II", "II"], '
                                 '"IX": ["III", "III"], "X": ["II", "V"]}')
    assert roman_dict_model_2.to_data() == {
        'II': ['II'],
        'III': ['III'],
        'IV': ['II', 'II'],
        'V': ['V'],
        'VI': ['II', 'III'],
        'VII': ['VII'],
        'VIII': ['II', 'II', 'II'],
        'IX': ['III', 'III'],
        'X': ['II', 'V']
    }

    assert roman_dict_model_1.to_json_schema(pretty=True) == """
{
    "title": "ProductFactorDictInRomanNumerals",
    "description": "Extremely useful model",
    "type": "object",
    "additionalProperties": {
        "type": "array",
        "items": {
            "type": "string"
        }
    }
}"""[1:]


def test_pandas_dataframe_builtin_direct():
    import pandas as pd

    class PandasDataFrameModel(Model[pd.DataFrame]):
        ...

    dataframe = pd.DataFrame([[1, 2, 3], [4, 5, 6]])

    model_1 = PandasDataFrameModel()
    assert isinstance(model_1.contents, pd.DataFrame) and model_1.contents.empty

    model_1.contents = dataframe

    pd.testing.assert_frame_equal(
        model_1.contents,
        dataframe,
    )

    with pytest.raises(ValidationError):
        PandasDataFrameModel([[1, 2, 3], [4, 5, 6]])

    model_2 = PandasDataFrameModel(dataframe)

    pd.testing.assert_frame_equal(
        model_2.contents,
        dataframe,
    )
