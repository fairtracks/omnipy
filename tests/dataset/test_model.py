from typing import Dict, Generic, List, Tuple, TypeVar

from pydantic import PositiveInt, StrictInt, ValidationError
import pytest

from unifair.dataset.model import Model


@pytest.mark.skip(reason="""
This test needs to be run as the first test in the test suite in order
not to fail. This is cumbersome. More importantly, it implies that the
functionality is not working correctly. However, it is not meant to work.
Thus, this test is here for documentation purposes only. """)
def test_no_model():
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

    number_model = StrModel()
    assert (isinstance(number_model, StrModel))
    assert (isinstance(number_model, Model))
    assert (number_model.__class__.__name__ == StrModel.__name__)

    assert Model[int]().to_data() == 0
    assert Model[str]().to_data() == ''
    assert Model[Dict]().to_data() == {}
    assert Model[List]().to_data() == []

    assert Model[int](12).to_data() == 12
    assert Model[str]('test').to_data() == 'test'
    assert Model[Dict]({'a': 2}).to_data() == {'a': 2}
    assert Model[List]([2, 4, 'b']).to_data() == [2, 4, 'b']


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


def test_invalid_models():
    with pytest.raises(TypeError):

        class NoTypesModel(Model):
            ...

        class DoubleTypesModel(Model[int, str]):  # noqa
            ...


def test_export_methods():
    assert Model[int](12).to_data() == 12
    assert Model[str]('test').to_data() == 'test'
    assert Model[Dict]({'a': 2}).to_data() == {'a': 2}
    assert Model[List]([2, 4, 'b']).to_data() == [2, 4, 'b']

    assert Model[int](12).to_json() == '12'
    assert Model[str]('test').to_json() == '"test"'
    assert Model[Dict]({'a': 2}).to_json() == '{"a": 2}'
    assert Model[List]([2, 4, 'b']).to_json() == '[2, 4, "b"]'

    std_description = Model._get_standard_field_description()
    assert Model[int].to_json_schema(pretty=True) == '''
{
    "title": "Model[int]",
    "description": "'''[1:] + std_description + '''",
    "default": 0,
    "type": "integer"
}'''  # noqa:Q001

    assert Model[str].to_json_schema(pretty=True) == '''
{
    "title": "Model[str]",
    "description": "'''[1:] + std_description + '''",
    "default": "",
    "type": "string"
}'''  # noqa:Q001

    assert Model[Dict].to_json_schema(pretty=True) == '''
{
    "title": "Model[Dict]",
    "description": "'''[1:] + std_description + '''",
    "default": {},
    "type": "object"
}'''  # noqa:Q001

    assert Model[List].to_json_schema(pretty=True) == '''
{
    "title": "Model[List]",
    "description": "'''[1:] + std_description + '''",
    "default": [],
    "type": "array",
    "items": {}
}'''  # noqa:Q001


def test_json_schema_generic_models():
    ListT = TypeVar('ListT', bound=List)

    class MyList(Model[ListT], Generic[ListT]):
        """My very interesting list model!"""

    assert MyList.to_json_schema(pretty=True) == """
{
    "title": "MyList",
    "description": "My very interesting list model!",
    "default": [],
    "type": "array",
    "items": {}
}"""[1:]

    assert MyList[List].to_json_schema(pretty=True) == """
{
    "title": "MyList[List]",
    "description": "My very interesting list model!",
    "default": [],
    "type": "array",
    "items": {}
}"""[1:]


@pytest.mark.skip(reason="""
Known issue due to shortcomings of the typing standard library.
Class variables of generic classes are not all available in
in runtime (see: https://github.com/python/typing/issues/629)
Any workarounds should best be implemented in pydantic,
possibly in uniFAIR if this becomes a real issue.
""")
def test_json_schema_generic_models_known_issue_1():
    listT = TypeVar('listT', bound=List)

    class MyList(Model[listT], Generic[listT]):
        """My very interesting list model!"""

    class MyListOfStrings(Model[MyList[List[str]]]):
        """MyList. What more can you ask for?"""

    assert MyListOfStrings.to_json_schema(pretty=True) == """
{
    "title": "MyListOfStrings",
    "description": "MyList. What more can you ask for?",
    "default": {
        "__root__": []
    },
    "allOf": [
        {
            "$ref": "#/definitions/MyList_List_str__"
        }
    ],
    "definitions": {
        "MyList_List_str__": {
            "title": "MyList[List[str]]",
            "description": "My very interesting list model!.",
            "default": [],
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    }
}"""[1:]


@pytest.mark.skip(reason="""
StrT seems to be replaced with the RootT TypeVar from Model, 
removing one level of the nested type tree in the process.
Possibly just a matter of figuring out the correct syntax
from the pydantic manual.
""")
def test_json_schema_generic_models_known_issue_2():
    StrT = TypeVar('StrT', bound=str)

    class MyListOfStrings(Model[List[StrT]], Generic[StrT]):
        """My very own list of strings!"""

    assert MyListOfStrings.to_json_schema(pretty=True) == """
{
    "title": "MyListOfStrings",
    "description": "My very own list of strings!",
    "default": [],
    "type": "array",
    "items": {
        "type": "string"
    }
}"""[1:]

    assert MyListOfStrings[str].to_json_schema(pretty=True) == """
{
    "title": "MyList",
    "description": "My very own list of strings!",
    "default": [],
    "type": "array",
    "items": {
        "type": "string",
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


def test_nested_model():
    class DictToListOfPositiveInts(Model[Dict[PositiveInt, List[PositiveInt]]]):
        """This model is perfect for a mapping product numbers to factor lists"""

    model = DictToListOfPositiveInts()
    assert model.to_data() == {}

    product_factors = {
        2: [2], 3: [3], 4: [2, 2], 5: [5], 6: [2, 3], 7: [7], 8: [2, 2, 2], 9: [3, 3]
    }
    model.from_data(product_factors)
    assert model.to_data() == product_factors

    unloaded_data = model.to_data()
    unloaded_data[10] = [-2, -5]

    with pytest.raises(ValidationError):
        model.from_data(unloaded_data)

    unloaded_data[10] = [2, 5]
    model.from_data(unloaded_data)
    assert model.to_data() == unloaded_data

    assert model.to_json() == ('{"2": [2], "3": [3], "4": [2, 2], "5": [5], "6": [2, 3], '
                               '"7": [7], "8": [2, 2, 2], "9": [3, 3], "10": [2, 5]}')

    assert model.to_json_schema(pretty=True) == """
{
    "title": "DictToListOfPositiveInts",
    "description": "This model is perfect for a mapping product numbers to factor lists",
    "default": {},
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
    roman_dict_model = ProductFactorDictInRomanNumerals(roman_tuple_model.to_data())

    assert roman_dict_model.to_json() == (
        '{"II": ["II"], "III": ["III"], "IV": ["II", "II"], "V": ["V"], '
        '"VI": ["II", "III"], "VII": ["VII"], "VIII": ["II", "II", "II"], '
        '"IX": ["III", "III"], "X": ["II", "V"]}')

    assert roman_dict_model.to_json_schema(pretty=True) == """
{
    "title": "ProductFactorDictInRomanNumerals",
    "description": "Extremely useful model",
    "default": {},
    "type": "object",
    "additionalProperties": {
        "type": "array",
        "items": {
            "type": "string"
        }
    }
}"""[1:]
