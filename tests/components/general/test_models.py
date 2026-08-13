"""Tests for general-purpose model helpers."""

from datetime import date
from typing import TYPE_CHECKING

import pytest

from omnipy.components.general.models import (Chain2,
                                              Chain3,
                                              Chain4,
                                              Chain5,
                                              Chain6,
                                              ConverterModel,
                                              NotIterableExceptStrOrBytesModel)
from omnipy.data.model import Model
from omnipy.util.pydantic import ValidationError

from ...helpers.functions import assert_model
from .helpers.models import MyList, MyListModel, RotateOneCharModel, SplitCharsModel

if TYPE_CHECKING:
    from omnipy.data._typing.mimic_models import PlainModel


def test_not_iterable_except_str_model():
    """Accept scalars while rejecting non-string iterables."""
    assert NotIterableExceptStrOrBytesModel().content is None
    assert NotIterableExceptStrOrBytesModel(None).content is None
    assert NotIterableExceptStrOrBytesModel(1234).content == 1234
    assert NotIterableExceptStrOrBytesModel(True).content is True

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel((1, 2, 3, 4))

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel([1, 2, 3, 4])

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel({1: 2, 3: 4})

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel({1, 2, 3, 4})

    assert NotIterableExceptStrOrBytesModel('1234').content == '1234'
    assert NotIterableExceptStrOrBytesModel('æøå'.encode('utf8')).content == 'æøå'.encode('utf8')


def test_chain2_model():
    """Compose two model conversions in sequence."""

    MyListModel(MyList(['a', 'b', 'c']))

    class SplitCharsToMyListModel(Chain2[
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    model = SplitCharsToMyListModel('abc')
    assert model.content == MyListModel(MyList('a', 'b', 'c'))
    assert model.to_data() == ['a', 'b', 'c']


def test_concat_chain2_model_with_to_data_conversion():
    """Concatenate Chain2 models while preserving data conversion."""
    class SplitCharsToMyListModel(Chain2[
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    stream = SplitCharsModel('abc') + SplitCharsToMyListModel('def')
    assert stream.to_data() == ['a', 'b', 'c', 'd', 'e', 'f']

    stream2 = SplitCharsToMyListModel('abc') + SplitCharsModel('def')
    assert stream2.to_data() == ['a', 'b', 'c', 'd', 'e', 'f']


def test_chain2_union_models():
    """Document union handling for Chain2 models."""
    with pytest.raises(IndexError):

        class FailingStrToBoolOrFloatModel(Chain2[Model[str], Model[bool] | Model[float]]):
            ...

        FailingStrToBoolOrFloatModel(3.4)

    # Could of course have used Model[bool | float] directly,
    # but this is to document a workaround for Chain2 with Unions
    class BoolOrFloatModel(Model[Model[bool] | Model[float]]):
        ...

    class StrToBoolOrFloatModel(Chain2[Model[str], BoolOrFloatModel]):
        ...

    float_data_model = StrToBoolOrFloatModel('3.4')
    assert float_data_model.to_data() == 3.4

    bool_data_model = StrToBoolOrFloatModel('1')
    assert bool_data_model.to_data() is True

    with pytest.raises(ValidationError):
        StrToBoolOrFloatModel('not_a_bool_nor_float')


# TODO: When Model conversion types have been implemented, improve Chain models to parse on main
#       type instead of last in chain, which causes confusion, like in
#       test_chain2_seems_like_wrong_order.
#
# def test_chain2_seems_like_wrong_order():
#     class IntThenStrModel(Chain2[Model[int], Model[str]]):
#         ...
#
#     assert IntThenStrModel(3.4).content == '3'


def test_chain3_model():
    """Compose three model conversions in sequence."""
    class RotateOneAndSplitCharsToMyListModel(Chain3[
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    model = RotateOneAndSplitCharsToMyListModel('abcdefg')
    assert model.content == MyListModel(MyList('b', 'c', 'd', 'e', 'f', 'g', 'a'))
    assert model.to_data() == ['b', 'c', 'd', 'e', 'f', 'g', 'a']


def test_chain4_model():
    """Compose four model conversions in sequence."""
    class RotateTwoAndSplitCharsToMyListModel(Chain4[
            RotateOneCharModel,
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    model = RotateTwoAndSplitCharsToMyListModel('abcdefg')
    assert model.content == MyListModel(MyList('c', 'd', 'e', 'f', 'g', 'a', 'b'))
    assert model.to_data() == ['c', 'd', 'e', 'f', 'g', 'a', 'b']


def test_chain5_model():
    """Compose five model conversions in sequence."""
    class RotateThreeAndSplitCharsToMyListModel(Chain5[
            RotateOneCharModel,
            RotateOneCharModel,
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    model = RotateThreeAndSplitCharsToMyListModel('abcdefg')
    assert model.content == MyListModel(MyList('d', 'e', 'f', 'g', 'a', 'b', 'c'))
    assert model.to_data() == ['d', 'e', 'f', 'g', 'a', 'b', 'c']


def test_chain6_model():
    """Compose six model conversions in sequence."""
    class RotateThreeAndSplitCharsToMyListModel(Chain6[
            RotateOneCharModel,
            RotateOneCharModel,
            RotateOneCharModel,
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    model = RotateThreeAndSplitCharsToMyListModel('abcdefg')
    assert model.content == MyListModel(MyList('e', 'f', 'g', 'a', 'b', 'c', 'd'))
    assert model.to_data() == ['e', 'f', 'g', 'a', 'b', 'c', 'd']


def _assert_convert(
    model_cls: type[ConverterModel],
    input_data: object,
    exp_output_model: type[Model],
    exp_model_type: type,
    expected_data: object,
) -> None:
    model = model_cls.convert(input_data)
    assert model.__class__ is exp_output_model
    assert_model(model, exp_model_type, expected_data)


def _assert_convert_all(
    model_cls: type[ConverterModel],
    input_data_items: list[object],
    exp_output_model: type[Model],
    exp_model_type: type,
    expected_data_items: list[object],
) -> None:
    for i, converter_model in enumerate(model_cls.convert_all(input_data_items)):
        assert converter_model.__class__ is exp_output_model
        assert_model(converter_model, exp_model_type, expected_data_items[i])


def _assert_convert_all_items(
    model_cls: type[ConverterModel],
    input_data_dict: dict[str, object],
    exp_output_model: type[Model],
    exp_model_type: type,
    expected_data_dict: dict[str, object],
) -> None:
    for key, converter_model in model_cls.convert_all_items(input_data_dict):
        assert converter_model.__class__ is exp_output_model
        assert_model(converter_model, exp_model_type, expected_data_dict[key])


def test_converter_model_parses_plain_types():
    """Parse plain values into a fundamentally different plain target type."""
    class SlashDateToDateModel(ConverterModel[str, date]):
        @classmethod
        def _convert(cls, data: str) -> date:
            year, month, day = (int(part) for part in data.split('/'))
            return date(year, month, day)

    assert_model(SlashDateToDateModel('2026/08/03'), str | date, date(2026, 8, 3))
    assert_model(SlashDateToDateModel(date(2026, 8, 3)), str | date, date(2026, 8, 3))
    assert_model(SlashDateToDateModel(Model[date](date(2026, 8, 3))), str | date, date(2026, 8, 3))

    # Test that content setting override still works
    model = SlashDateToDateModel('2026/08/03')
    model.content = date(2026, 8, 4)
    assert_model(model, str | date, date(2026, 8, 4))

    assert SlashDateToDateModel.convert('2026/08/03') == date(2026, 8, 3)

    assert tuple(SlashDateToDateModel.convert_all([
        '2026/01/15',
        '2026/12/24',
    ])) == (
        date(2026, 1, 15),
        date(2026, 12, 24),
    )

    converted_items = SlashDateToDateModel.convert_all_items({
        'river': '2026/04/01',
        'lake': '2026/04/02',
    })
    assert dict(converted_items) == {
        'river': date(2026, 4, 1),
        'lake': date(2026, 4, 2),
    }


def test_converter_model_parses_model_to_model():
    """Parse one structured temperature model into another structured temperature model."""

    # PlainModel to avoid Model[float] subclasses to be typed as Model_float
    class FahrenheitModel(PlainModel[float]):
        ...

    class CelsiusModel(PlainModel[float]):
        ...

    class FahrenheitToCelsiusModel(ConverterModel[FahrenheitModel, CelsiusModel]):
        @classmethod
        def _convert(cls, data: FahrenheitModel) -> CelsiusModel:
            return CelsiusModel((data.content - 32) * 5 / 9)

    assert_model(
        FahrenheitToCelsiusModel(FahrenheitModel(68.0)),
        FahrenheitModel | CelsiusModel,
        CelsiusModel(20.0),
    )
    assert_model(FahrenheitToCelsiusModel(68.0), FahrenheitModel | CelsiusModel, CelsiusModel(20.0))

    _assert_convert(FahrenheitToCelsiusModel, FahrenheitModel(68.0), CelsiusModel, float, 20.0)

    _assert_convert_all(
        FahrenheitToCelsiusModel,
        [68.0, FahrenheitModel(68.0)],
        CelsiusModel,
        float,
        [20.0, 20.0],
    )

    _assert_convert_all_items(
        FahrenheitToCelsiusModel,
        {
            'yesterday': FahrenheitModel(77.0), 'today': FahrenheitModel(68.0)
        },
        CelsiusModel,
        float,
        {
            'yesterday': 25.0, 'today': 20.0
        },
    )

    already_normalized = FahrenheitToCelsiusModel(CelsiusModel(4.5))
    assert already_normalized.to_data() == 4.5


def test_converter_model_parses_two_models_to_one_model():
    """Parse either Fahrenheit or Celsius models into one Kelvin model."""

    # PlainModel to avoid Model[float] subclasses to be typed as Model_float
    class CelsiusModel(PlainModel[float]):
        ...

    class FahrenheitModel(PlainModel[float]):
        ...

    class KelvinModel(PlainModel[float]):
        ...

    class TemperatureNormalizer(ConverterModel[
            CelsiusModel | FahrenheitModel,
            KelvinModel,
    ]):
        @classmethod
        def _convert(
            cls,
            data: CelsiusModel | FahrenheitModel,
        ) -> KelvinModel:
            match data:
                case CelsiusModel():
                    return KelvinModel(data.content + 273.15)
                case FahrenheitModel():
                    return KelvinModel((data.content - 32) * 5 / 9 + 273.15)

    assert_model(
        TemperatureNormalizer(FahrenheitModel(68.0)),
        CelsiusModel | FahrenheitModel | KelvinModel,
        KelvinModel(293.15),
    )

    _assert_convert(TemperatureNormalizer, FahrenheitModel(68.0), KelvinModel, float, 293.15)
    _assert_convert(TemperatureNormalizer, CelsiusModel(18.5), KelvinModel, float, 291.65)

    _assert_convert_all(
        TemperatureNormalizer,
        [FahrenheitModel(68.0), CelsiusModel(18.5)],
        KelvinModel,
        float,
        [293.15, 291.65],
    )

    _assert_convert_all_items(
        TemperatureNormalizer,
        {
            'celsius': CelsiusModel(100.0), 'fahrenheit': FahrenheitModel(212.0)
        },
        KelvinModel,
        float,
        {
            'celsius': 373.15, 'fahrenheit': 373.15
        },
    )

    already_normalized = TemperatureNormalizer(KelvinModel(0))
    assert already_normalized.to_data() == 0


def test_converter_model_rejects_parameterized_generics_for_from_type():
    """Reject generic aliases like list[int] as ConverterModel source type."""
    with pytest.raises(TypeError, match='Parameterized generics not allowed for FromT'):

        class _FailingConverterModel(ConverterModel[list[int], str]):
            @classmethod
            def _convert(cls, data: list[int]) -> str:
                return ','.join(str(num) for num in data)


def test_converter_model_rejects_same_from_and_to_type():
    """Reject converter specializations where source and target types are identical."""
    with pytest.raises(TypeError, match='FromT and ToT cannot be the same type'):

        class _FailingConverterModel(ConverterModel[int, int]):
            @classmethod
            def _convert(cls, data: int) -> int:
                return data


def test_converter_model_rejects_union_from_type_with_target_overlap():
    """Reject source unions that already contain the target type."""
    with pytest.raises(TypeError, match='FromT and ToT cannot be the same type'):

        class _FailingConverterModel(ConverterModel[int | str, str]):
            @classmethod
            def _convert(cls, data: int | str) -> str:
                return str(data)
