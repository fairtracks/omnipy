import pytest

from omnipy.components.general.models import (Chain2,
                                              Chain3,
                                              Chain4,
                                              Chain5,
                                              Chain6,
                                              NotIterableExceptStrOrBytesModel)
from omnipy.data.model import Model
from omnipy.util._pydantic import ValidationError

from .helpers.models import MyList, MyListModel, RotateOneCharModel, SplitCharsModel


def test_not_iterable_except_str_model():
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
    class SplitCharsToMyListModel(Chain2[
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    stream = SplitCharsModel('abc') + SplitCharsToMyListModel('def')
    assert stream.to_data() == ['a', 'b', 'c', 'd', 'e', 'f']

    stream = SplitCharsToMyListModel('abc') + SplitCharsModel('def')
    assert stream.to_data() == ['a', 'b', 'c', 'd', 'e', 'f']


def test_chain2_union_models():
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
