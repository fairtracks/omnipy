"""Tests for general-purpose model helpers."""

from dataclasses import dataclass
from datetime import date
from typing import Literal, TYPE_CHECKING

import pytest

from omnipy.components.general.models import (
    AddAllValuesModel,
    Chain2,
    Chain3,
    Chain4,
    Chain5,
    Chain6,
    ConverterModel,
    EnumeratedDatasetModel,
    EnumeratedListModel,
    EnumeratedListOfTuplesModel,
    MergeListsOfRecordsIntoDatasetByIndexModel,
    MergeListsOfRecordsIntoDatasetByPrimaryKeyModel,
    NotIterableExceptStrOrBytesModel,
    PrimaryKeyDatasetModel,
)
from omnipy.data.dataset import Dataset
from omnipy.data.helpers import FailedData, PendingData
from omnipy.data.model import Model
from omnipy.data.primary_key import PrimaryKey
from omnipy.util.pydantic import ValidationError

from ...helpers.functions import assert_model
from ..helpers.models import Record
from .helpers.models import MyList, MyListModel, RotateOneCharModel, SplitCharsModel


@pytest.mark.parametrize('data', [[1, 2, 3], (1, 2, 3), {'a': 1, 'b': 2, 'c': 3}])
def test_add_all_values(data) -> None:
    model = AddAllValuesModel[int](data)
    assert type(model.content) is int
    assert model.content == 6
    assert model.to_data() == 6
    converted = AddAllValuesModel[int].convert(data)
    assert type(converted) is int
    assert converted == 6


def test_add_all_values_preserves_order_and_inputs() -> None:
    pages = [[1, 2], [], [3]]
    model = AddAllValuesModel[list[int]](pages)
    assert type(model.content) is list
    assert model.content == [1, 2, 3]
    assert model.to_data() == [1, 2, 3]
    assert pages == [[1, 2], [], [3]]
    assert AddAllValuesModel[str]({'b': 'first', 'a': 'second'}).to_data() == 'firstsecond'
    assert AddAllValuesModel[int](iter([1, 2, 3])).to_data() == 6


def test_add_all_values_accepts_already_converted_output() -> None:
    assert AddAllValuesModel[int](6).content == 6
    assert AddAllValuesModel[list[int]]([]).content == []


def test_add_all_values_from_mimicking_dataset() -> None:
    pages = Model[Model[Dataset[Model[list[int]]]]]({'first': [1, 2], 'second': [3]})
    assert AddAllValuesModel[list[int]](pages).to_data() == [1, 2, 3]
    assert pages.to_data() == {'first': [1, 2], 'second': [3]}


@pytest.mark.parametrize('data', [[], {}, iter(())])
def test_add_all_values_rejects_empty_input(data) -> None:
    with pytest.raises(ValueError, match='empty iterable'):
        AddAllValuesModel[int](data)


if TYPE_CHECKING:
    from omnipy.data.typing.model import PlainModel


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
    assert NotIterableExceptStrOrBytesModel('æøå'.encode()).content == 'æøå'.encode()


def test_chain2_model():
    """Compose two model conversions in sequence."""

    MyListModel(MyList(['a', 'b', 'c']))

    class SplitCharsToMyListModel(
        Chain2[
            SplitCharsModel,
            MyListModel,
        ]
    ): ...

    model = SplitCharsToMyListModel('abc')
    assert model.content == MyListModel(MyList('a', 'b', 'c'))
    assert model.to_data() == ['a', 'b', 'c']


def test_concat_chain2_model_with_to_data_conversion():
    """Concatenate Chain2 models while preserving data conversion."""

    if TYPE_CHECKING:
        from omnipy.shared.protocols.content import IsStrContent

        class SplitCharsToMyListModel(
            IsStrContent,
            Chain2[
                SplitCharsModel,
                MyListModel,
            ],
        ): ...
    else:

        class SplitCharsToMyListModel(
            Chain2[
                SplitCharsModel,
                MyListModel,
            ],
        ): ...

    stream = SplitCharsModel('abc') + SplitCharsToMyListModel('def')
    assert stream.to_data() == ['a', 'b', 'c', 'd', 'e', 'f']

    stream2 = SplitCharsToMyListModel('abc') + SplitCharsModel('def')
    assert stream2.to_data() == ['a', 'b', 'c', 'd', 'e', 'f']


def test_chain2_union_models():
    """Document union handling for Chain2 models."""
    with pytest.raises(IndexError):

        class FailingStrToBoolOrFloatModel(Chain2[Model[str], Model[bool] | Model[float]]): ...

        FailingStrToBoolOrFloatModel(3.4)

    # Could of course have used Model[bool | float] directly,
    # but this is to document a workaround for Chain2 with Unions
    class BoolOrFloatModel(Model[Model[bool] | Model[float]]): ...

    class StrToBoolOrFloatModel(Chain2[Model[str], BoolOrFloatModel]): ...

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

    class RotateOneAndSplitCharsToMyListModel(
        Chain3[
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
        ]
    ): ...

    model = RotateOneAndSplitCharsToMyListModel('abcdefg')
    assert model.content == MyListModel(MyList('b', 'c', 'd', 'e', 'f', 'g', 'a'))
    assert model.to_data() == ['b', 'c', 'd', 'e', 'f', 'g', 'a']


def test_chain4_model():
    """Compose four model conversions in sequence."""

    class RotateTwoAndSplitCharsToMyListModel(
        Chain4[
            RotateOneCharModel,
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
        ]
    ): ...

    model = RotateTwoAndSplitCharsToMyListModel('abcdefg')
    assert model.content == MyListModel(MyList('c', 'd', 'e', 'f', 'g', 'a', 'b'))
    assert model.to_data() == ['c', 'd', 'e', 'f', 'g', 'a', 'b']


def test_chain5_model():
    """Compose five model conversions in sequence."""

    class RotateThreeAndSplitCharsToMyListModel(
        Chain5[
            RotateOneCharModel,
            RotateOneCharModel,
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
        ]
    ): ...

    model = RotateThreeAndSplitCharsToMyListModel('abcdefg')
    assert model.content == MyListModel(MyList('d', 'e', 'f', 'g', 'a', 'b', 'c'))
    assert model.to_data() == ['d', 'e', 'f', 'g', 'a', 'b', 'c']


def test_chain6_model():
    """Compose six model conversions in sequence."""

    class RotateThreeAndSplitCharsToMyListModel(
        Chain6[
            RotateOneCharModel,
            RotateOneCharModel,
            RotateOneCharModel,
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
        ]
    ): ...

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

    assert tuple(
        SlashDateToDateModel.convert_all(
            [
                '2026/01/15',
                '2026/12/24',
            ]
        )
    ) == (
        date(2026, 1, 15),
        date(2026, 12, 24),
    )

    converted_items = SlashDateToDateModel.convert_all_items(
        {
            'river': '2026/04/01',
            'lake': '2026/04/02',
        }
    )
    assert dict(converted_items) == {
        'river': date(2026, 4, 1),
        'lake': date(2026, 4, 2),
    }


def test_converter_model_parses_model_to_model():
    """Parse one structured temperature model into another structured temperature model."""

    if TYPE_CHECKING:
        # PlainModel to avoid Model[float] subclasses to be typed as Model_float
        class FahrenheitModel(PlainModel[float]): ...

        class CelsiusModel(PlainModel[float]): ...
    else:

        class FahrenheitModel(Model[float]): ...

        class CelsiusModel(Model[float]): ...

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
        {'yesterday': FahrenheitModel(77.0), 'today': FahrenheitModel(68.0)},
        CelsiusModel,
        float,
        {'yesterday': 25.0, 'today': 20.0},
    )

    already_normalized = FahrenheitToCelsiusModel(CelsiusModel(4.5))
    assert already_normalized.to_data() == 4.5


def test_converter_model_parses_two_models_to_one_model():
    """Parse either Fahrenheit or Celsius models into one Kelvin model."""

    if TYPE_CHECKING:
        # PlainModel to avoid Model[float] subclasses to be typed as Model_float
        class CelsiusModel(PlainModel[float]): ...

        class FahrenheitModel(PlainModel[float]): ...

        class KelvinModel(PlainModel[float]): ...
    else:

        class CelsiusModel(Model[float]): ...

        class FahrenheitModel(Model[float]): ...

        class KelvinModel(Model[float]): ...

    class TemperatureNormalizer(
        ConverterModel[
            CelsiusModel | FahrenheitModel,
            KelvinModel,
        ]
    ):
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
        {'celsius': CelsiusModel(100.0), 'fahrenheit': FahrenheitModel(212.0)},
        KelvinModel,
        float,
        {'celsius': 373.15, 'fahrenheit': 373.15},
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


def test_enumerated_list_of_tuples_model() -> None:
    """Normalize enumerated tuple lists with sequential indexes."""
    data = [(0, 'a'), ('1', 'b'), (2, 0)]
    expected_str = [(0, 'a'), (1, 'b'), (2, '0')]
    expected_object = [(0, 'a'), (1, 'b'), (2, 0)]

    with pytest.raises(ValidationError):
        EnumeratedListOfTuplesModel[int](data)

    enumerated = EnumeratedListOfTuplesModel[str](data)
    assert enumerated.content == expected_str
    assert enumerated.to_data() == expected_str

    enumerated = EnumeratedListOfTuplesModel(data)
    assert enumerated.content == expected_object
    assert enumerated.to_data() == expected_object

    data_empty: list[str] = []
    expected_empty: list[str] = []
    enumerated = EnumeratedListOfTuplesModel(data_empty)
    assert enumerated.content == expected_empty
    assert enumerated.to_data() == expected_empty


def test_enumerated_list_of_tuples_model_failures() -> None:
    """Reject enumerated tuple lists with invalid indexes."""
    data_not_sequential = [(3, 'a'), (5, 'b'), (1, 'c')]
    with pytest.raises(ValidationError):
        EnumeratedListOfTuplesModel(data_not_sequential)

    data_not_from_zero = [(1, 'a'), (2, 'b'), (3, 'c')]
    with pytest.raises(ValidationError):
        EnumeratedListOfTuplesModel(data_not_from_zero)


def test_enumerated_list_model() -> None:
    """Enumerate plain lists into indexed tuple pairs."""
    data = ['a', 'b', 'c']
    expected = [(0, 'a'), (1, 'b'), (2, 'c')]

    with pytest.raises(ValidationError):
        EnumeratedListModel[int](data)

    enumerated = EnumeratedListModel[str](data)
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


def test_enumerated_dataset_preserves_duplicates_and_order() -> None:
    assert EnumeratedDatasetModel[str](['b', 'a', 0]).to_data() == {'0': 'b', '1': 'a', '2': '0'}
    assert EnumeratedDatasetModel(['b', 'a', 0]).to_data() == {'0': 'b', '1': 'a', '2': 0}
    assert EnumeratedDatasetModel[tuple[int, str]]([(7, 'x')]).to_data() == {'0': (7, 'x')}
    assert EnumeratedDatasetModel[int]([]).to_data() == {}


def test_primary_key_cache_is_specific_to_each_model_class() -> None:
    class ByIdentity(PrimaryKeyDatasetModel[PrimaryKey[Literal['identity']], Record]): ...

    identity_key = ByIdentity.primary_key
    assert identity_key == ('identity',)
    assert ByIdentity.primary_key is identity_key

    class InheritedByIdentity(ByIdentity): ...

    class ByProjectAndIdentity(
        PrimaryKeyDatasetModel[PrimaryKey[Literal['project'], Literal['identity']], Record]
    ): ...

    inherited_key = InheritedByIdentity.primary_key
    assert inherited_key == identity_key
    assert inherited_key is not identity_key
    assert InheritedByIdentity.primary_key is inherited_key

    composite_key = ByProjectAndIdentity.primary_key
    assert composite_key == ('project', 'identity')
    assert ByProjectAndIdentity.primary_key is composite_key
    assert ByIdentity.primary_key is identity_key


@pytest.mark.parametrize('as_dataset', [False, True])
def test_primary_key_dataset_composite_keys(as_dataset: bool) -> None:
    records = [Record(identity='a|b', project='p%1'), Record(identity=None, project='p2')]
    data = Dataset[Model[Record]](first=records[0], second=records[1]) if as_dataset else records
    model = PrimaryKeyDatasetModel[PrimaryKey[Literal['project'], Literal['identity']], Record](
        data
    )
    assert model.to_data() == {
        'p%251|a%7Cb': records[0].dict(),
        'p2|None': records[1].dict(),
    }
    assert list(model.to_data()) == ['p%251|a%7Cb', 'p2|None']


@pytest.mark.parametrize('identities', [['same', 'same'], [1, '1'], [None, 'None']])
def test_primary_key_dataset_rejects_serialization_collisions(identities) -> None:
    records = [Record(identity=identity) for identity in identities]
    with pytest.raises(ValueError, match='Duplicate serialized primary key'):
        PrimaryKeyDatasetModel[PrimaryKey[Literal['identity']], Record](records)


def test_primary_key_dataset_accepts_container_keys_and_defaults() -> None:
    records = [Record(identity=[1, 2]), Record(identity={'a': 1})]
    model = PrimaryKeyDatasetModel[PrimaryKey[Literal['identity']], Record](records)
    assert list(model.to_data()) == ['[1, 2]', "{'a': 1}"]
    default_key = PrimaryKeyDatasetModel[PrimaryKey[Literal['project']], Record]([records[0]])
    assert list(default_key.to_data()) == ['north']


def test_primary_key_dataset_rejects_unknown_field_even_when_empty() -> None:
    with pytest.raises(ValueError, match='Unknown primary-key field'):
        PrimaryKeyDatasetModel[PrimaryKey[Literal['missing']], Record]([])


def test_composite_key_serialization_prevents_delimiter_ambiguity() -> None:
    records = [Record(project='a|b', identity='c'), Record(project='a', identity='b|c')]
    model_cls = PrimaryKeyDatasetModel[PrimaryKey[Literal['project'], Literal['identity']], Record]
    model = model_cls(records)
    assert list(model.to_data()) == ['a%7Cb|c', 'a|b%7Cc']
    with pytest.raises(ValueError, match='Duplicate serialized primary key'):
        model.from_data([Record(identity=1), Record(identity='1')])
    assert list(model.to_data()) == ['a%7Cb|c', 'a|b%7Cc']


def test_primary_key_dataset_recomputes_input_keys() -> None:
    source = Dataset[Model[Record]](wrong=Record(identity='right'))
    result = PrimaryKeyDatasetModel[PrimaryKey[Literal['identity']], Record](source)
    assert list(result.to_data()) == ['right']
    assert list(source) == ['wrong']


@pytest.mark.parametrize('as_dataset', [False, True])
def test_merge_lists_of_records(as_dataset: bool) -> None:
    pages = [[Record(identity='b')], [], [Record(identity='a')]]
    data = EnumeratedDatasetModel[list[Record]](pages) if as_dataset else pages
    keyed = MergeListsOfRecordsIntoDatasetByPrimaryKeyModel[
        PrimaryKey[Literal['identity']], Record
    ](data)
    indexed = MergeListsOfRecordsIntoDatasetByIndexModel[Record](data)
    assert list(keyed.to_data()) == ['b', 'a']
    assert list(indexed.to_data()) == ['0', '1']
    assert list(keyed.to_data().values()) == list(indexed.to_data().values())
    assert [record.identity for page in pages for record in page] == ['b', 'a']


@pytest.mark.parametrize('lists', [[], {}])
def test_merge_empty_lists_of_records(lists: list[Record]) -> None:
    assert MergeListsOfRecordsIntoDatasetByIndexModel[Record](lists).to_data() == {}
    assert (
        MergeListsOfRecordsIntoDatasetByPrimaryKeyModel[PrimaryKey[Literal['identity']], Record](
            lists
        ).to_data()
        == {}
    )


# TODO: Recheck with native Pydantic v2, which rejects [] as a dict or
#     record. The v1 compatibility API still coerces each empty page to a
#     default-valued Record. See
#     test_mimic_first_level_operations_on_nested_dict in
#     tests/data/test_model.py.
@pytest.mark.skip(reason='Known Pydantic v1 issue: empty lists parse as default-valued records')
@pytest.mark.parametrize('lists', [[[]], [[], []]])
def test_merge_empty_pages_with_default_records_known_issue(lists: list[Record]) -> None:
    assert MergeListsOfRecordsIntoDatasetByIndexModel[Record](lists).to_data() == {}
    assert (
        MergeListsOfRecordsIntoDatasetByPrimaryKeyModel[PrimaryKey[Literal['identity']], Record](
            lists
        ).to_data()
        == {}
    )


def test_merge_record_pages_rejects_cross_page_collisions() -> None:
    pages = [[Record(identity=1)], [Record(identity='1')]]
    with pytest.raises(ValueError, match='Duplicate serialized primary key'):
        MergeListsOfRecordsIntoDatasetByPrimaryKeyModel[PrimaryKey[Literal['identity']], Record](
            pages
        )
    assert len(MergeListsOfRecordsIntoDatasetByIndexModel[Record](pages).to_data()) == 2


@pytest.mark.parametrize('failed', [False, True])
def test_merge_record_pages_does_not_drop_unavailable_pages(failed: bool) -> None:
    pages = Dataset[Model[list[Record]]](available=[Record(identity='available')])
    details = dict(job_name='request', job_unique_name='request-1')
    if failed:
        pages['missing'] = FailedData(**details, exception=ValueError('bad response'))
        expected_message = 'failed to return data'
        expected_error_type = 'value_error.faileddata'
    else:
        pages['missing'] = PendingData(**details)
        expected_message = 'still awaiting data'
        expected_error_type = 'value_error.pendingdata'
    with pytest.raises(ValidationError, match=expected_message) as error:
        MergeListsOfRecordsIntoDatasetByIndexModel[Record](pages)
    assert error.value.errors()[0]['type'] == expected_error_type
