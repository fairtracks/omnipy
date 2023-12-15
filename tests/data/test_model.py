from math import floor
import os
from textwrap import dedent
from types import MappingProxyType, NoneType
from typing import Annotated, Any, Generic, List, Optional, Type, TypeAlias, TypeVar, Union

from pydantic import BaseModel, PositiveInt, StrictInt, ValidationError
import pytest

from omnipy.data.model import Model
from omnipy.modules.general.typedefs import FrozenDict


def test_no_model_known_issue():
    # Correctly instantiating a model in the beginning of the test implicitly tests whether
    # creating a model sets the field-related class members of Model, such that a later object
    # instantiation without a specified model reuses the previous fields. This which would have
    # happened if `_depopulate_root_field()` were not called in `Model.__class_getitem__()`.
    Model[int]()

    with pytest.raises(TypeError):
        Model()

    with pytest.raises(TypeError):

        class ModelSubclass(Model):
            ...

        ModelSubclass()


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
    assert Model[dict]().to_data() == {}
    assert Model[list]().to_data() == []

    assert Model[int](12).to_data() == 12
    assert Model[str]('test').to_data() == 'test'
    assert Model[list]([2, 4, 'b', {}]).to_data() == [2, 4, 'b', {}]
    assert Model[dict]({'a': 2, 'b': True}).to_data() == {'a': 2, 'b': True}
    assert Model[dict](a=2, b=True).to_data() == {'a': 2, 'b': True}
    assert Model[dict]((('a', 2), ('b', True))).to_data() == {'a': 2, 'b': True}


def test_init_model_as_input():
    assert Model[int](Model[float](4.5)).to_data() == 4
    assert Model[tuple[int, ...]](Model[list[float]]([4.5, 2.3])).to_data() == (4, 2)


def test_error_init():
    with pytest.raises(TypeError):
        assert Model[tuple[int, ...]](12, 2, 4).to_data() == 12
    assert Model[tuple[int, ...]]((12, 2, 4)).to_data() == (12, 2, 4)

    with pytest.raises(AssertionError):
        Model[int](123, __root__=234)

    with pytest.raises(AssertionError):
        Model[int](123, other=234)

    with pytest.raises(AssertionError):
        Model[int](__root__=123, other=234)


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
        Model[int](5).foo = True  # noqa


def test_get_inner_outer_type():
    model = Model[int]()
    assert model.outer_type() == int
    assert model.inner_type() == int
    assert model.is_nested_type() is False

    model = Model[list[int]]()
    assert model.outer_type() == list
    assert model.outer_type(with_args=True) == list[int]
    assert model.inner_type() == int
    assert model.inner_type(with_args=True) == int
    assert model.is_nested_type() is True

    model = Model[list[list[int]]]()
    assert model.outer_type() == list
    assert model.outer_type(with_args=True) == list[list[int]]
    assert model.inner_type() == list
    assert model.inner_type(with_args=True) == list[int]
    assert model.is_nested_type() is True

    model = Model[dict[str, list[int]]]()
    assert model.outer_type() == dict
    assert model.outer_type(with_args=True) == dict[str, list[int]]
    assert model.inner_type() == list
    assert model.inner_type(with_args=True) == list[int]
    assert model.is_nested_type() is True

    model = Model[Annotated[Optional[dict[str, list[int]]], 'Something']]()
    assert model.outer_type() == dict
    assert model.outer_type(with_args=True) == dict[str, list[int]]
    assert model.inner_type() == list
    assert model.inner_type(with_args=True) == list[int]
    assert model.is_nested_type() is True


def test_equality_other_models():
    assert Model[int]() == Model[int]()

    model = Model[int]()
    model.from_data(123)
    assert model == Model[int](123)
    assert model != Model[int](234)

    # Equality is dependent on the datatype/model, in contrast to pydantic.
    # Relevant issue: https://github.com/pydantic/pydantic/pull/3066
    assert Model[int](1) != Model[PositiveInt](1)

    assert Model[list[int]]([1, 2, 3]) == Model[list[int]]([1.0, 2.0, 3.0])
    assert Model[list[int]]([1, 2, 3]) != Model[list[float]]([1.0, 2.0, 3.0])
    assert Model[list[int]]([1, 2, 3]) != Model[list[int]]([1, 2])
    assert Model[list[int]]([1, 2, 3]) != Model[list[int | float]]([1, 2, 3])
    assert Model[list[int]]([1, 2, 3]) != Model[List[int]]([1, 2, 3])


def test_complex_equality():
    model_1 = Model[list[int]]()
    model_1.contents = [1, 2, 3]
    model_2 = Model[list[int]]()
    model_2.contents = (1, 2, 3)

    assert model_1 != model_2
    model_2.validate_contents()
    assert model_1 == model_2


# TODO: Revisit with pydantic v2. Expected to change
def test_equality_with_pydantic_not_symmetric():
    class RootPydanticInt(BaseModel):
        __root__: int

    class MyInt(Model[int]):
        ...

    assert RootPydanticInt(__root__=1) != 1
    assert RootPydanticInt(__root__=1) == {'__root__': 1}
    assert MyInt(1) != 1
    assert MyInt(1) != {'__root__': 1}

    assert RootPydanticInt(__root__=1) == MyInt(1)
    assert MyInt(1) != RootPydanticInt(__root__=1)


def test_equality_with_pydantic_as_args():
    class PydanticModel(BaseModel):
        a: int = 0

    class OtherPydanticModel(BaseModel):
        a: float = 0

    assert PydanticModel(a=1) == OtherPydanticModel(a=1)

    class MyModel(Model[PydanticModel]):
        ...

    class MyOtherModel(Model[OtherPydanticModel]):
        ...

    assert MyModel(a=1) == MyModel(a=1)
    assert MyModel(a=1) == MyModel({'a': 1})
    assert MyModel(a=1) != MyModel(a=2)
    assert MyModel(a=1) != MyOtherModel(a=1)

    class EqualPydanticModel(PydanticModel):
        ...

    class MyEqualModel(Model[EqualPydanticModel]):
        ...

    assert MyModel(a=1) != MyEqualModel(a=1)

    class MyInherited(MyModel):
        ...

    assert MyModel(a=1) != MyInherited(a=1)


def _issubclass_and_isinstance(model_cls_a: Type[Model], model_cls_b: Type[Model]) -> bool:
    is_subclass = issubclass(model_cls_a, model_cls_b)

    model_a = model_cls_a()
    is_instance = isinstance(model_a, model_cls_b)

    return is_subclass and is_instance


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason='To be implemented later. Should be issubtype instead')
def test_issubclass_and_isinstance():
    assert _issubclass_and_isinstance(Model[str], Model[str])
    assert not _issubclass_and_isinstance(Model[int], Model[str])

    assert _issubclass_and_isinstance(Model[int], Model[int | str])
    assert _issubclass_and_isinstance(Model[str], Model[int | str])

    assert _issubclass_and_isinstance(Model[list[str]], Model[list])

    class MyStrList(Model[list[str]]):
        ...

    assert _issubclass_and_isinstance(MyStrList, Model[list])


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


def test_load_inconvertible_data():
    class NumberModel(Model[int]):
        ...

    model = NumberModel()

    with pytest.raises(ValidationError):
        model.from_data('fifteen')
    assert model.contents == 0

    with pytest.raises(ValidationError):
        NumberModel([])
    assert model.contents == 0


def test_load_inconvertible_data_strict_type():
    class StrictNumberModel(Model[StrictInt]):
        ...

    model = StrictNumberModel()

    with pytest.raises(ValidationError):
        model.from_data(123.4)
    assert model.contents == 0

    with pytest.raises(ValidationError):
        model.from_data('234')
    assert model.contents == 0

    with pytest.raises(ValidationError):
        StrictNumberModel(234.9)
    assert model.contents == 0

    model.from_data(123)
    assert model.contents == 123


def test_load_inconvertible_data_nested_type():
    class ListOfIntsModel(Model[list[int]]):
        ...

    model = ListOfIntsModel()

    with pytest.raises(ValidationError):
        model.from_data(123.4)
    assert model.contents == []

    model.from_data([])
    assert model.contents == []

    with pytest.raises(ValidationError):
        model.from_data(['abc'])
    assert model.contents == []

    with pytest.raises(ValidationError):
        ListOfIntsModel([[]])
    assert model.contents == []

    model.from_data([123, 234])
    assert model.contents == [123, 234]


def test_error_invalid_model():

    with pytest.raises(TypeError):

        class DoubleTypesModel(Model[int, str]):  # noqa
            ...


def test_tuple_of_anything():
    class TupleModel(Model[tuple]):
        ...

    assert TupleModel().to_data() == ()
    assert TupleModel((1, 's', True)).to_data() == (1, 's', True)
    with pytest.raises(ValidationError):
        TupleModel(1)


def test_tuple_of_single_type():
    class TupleModel(Model[tuple[int]]):
        ...

    assert TupleModel().to_data() == (0,)
    with pytest.raises(ValidationError):
        TupleModel(1)

    with pytest.raises(ValidationError):
        TupleModel((1, 2, 3))

    with pytest.raises(ValidationError):
        TupleModel((1, 's', True))


def test_tuple_of_single_type_repeated():
    class TupleModel(Model[tuple[int, ...]]):
        ...

    assert TupleModel().to_data() == ()
    assert TupleModel((1, 2, 3)).to_data() == (1, 2, 3)
    with pytest.raises(ValidationError):
        TupleModel(1)

    with pytest.raises(ValidationError):
        TupleModel((1, 's', True))


def test_fixed_tuple_of_different_types():
    class TupleModel(Model[tuple[int, str]]):
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
    # The requirements for omnipy is Python 3.10, and there have been some hashin issues with mostly
    # the older form of this notation, so the newer should be preferred. The old form are kept
    # several places in this file tests related to the notation.

    class UnionModel(Model[int | str | list]):
        ...

    assert UnionModel(15).to_data() == 15
    assert UnionModel('abc').to_data() == 'abc'
    assert UnionModel([]).to_data() == []


# TODO: Revisit test_nested_annotated_union_default_not_defined_by_first_type_known_issue with
#       new Python versions
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Known issue due to a caching problem in the `typing` package in python, which causes a bug in
pydantic (https://github.com/pydantic/pydantic/issues/4519). The first initiation of a nested
type from the typing package is cached by the typing package and defines the order of the second
initiation (even though the order of int and str is the opposite). Works when split into
individual tests. New Union nomenclature introduced in Python 3.10 does not help when nested
under Annotated. Issue is not present in e.g. List or Dict as the default values of these are
[] and {}, respectively.
""")
def test_nested_annotated_union_default_not_defined_by_first_type_known_issue():
    class IntFirstAnnotatedUnionModel(Model[Annotated[Union[int, str], 'test']]):
        ...

    assert IntFirstAnnotatedUnionModel().to_data() == 0

    class StrFirstAnnotatedUnionModel(Model[Annotated[Union[str, int], 'test']]):
        ...

    assert StrFirstAnnotatedUnionModel().to_data() == ''

    class IntFirstAnnotatedUnionModelNew(Model[Annotated[int | str, 'test']]):
        ...

    assert IntFirstAnnotatedUnionModelNew().to_data() == 0

    class StrFirstAnnotatedUnionModelNew(Model[Annotated[str | int, 'test']]):
        ...

    assert StrFirstAnnotatedUnionModelNew().to_data() == ''


# TODO: Revisit
#       test_optional_v1_hack_nested_annotated_union_default_not_defined_by_first_type_known_issue
#       with pydantic v2 and/or new versions of Python
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Same issue as in test_nested_union_default_not_defined_by_first_type_known_issue, however made
more common by "pydantic v1"-related hack in Model (in omnipy), where adding Annotater[Optional]
to all models have added two levels to the type nesting.
""")
def test_optional_v1_hack_nested_annotated_union_default_not_defined_by_first_type_known_issue():
    class IntFirstUnionModel(Model[Union[int, str]]):
        ...

    assert IntFirstUnionModel().to_data() == 0

    class StrFirstUnionModel(Model[Union[str, int]]):
        ...

    assert StrFirstUnionModel().to_data() == ''

    class IntFirstUnionModel(Model[int | str]):
        ...

    assert IntFirstUnionModel().to_data() == 0

    class StrFirstUnionModel(Model[str | int]):
        ...

    assert StrFirstUnionModel().to_data() == ''


def test_union_default_value_from_first_callable_type():
    class FirstTypeNotInstantiatableUnionModel(Model[Any | str]):
        ...

    assert FirstTypeNotInstantiatableUnionModel().to_data() == ''

    with pytest.raises(TypeError):

        class NoTypeInstantiatableUnionModel(Model[Any | Type]):
            ...


def test_union_default_value_if_any_none():
    class NoneFirstUnionModel(Model[None | str]):
        ...

    assert NoneFirstUnionModel().to_data() is None

    class NoneSecondUnionModel(Model[str | None]):
        ...

    assert NoneSecondUnionModel().to_data() is None


# TODO: Revisit test_optional_v1_hack_parsing_independent_on_union_type_order_known_issue with
#       pydantic v2 and/or new versions of Python
@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Same as test_optional_v1_hack_nested_annotated_union_default_not_defined_by_first_type_known_issue,
however in this case also cause issue for parsing. Smart union makes this rare. One example where
this pops up is parsing strings to int or float. There is no reason to always choose one over the
other, so the order decides. The "pydantic v1"-related hack in Model (in omnipy), adding
Annotater[Optional] to all models, triggers type caching in the typing package.
""")
def test_optional_v1_hack_parsing_independent_on_union_type_order_known_issue():
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

    class NestedUnionWithSingleTypeTuple(Model[Union[Union[tuple[str], int], float]]):
        ...

    assert NestedUnionWithSingleTypeTuple().to_data() == ('',)


def test_none_allowed():
    class NoneModel(Model[NoneType]):
        ...

    assert NoneModel().to_data() is None
    assert NoneModel(None).to_data() is None

    with pytest.raises(ValidationError):
        NoneModel(13)

    with pytest.raises(ValidationError):
        NoneModel('None')

    class MaybeNumberModelOptional(Model[Optional[int]]):
        ...

    class MaybeNumberModelUnion(Model[Union[int, None]]):
        ...

    class MaybeNumberModelUnionNew(Model[int | None]):
        ...

    for model_cls in [MaybeNumberModelOptional, MaybeNumberModelUnion, MaybeNumberModelUnionNew]:
        assert model_cls().to_data() is None
        assert model_cls(None).to_data() is None
        assert model_cls(13).to_data() == 13

        with pytest.raises(ValidationError):
            model_cls('None')


def test_none_not_allowed():
    class IntListModel(Model[list[int]]):
        ...

    class IntDictModel(Model[dict[int, int]]):
        ...

    for model_cls in [IntListModel, IntDictModel]:
        assert model_cls().to_data() is not None

        with pytest.raises(ValidationError):
            model_cls(None)


def test_list_of_none():
    class NoneModel(Model[NoneType]):
        ...

    class ListOfNoneModel(Model[list[NoneModel]]):
        ...

    assert ListOfNoneModel().contents == []
    assert ListOfNoneModel([]).contents == []

    with pytest.raises(ValidationError):
        ListOfNoneModel(None)

    assert ListOfNoneModel((None,)).contents == [NoneModel(None)]
    assert ListOfNoneModel([None]).contents == [NoneModel(None)]

    with pytest.raises(ValidationError):
        ListOfNoneModel({1: None})


def test_tuple_of_none():
    class NoneModel(Model[NoneType]):
        ...

    class TupleOfNoneModel(Model[tuple[NoneModel, ...]]):
        ...

    assert TupleOfNoneModel().contents == ()
    assert TupleOfNoneModel(()).contents == ()

    with pytest.raises(ValidationError):
        TupleOfNoneModel(None)

    assert TupleOfNoneModel((None,)).contents == (NoneModel(None),)
    assert TupleOfNoneModel([None]).contents == (NoneModel(None),)

    with pytest.raises(ValidationError):
        TupleOfNoneModel({1: None})


def test_dict_of_none():
    class NoneModel(Model[NoneType]):
        ...

    class DictOfInt2NoneModel(Model[dict[int, NoneModel]]):
        ...

    assert DictOfInt2NoneModel().contents == {}
    assert DictOfInt2NoneModel({}).contents == {}

    with pytest.raises(ValidationError):
        DictOfInt2NoneModel(None)

    with pytest.raises(ValidationError):
        DictOfInt2NoneModel([None])

    assert DictOfInt2NoneModel({1: None}).contents == {1: NoneModel(None)}
    assert DictOfInt2NoneModel(MappingProxyType({1: None})).contents == {1: NoneModel(None)}

    with pytest.raises(ValidationError):
        DictOfInt2NoneModel({'hello': None})


def test_frozendict_of_none():
    class NoneModel(Model[NoneType]):
        ...

    class FrozenDictOfInt2NoneModel(Model[FrozenDict[int, NoneModel]]):
        ...

    assert FrozenDictOfInt2NoneModel().contents == FrozenDict()
    assert FrozenDictOfInt2NoneModel().contents == FrozenDict()

    with pytest.raises(ValidationError):
        FrozenDictOfInt2NoneModel(None)

    with pytest.raises(ValidationError):
        FrozenDictOfInt2NoneModel([None])

    assert FrozenDictOfInt2NoneModel({1: None}).contents == FrozenDict({1: NoneModel(None)})
    assert FrozenDictOfInt2NoneModel(FrozenDict({1: None
                                                 })).contents == FrozenDict({1: NoneModel(None)})

    with pytest.raises(ValidationError):
        FrozenDictOfInt2NoneModel({'hello': None})


# TODO: Look at union + None bug. Perhaps fixed by pydantic v2, but should probably be fixed before
#       that


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason='Known issue, unknown why. Most probably related to pydantic v1 hack')
def test_model_union_none_known_issue():
    with pytest.raises(ValidationError):
        [Model[int | float]](None)


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason='Current pydantic v1 hack requires nested types like list and dict to explicitly'
    'include Optional in their arguments to support parsing of None when the level of '
    'nesting is 2 or more')
def test_doubly_nested_list_and_dict_of_none_model_known_issue():
    class NoneModel(Model[NoneType]):
        ...

    class ListOfListOfNoneModel(Model[list[list[NoneModel]]]):
        ...

    # Workaround
    # class ListOfListOfNoneModel(Model[list[list[Optional[NoneModel]]]]):
    #     ...

    assert ListOfListOfNoneModel() == ListOfListOfNoneModel([])
    assert ListOfListOfNoneModel([]) == ListOfListOfNoneModel([])

    with pytest.raises(ValidationError):
        ListOfListOfNoneModel(None)

    with pytest.raises(ValidationError):
        ListOfListOfNoneModel([None])

    # Workaround fails with this
    assert ListOfListOfNoneModel([[None]]) == ListOfListOfNoneModel([[NoneModel(None)]])

    # Workaround assert
    # assert ListOfListOfNoneModel([[None]]).contents == [[None]]

    with pytest.raises(ValidationError):
        ListOfListOfNoneModel([{1: None}])

    class DictOfDictOfInt2NoneModel(Model[dict[int, dict[int, NoneModel]]]):
        ...

    # Workaround
    # class DictOfDictOfInt2NoneModel(Model[dict[int, dict[int, Optional[NoneModel]]]]):
    #     ...

    DictOfDictOfInt2NoneModel()

    with pytest.raises(ValidationError):
        DictOfDictOfInt2NoneModel(None)

    with pytest.raises(ValidationError):
        DictOfDictOfInt2NoneModel([None])

    with pytest.raises(ValidationError):
        DictOfDictOfInt2NoneModel({1: None})

    # Workaround fails with this
    assert DictOfDictOfInt2NoneModel({1: {2: None}}) == \
        DictOfDictOfInt2NoneModel({1: {2: NoneModel(None)}})

    # Workaround assert
    # assert DictOfDictOfInt2NoneModel({1: {2: None}}).contents == {1: {2: None}}

    with pytest.raises(ValidationError):
        DictOfDictOfInt2NoneModel({1: {'hello': None}})


# Simpler working test added to illustrate more complex fails related to pydantic issue:
# https://github.com/pydantic/pydantic/issues/3836
def test_nested_model_classes_none_as_default() -> None:
    class MaybeNumberModelOptional(Model[Optional[int]]):
        ...

    class MaybeNumberModelUnion(Model[Union[int, None]]):
        ...

    class MaybeNumberModelUnionNew(Model[int | None]):
        ...

    class OuterMaybeNumberModelOptional(Model[MaybeNumberModelOptional]):
        ...

    class OuterMaybeNumberModelUnion(Model[MaybeNumberModelUnion]):
        ...

    class OuterMaybeNumberModelUnionNew(Model[MaybeNumberModelUnionNew]):
        ...

    assert OuterMaybeNumberModelOptional().contents == MaybeNumberModelOptional(None)

    assert OuterMaybeNumberModelUnion().contents == MaybeNumberModelUnion(None)

    assert OuterMaybeNumberModelUnionNew().contents == MaybeNumberModelUnionNew(None)


# Simpler working test added to illustrate more complex fails related to pydantic issue:
# https://github.com/pydantic/pydantic/issues/3836
def test_nested_model_classes_inner_generic_none_as_default() -> None:
    class MaybeNumberModel(Model[Optional[int]]):
        ...

    BaseT = TypeVar('BaseT', bound=MaybeNumberModel)

    class BaseModel(Model[BaseT], Generic[BaseT]):
        ...

    class OuterMaybeNumberModel(BaseModel[MaybeNumberModel]):
        ...

    assert OuterMaybeNumberModel().contents == MaybeNumberModel(None)


def test_nested_model_classes_inner_optional_generic_none_as_default() -> None:
    class MaybeNumberModel(Model[Optional[int]]):
        ...

    BaseT = TypeVar('BaseT', bound=Optional[MaybeNumberModel])

    class BaseModel(Model[BaseT], Generic[BaseT]):
        ...

    class OuterMaybeNumberModel(BaseModel[MaybeNumberModel]):
        ...

    assert OuterMaybeNumberModel().contents == MaybeNumberModel(None)


def test_union_nested_model_classes_inner_optional_generic_none_as_default() -> None:
    class MaybeNumberModel(Model[Optional[int]]):
        ...

    class MaybeStringModel(Model[Optional[str]]):
        ...

    BaseT = TypeVar('BaseT', bound=Union[MaybeNumberModel, MaybeStringModel])

    class BaseModel(Model[BaseT], Generic[BaseT]):
        ...

    class OuterMaybeNumberModel(BaseModel[Union[MaybeNumberModel, MaybeStringModel]]):
        ...

    assert OuterMaybeNumberModel().contents == MaybeNumberModel(None)


def test_union_nested_model_classes_inner_forwardref_generic_list_of_none() -> None:
    BaseT = TypeVar('BaseT', bound=Union['ListModel', 'MaybeNumberModel'])

    class MaybeNumberModel(Model[Optional[int]]):
        ...

    class GenericListModel(Model[list[BaseT]], Generic[BaseT]):
        ...

    class ListModel(GenericListModel['FullModel']):
        ...

    FullModel: TypeAlias = Union[ListModel, MaybeNumberModel]

    ListModel.update_forward_refs(FullModel=FullModel)

    assert ListModel().contents == []
    assert ListModel([None]).contents == [MaybeNumberModel(None)]


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Known issue that popped up in omnipy.modules.json.models. Might be solved by pydantic v2.
Dropping JsonBaseModel (here: BaseModel) is one workaround as it (in contrast to JsonBaseDataset)
does not seem to be needed.
""")
def test_union_nested_model_classes_inner_forwardref_double_generic_none_as_default_known_issue(
) -> None:
    MaybeNumber: TypeAlias = Optional[int]

    BaseT = TypeVar('BaseT', bound=list | 'FullModel' | MaybeNumber)

    class BaseModel(Model[BaseT], Generic[BaseT]):
        ...

    class MaybeNumberModel(BaseModel[MaybeNumber]):
        ...

    # Problem is here. Default value of list[BaseT] is [], while default value of
    # BaseModel[list[BaseT]] is None
    class GenericListModel(BaseModel[list[BaseT]], Generic[BaseT]):
        ...

    class ListModel(GenericListModel['FullModel']):
        ...

    FullModel: TypeAlias = ListModel | MaybeNumberModel

    ListModel.update_forward_refs(FullModel=FullModel)

    assert ListModel().contents == []


def test_import_export_methods():
    assert Model[int](12).to_data() == 12
    assert Model[str]('test').to_data() == 'test'
    assert Model[dict]({'a': 2}).to_data() == {'a': 2}
    assert Model[list]([2, 4, 'b']).to_data() == [2, 4, 'b']

    assert Model[int](12).contents == 12
    assert Model[str]('test').contents == 'test'
    assert Model[dict]({'a': 2}).contents == {'a': 2}
    assert Model[list]([2, 4, 'b']).contents == [2, 4, 'b']

    assert Model[int](12).to_json() == '12'
    assert Model[str]('test').to_json() == '"test"'
    assert Model[dict]({'a': 2}).to_json(pretty=False) == '{"a": 2}'
    assert Model[list]([2, 4, 'b']).to_json(pretty=False) == '[2, 4, "b"]'

    model_int = Model[int]()
    model_int.from_json('12')
    assert model_int.to_data() == 12

    model_int.contents = '13'
    assert model_int.contents == '13'
    model_int.validate_contents()
    assert model_int.contents == 13
    assert model_int.to_data() == 13

    model_int.from_data(14)
    assert model_int.contents == 14
    model_int.from_data('14')
    assert model_int.contents == 14

    model_str = Model[str]()
    model_str.from_json('"test"')
    assert model_str.contents == 'test'
    assert model_str.to_data() == 'test'
    model_str.from_data('test')
    assert model_str.contents == 'test'
    assert model_str.to_data() == 'test'

    model_str.contents = 13
    assert model_str.contents == 13
    model_str.validate_contents()
    assert model_str.contents == '13'
    assert model_str.to_data() == '13'

    model_dict = Model[dict]()
    model_dict.from_json('{"a": 2}')
    assert model_dict.to_data() == {'a': 2}

    model_dict.contents = {'b': 3}
    assert model_dict.contents == {'b': 3}
    assert model_dict.to_data() == {'b': 3}

    model_list = Model[list]()
    model_list.from_json('[2, 4, "b"]')
    assert model_list.to_data() == [2, 4, 'b']

    model_list.contents = [True, 'text', -47.9]
    assert model_list.contents == [True, 'text', -47.9]
    assert model_list.to_data() == [True, 'text', -47.9]

    std_description = Model._get_standard_field_description()
    assert Model[int].to_json_schema() == dedent('''\
    {
      "title": "Model[int]",
      "description": "''' + std_description + '''",
      "type": "integer"
    }''')  # noqa: Q001

    assert Model[str].to_json_schema() == dedent('''\
    {
      "title": "Model[str]",
      "description": "''' + std_description + '''",
      "type": "string"
    }''')  # noqa: Q001

    assert Model[dict].to_json_schema() == dedent('''\
    {
      "title": "Model[dict]",
      "description": "''' + std_description + '''",
      "type": "object"
    }''')  # noqa: Q001

    assert Model[list].to_json_schema() == dedent('''\
    {
      "title": "Model[list]",
      "description": "''' + std_description + '''",
      "type": "array",
      "items": {}
    }''')  # noqa: Q001


def test_model_operations_as_list_simple():
    model = Model[list[int]]()
    assert len(model) == 0

    model.append(123)
    assert len(model) == 1
    assert model[0] == 123
    assert isinstance(model, Model)

    model += [234, 345, 456]
    assert len(model) == 4
    assert model[-1] == 456
    assert isinstance(model, Model)

    assert model[1:-1].contents == [234, 345]
    assert isinstance(model, Model)

    assert tuple(reversed(model)) == (456, 345, 234, 123)

    model[2] = 432
    model[3] = '654'
    assert model[2] == 432
    assert model[3] == 654

    with pytest.raises(ValidationError):
        model[0] = 'bacon'

    assert model[1] == 234

    model[1] /= 2
    assert model[1] == 117
    assert isinstance(model, Model)

    assert model.contents == [123, 117, 432, 654]
    assert model.index(432) == 2

    assert model.pop() == 654
    assert len(model) == 3


def test_model_operations_as_nested_list_no_validation_at_second_level():
    model = Model[list[int | list[int]]]([123, 234, [345]])

    with pytest.raises(ValidationError):
        model[-1] = 'abc'

    with pytest.raises(ValidationError):
        model[-1] = None

    with pytest.raises(ValidationError):
        model[-1] = {2: 3}

    with pytest.raises(ValidationError):
        model[-1] = {}

    with pytest.raises(ValidationError):
        model[-1] = ['abc', 'bce']

    model[-1] = tuple(range(3))
    assert model.contents == [123, 234, [0, 1, 2]]

    # model[-1] is the result of an __getitem__ and is not wrapped as a Model
    assert isinstance(model, Model)
    assert not isinstance(model, list)
    assert not isinstance(model[-1], Model)
    assert isinstance(model[-1], list)

    model[-1].append(tuple(range(3)))
    assert len(model[-1]) == 4
    assert model.contents == [123, 234, [0, 1, 2, (0, 1, 2)]]

    assert model[-1][-1][-1] == 2

    with pytest.raises(TypeError):
        model[-1][-1][-1] = 15
    assert isinstance(model[-1][-1], tuple)
    assert not isinstance(model[-1][1], Model)

    # Here the `model[-1] +=` operation is a series of `__get__`, `__iadd__`, and `__set__`
    # operations, with the `__get__` and `__set__` operating on the "parent" model object.
    # In contrast, the `append()` method only operates on the child level. As only the parent is
    # a Model object, the `+=` operation will trigger a validation, while the `append()` will not.
    with pytest.raises(ValidationError):
        model[-1] += ('a',)
    assert model.contents == [123, 234, [0, 1, 2]]


def test_model_operations_as_nested_list_with_full_validation():
    model = Model[list[Model[list[Model[list[int]] | int]] | int]]([123, 234, [345]])

    model[-1] = tuple(range(3))
    assert model.to_data() == [123, 234, [0, 1, 2]]

    # model[-1] is wrapped as a Model according to nested type args
    assert isinstance(model, Model)
    assert not isinstance(model, list)
    assert isinstance(model[-1], Model)
    assert not isinstance(model[-1], list)

    model[-1].append(tuple(range(3)))
    assert len(model[-1]) == 4
    assert model.to_data() == [123, 234, [0, 1, 2, [0, 1, 2]]]

    assert model[-1][-1][-1] == 2

    model[-1][-1][-1] = 15
    assert model.to_data() == [123, 234, [0, 1, 2, [0, 1, 15]]]
    assert not isinstance(model[-1][-1], tuple)
    assert isinstance(model[-1][-1], Model)

    with pytest.raises(ValidationError):
        model[-1] += ('a',)
    with pytest.raises(ValidationError):
        model[-1][3] += ('b',)
    assert model.to_data() == [123, 234, [0, 1, 2, [0, 1, 15]]]


def test_model_operations_as_dict():
    model = Model[dict[str, int]]({'abc': 123})

    assert len(model) == 1
    assert model['abc'] == 123

    model['abc'] = 321
    model['bcd'] = 234
    model['cde'] = 345

    with pytest.raises(ValidationError):
        model['def'] = 'eggs'

    assert 'cde' in model
    assert 'def' not in model

    assert len(model) == 3
    assert model['abc'] == 321

    assert model.contents == {'abc': 321, 'bcd': 234, 'cde': 345}

    assert tuple(model.keys()) == ('abc', 'bcd', 'cde')
    assert tuple(model.values()) == (321, 234, 345)
    assert tuple(model.items()) == (('abc', 321), ('bcd', 234), ('cde', 345))

    assert isinstance(model, Model)
    model.update({'def': 456, 'efg': 567})
    assert 'def' in model
    assert isinstance(model, Model)

    model |= {'efg': 765, 'ghi': 678}
    assert model['efg'] == 765
    assert isinstance(model, Model)

    del model['bcd']

    other = {'abc': 321, 'cde': 345, 'def': 456, 'efg': 765, 'ghi': 678}
    assert model.contents == other
    assert model == Model[dict[str, int]](other)


def test_model_operations_as_nested_dict_no_validation_at_second_level():
    model = Model[dict[str, dict[int, int] | int]]({'a': {12: 234, 13: 345}})

    with pytest.raises(ValidationError):
        model['a'] = 'abc'

    with pytest.raises(ValidationError):
        model['a'] = None

    with pytest.raises(ValidationError):
        model['a'] = ['abc']

    # empty list is parsed as empty dict in pydantic v1
    model['a'] = []
    assert model.contents == {'a': {}}

    with pytest.raises(ValidationError):
        model['a'] = {'abc': 'bce'}

    model['a'] = {'14': '456'}
    assert model.contents == {'a': {14: 456}}

    # model['a'] is the result of an __getitem__ and is not wrapped as a Model
    assert isinstance(model, Model)
    assert not isinstance(model, dict)
    assert not isinstance(model['a'], Model)
    assert isinstance(model['a'], dict)

    # As model['a'] is not a Model, update() does not validate
    f = model['a']
    f.update({'14': '654', '15': {'a': 'b'}})
    assert len(model['a']) == 3
    assert model.contents == {'a': {14: 456, '14': '654', '15': {'a': 'b'}}}

    # The|= operator combines an "__or__" (which equals to update() for dicts)(
    with pytest.raises(ValidationError):
        model['a'] |= {'16': 'a'}

    assert model.contents == {'a': {14: 456}}


def test_model_operations_as_nested_dict_with_full_validation():
    model = Model[dict[str, Model[dict[int, Model[dict[int, int]] | int] | int]]]({
        'a': {
            12: 234, 13: 345
        }
    })

    with pytest.raises(ValidationError):
        model['a'] = 'abc'

    # See test_model_union_none_known_issue()
    #
    # with pytest.raises(ValidationError):
    #     model['a'] = None

    with pytest.raises(ValidationError):
        model['a'] = ['abc']

    model['a'] = []
    assert model.to_data() == ({'a': {}})

    with pytest.raises(ValidationError):
        model['a'] = {'abc': 'bce'}

    model['a'] = {'14': '456'}
    assert model.to_data() == ({'a': {14: 456}})

    assert isinstance(model, Model)
    assert not isinstance(model, dict)
    assert isinstance(model['a'], Model)
    assert not isinstance(model['a'], dict)

    with pytest.raises(ValidationError):
        model['a'].update({'14': '654', '15': {'a': 'b'}})

    assert len(model['a']) == 1
    assert model.to_data() == {'a': {14: 456}}

    with pytest.raises(ValidationError):
        model['a'].update({'14': '654', '15': {'111': {1: 2}}})

    model['a'].update({'14': '654', '15': {'111': 4321}})

    assert len(model['a']) == 2
    assert model.to_data() == {'a': {14: 654, 15: {111: 4321}}}

    with pytest.raises(ValidationError):
        model['a'] |= {'16': {'a': 'b'}}

    model['a'] |= {'16': {'112': 5432}}
    assert model.to_data() == {'a': {14: 654, 15: {111: 4321}, 16: {112: 5432}}}

    with pytest.raises(ValidationError):
        model['a'][15] |= {112: tuple(range(3))}

    with pytest.raises(ValidationError):
        model['a'][15] |= {'112': 'a'}

    with pytest.raises(ValidationError):
        model['a'][15] |= {'112': []}

    with pytest.raises(ValidationError):
        model['a'][15][111] = []

    model['a'][15] = []
    assert model.to_data() == {'a': {14: 654, 15: {}, 16: {112: 5432}}}


def test_model_operations_as_scalars():
    model = Model[int](1)

    assert (model + 1).contents == 2
    assert (1 + model).contents == 2
    assert model.contents == 1

    model *= 10
    assert model.contents == 10

    assert model / 3 == pytest.approx(3.333333)  # converting to other basic type removes Model
    assert (model // 3).contents == 3
    assert -model.contents == -10

    assert (model % 3).contents == 1  # modulo
    assert (model & 2).contents == 2  # bitwise AND
    assert (model**2).contents == 100  # power

    assert float(model) == float(10)  # converting to other basic type removes Model

    model = Model[float](10)
    assert (model / 3).contents == pytest.approx(3.333333)

    model = Model[float](2.5)
    assert floor(model) == 2  # converting to other basic type removes Model


def test_model_operations_as_union_of_scalars():
    model = Model[int | float](1)

    assert (model + 1).contents == 2
    assert (1 + model).contents == 2
    assert model.contents == 1

    model *= 10
    assert model.contents == 10

    assert (model / 3).contents == pytest.approx(3.333333)
    assert (model // 3).contents == 3
    assert -model.contents == -10

    assert (model % 3).contents == 1  # modulo
    assert (model & 2).contents == 2  # bitwise AND
    assert (model**2).contents == 100  # power

    assert float(model) == 10  # float(), int(), etc always converts


def test_model_copy():
    ...


def test_json_schema_generic_model_one_level():
    ListT = TypeVar('ListT', bound=list)  # noqa

    # Note that the TypeVars need to be bound to a type who in itself, or whose origin_type
    # produces a default value when called without parameters. Here, `ListT` is bound to list,
    # and `typing.get_origin(list)() == []`.

    class MyList(Model[ListT], Generic[ListT]):
        """My very interesting list model!"""

    assert MyList.to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyList",
      "description": "My very interesting list model!",
      "type": "array",
      "items": {}
    }""")

    assert MyList[list].to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyList[list]",
      "description": "My very interesting list model!",
      "type": "array",
      "items": {}
    }""")


def test_json_schema_generic_model_two_levels():
    StrT = TypeVar('StrT', bound=str)  # noqa

    class MyListOfStrings(Model[list[StrT]], Generic[StrT]):
        """My very own list of strings!"""

    assert MyListOfStrings.to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyListOfStrings",
      "description": "My very own list of strings!",
      "type": "array",
      "items": {
        "type": "string"
      }
    }""")

    assert MyListOfStrings[str].to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyListOfStrings[str]",
      "description": "My very own list of strings!",
      "type": "array",
      "items": {
        "type": "string"
      }
    }""")


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
Known issue due to shortcomings of the typing standard library.
Class variables of generic classes are not all available in
in runtime (see: https://github.com/python/typing/issues/629)
In this case, the description of the generic class MyList
is not available from MyListOfStrings to_json_schema method.
Any workarounds should best be implemented in pydantic,
possibly in omnipy if this becomes a real issue.
""")
def test_json_schema_generic_models_known_issue():
    ListT = TypeVar('ListT', bound=list)  # noqa

    class MyList(Model[ListT], Generic[ListT]):
        """My very interesting list model!"""

    class MyListOfStrings(Model[MyList[list[str]]]):
        """MyList. What more can you ask for?"""

    assert MyListOfStrings.to_json_schema(pretty=True) == dedent("""\
    {
      "title": "MyListOfStrings",
      "description": "MyList. What more can you ask for?",
      "$ref": "#/definitions/MyList_List_str__",
      "definitions": {
        "MyList_List_str__": {
          "title": "MyList[list[str]]",
          "description": "My very interesting list model!.",
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    }""")


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


def test_custom_parser_to_other_type():
    from .helpers.models import StringToLength

    assert StringToLength('So we sailed up to the sun').to_data() == 26
    string_to_length = StringToLength()
    string_to_length.from_data('Till we found the sea of green')
    assert string_to_length.to_data() == 30


def test_nested_model():
    class DictToListOfPositiveInts(Model[dict[PositiveInt, list[PositiveInt]]]):
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

    assert model_1.to_json(
        pretty=False) == ('{"2": [2], "3": [3], "4": [2, 2], "5": [5], "6": [2, 3], '
                          '"7": [7], "8": [2, 2, 2], "9": [3, 3], "10": [2, 5]}')

    model_2 = DictToListOfPositiveInts()
    model_2.from_json('{"2": [2], "3": [3], "4": [2, 2], "5": [5], "6": [2, 3], '
                      '"7": [7], "8": [2, 2, 2], "9": [3, 3], "10": [2, 5]}')
    assert sorted(model_2.to_data()) == sorted({
        2: [2], 3: [3], 4: [2, 2], 5: [5], 6: [2, 3], 7: [7], 8: [2, 2, 2], 9: [3, 3], 10: [2, 5]
    })

    assert model_1.to_json_schema() == dedent("""\
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
    }""")


def test_complex_nested_models():
    class ProductFactorsTuple(Model[tuple[PositiveInt, list[PositiveInt]]]):
        """This model maps a single product to its product_factors, including validation"""
        @classmethod
        def _parse_data(
                cls, data: tuple[PositiveInt,
                                 list[PositiveInt]]) -> tuple[PositiveInt, list[PositiveInt]]:
            from functools import reduce
            from operator import mul

            product, factors = data
            assert reduce(mul, factors) == product
            return data

    class ListOfProductFactorsTuples(Model[list[ProductFactorsTuple]]):
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

    class ListOfProductFactorsTuplesRoman(Model[list[tuple[RomanNumeral, list[RomanNumeral]]]]):
        """A list of ProductFactorsTuples with RomanNumerals"""

    class ProductFactorDictInRomanNumerals(Model[dict[str, list[str]]]):
        """Extremely useful model"""

    roman_tuple_model = ListOfProductFactorsTuplesRoman(unloaded_data)
    roman_dict_model_1 = ProductFactorDictInRomanNumerals(roman_tuple_model.to_data())

    assert roman_dict_model_1.to_json(
        pretty=False) == ('{"II": ["II"], "III": ["III"], "IV": ["II", "II"], "V": ["V"], '
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

    assert roman_dict_model_1.to_json_schema() == dedent("""\
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
    }""")


def test_pandas_dataframe_non_builtin_direct():
    # TODO: Using pandas here to test concept of non-builtin data structures. Switch to other
    #  example to remove dependency, to prepare splitting of pandas module to separate repo

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
