from dataclasses import fields
from types import MappingProxyType

from pydantic import ValidationError
import pytest
import pytest_cases as pc

from omnipy.data.model import Model
from omnipy.modules.frozen.models import (_FrozenAnyUnionM,
                                          _FrozenScalarM,
                                          NestedFrozenDictsOrTuplesModel,
                                          NestedFrozenOnlyDictsModel,
                                          NestedFrozenOnlyTuplesModel)
from omnipy.modules.frozen.typedefs import FrozenDict

from ..helpers.classes import CaseInfo


def test_frozen_scalar() -> None:
    class FrozenScalarModel(Model[_FrozenScalarM[int]]):
        ...

    assert FrozenScalarModel().contents == _FrozenScalarM[int](0)

    with pytest.raises(ValidationError):
        FrozenScalarModel(None)

    with pytest.raises(ValidationError):
        FrozenScalarModel('hello')

    assert FrozenScalarModel(1).contents == _FrozenScalarM[int](1)


def test_frozen_scalar_of_none() -> None:
    class FrozenScalarModel(Model[_FrozenScalarM[None]]):
        ...

    assert FrozenScalarModel().contents == _FrozenScalarM[None](None)
    assert FrozenScalarModel(None).contents == _FrozenScalarM[None](None)

    with pytest.raises(ValidationError):
        FrozenScalarModel([None])

    with pytest.raises(ValidationError):
        FrozenScalarModel(123)


def test_frozen_dict_of_none() -> None:
    class NoneModel(Model[None]):
        ...

    class FrozenDictsOfInt2NoneModel(Model[FrozenDict[int, NoneModel]]):
        ...

    assert FrozenDictsOfInt2NoneModel().contents == FrozenDict()

    with pytest.raises(ValidationError):
        FrozenDictsOfInt2NoneModel(None)

    with pytest.raises(ValidationError):
        FrozenDictsOfInt2NoneModel([None])

    assert FrozenDictsOfInt2NoneModel({1: None}).contents == FrozenDict({1: NoneModel(None)})
    assert FrozenDictsOfInt2NoneModel(FrozenDict({1: None
                                                  })).contents == FrozenDict({1: NoneModel(None)})

    with pytest.raises(ValidationError):
        FrozenDictsOfInt2NoneModel({'hello': None})


def test_nested_frozen_only_tuples() -> None:
    class NestedFrozenTuplesOfIntsModel(
            Model[NestedFrozenOnlyTuplesModel[int]],):
        ...

    assert NestedFrozenTuplesOfIntsModel().to_data() == ()

    with pytest.raises(ValidationError):
        NestedFrozenTuplesOfIntsModel(None)

    with pytest.raises(ValidationError):
        NestedFrozenTuplesOfIntsModel([None])

    with pytest.raises(ValidationError):
        NestedFrozenTuplesOfIntsModel([None, 1])

    with pytest.raises(ValidationError):
        NestedFrozenTuplesOfIntsModel([1, 'hello'])

    with pytest.raises(ValidationError):
        NestedFrozenTuplesOfIntsModel({1: 2})

    with pytest.raises(ValidationError):
        NestedFrozenTuplesOfIntsModel([[1, None]])

    assert NestedFrozenTuplesOfIntsModel(('1', [2, '3'])).to_data() == (1, (2, 3))


def test_nested_frozen_only_tuples_of_none() -> None:
    class NestedFrozenOnlyTuplesOfNoneModel(
            Model[NestedFrozenOnlyTuplesModel[None]],):
        ...

    assert NestedFrozenOnlyTuplesOfNoneModel().to_data() == ()

    with pytest.raises(ValidationError):
        NestedFrozenOnlyTuplesOfNoneModel(None)

    assert NestedFrozenOnlyTuplesOfNoneModel([None]).to_data() == (None,)

    assert NestedFrozenOnlyTuplesOfNoneModel((None, None)).to_data() == (None, None)

    with pytest.raises(ValidationError):
        NestedFrozenOnlyTuplesOfNoneModel(['hello', None])

    with pytest.raises(ValidationError):
        assert NestedFrozenOnlyTuplesOfNoneModel({None: None})

    assert NestedFrozenOnlyTuplesOfNoneModel([[None, None]]).to_data() == ((None, None),)

    assert NestedFrozenOnlyTuplesOfNoneModel(
        (None, [None, (None, None)])).to_data() == (None, (None, (None, None)))


def test_nested_frozen_only_dicts() -> None:
    class NestedFrozenOnlyDictsOfInt2StrModel(
            Model[NestedFrozenOnlyDictsModel[int, str]],):
        ...

    assert NestedFrozenOnlyDictsOfInt2StrModel().to_data() == {}

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2StrModel(None)

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2StrModel([None])

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2StrModel({None: 1})

    assert NestedFrozenOnlyDictsOfInt2StrModel({
        1: 'hello'
    }).to_data() == MappingProxyType({1: 'hello'})

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2StrModel({1: None})

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2StrModel([(1, 'str', 5)])

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2StrModel({1: [1, None]})

    assert NestedFrozenOnlyDictsOfInt2StrModel({
        '1': {
            '2': 3
        }
    }).to_data() == MappingProxyType({1: {
        2: '3'
    }})


def test_nested_frozen_only_dicts_of_none() -> None:
    class NestedFrozenOnlyDictsOfInt2NoneModel(
            Model[NestedFrozenOnlyDictsModel[int, None]],):
        ...

    assert NestedFrozenOnlyDictsOfInt2NoneModel().to_data() == {}

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2NoneModel(None)

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2NoneModel([None])

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2NoneModel({None: 1})

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2NoneModel({'hello': None})

    assert NestedFrozenOnlyDictsOfInt2NoneModel({
        '4': None
    }).to_data() == MappingProxyType({4: None})

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2NoneModel([(1, 'str', 5)])

    with pytest.raises(ValidationError):
        NestedFrozenOnlyDictsOfInt2NoneModel({1: [1, None]})

    assert NestedFrozenOnlyDictsOfInt2NoneModel({
        '1': {
            '2': None
        }
    }).to_data() == MappingProxyType({1: {
        2: None
    }})


def test_nested_frozen_dicts_or_tuples() -> None:
    class NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel(
            Model[NestedFrozenDictsOrTuplesModel[int, int]],):
        ...

    assert NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel().to_data() == 0

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel(None)

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel([None])

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel({None: 1})

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel({1: 'hello'})

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel({1: None})

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel([{1: None}])

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel({1: [1, None]})

    assert NestedFrozenDictsOfInt2IntOrTuplesOfIntsModel({
        '1': [2, '3']
    }).to_data() == MappingProxyType({1: (2, 3)})


def test_nested_frozen_dicts_or_tuples_of_none() -> None:
    _FrozenAnyUnionM[int, None](None)

    class NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel(
            Model[NestedFrozenDictsOrTuplesModel[int, None]],):
        ...

    assert NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel().to_data() is None

    assert NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel(None).to_data() is None

    assert NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel([None]).to_data() == (None,)

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel({None: None})

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel({'hello': None})

    assert NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel({1: None}).to_data() == {1: None}

    assert NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel([{1: None}]).to_data() == ({1: None},)

    with pytest.raises(ValidationError):
        NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel({1: [1, None]})

    assert NestedFrozenDictsOfInt2NoneOrTuplesOfNoneModel({
        '1': [None, None]
    }).to_data() == {
        1: (None, None)
    }


@pc.parametrize_with_cases('case', cases='.cases.frozen_data')
def test_nested_frozen_models(case: CaseInfo) -> None:
    for field in fields(case.data_points):
        name = field.name
        for model_cls in case.model_classes_for_data_point(name):
            data = getattr(case.data_points, name)

            # print('\n---')
            # print(f'Field name: {name}')
            # print(f'Model class: {model_cls.__name__}')
            # print(f'Data input: {data}')

            if case.data_point_should_fail(name):
                with pytest.raises(ValidationError):
                    model_cls(data)
            else:
                model_cls(data)
                # model_obj = model_cls(data)

                # print(f'repr(model_obj): {repr(model_obj)}')
                # print(f'model_obj.contents: {model_obj.contents}')
                # print(f'model_obj.to_data(): {model_obj.to_data()}')
