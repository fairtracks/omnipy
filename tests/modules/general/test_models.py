import pytest

from omnipy.modules.general.models import (Chain2,
                                           Chain3,
                                           Chain4,
                                           Chain5,
                                           Chain6,
                                           NotIterableExceptStrOrBytesModel)
from omnipy.util.pydantic import ValidationError

from .helpers.models import MyList, MyListModel, RotateOneCharModel, SplitCharsModel


def test_not_iterable_except_str_model():
    assert NotIterableExceptStrOrBytesModel().contents is None
    assert NotIterableExceptStrOrBytesModel(None).contents is None
    assert NotIterableExceptStrOrBytesModel(1234).contents == 1234
    assert NotIterableExceptStrOrBytesModel(True).contents is True

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel((1, 2, 3, 4))

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel([1, 2, 3, 4])

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel({1: 2, 3: 4})

    with pytest.raises(ValidationError):
        NotIterableExceptStrOrBytesModel({1, 2, 3, 4})

    assert NotIterableExceptStrOrBytesModel('1234').contents == '1234'
    assert NotIterableExceptStrOrBytesModel('æøå'.encode('utf8')).contents == 'æøå'.encode('utf8')


def test_chain2_model():

    MyListModel(MyList(['a', 'b', 'c']))

    class SplitCharsToMyListModel(Chain2[
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    model = SplitCharsToMyListModel('abc')
    assert model.contents == MyListModel(MyList('a', 'b', 'c'))
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


def test_chain3_model():
    class RotateOneAndSplitCharsToMyListModel(Chain3[
            RotateOneCharModel,
            SplitCharsModel,
            MyListModel,
    ]):
        ...

    model = RotateOneAndSplitCharsToMyListModel('abcdefg')
    assert model.contents == MyListModel(MyList('b', 'c', 'd', 'e', 'f', 'g', 'a'))
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
    assert model.contents == MyListModel(MyList('c', 'd', 'e', 'f', 'g', 'a', 'b'))
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
    assert model.contents == MyListModel(MyList('d', 'e', 'f', 'g', 'a', 'b', 'c'))
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
    assert model.contents == MyListModel(MyList('e', 'f', 'g', 'a', 'b', 'c', 'd'))
    assert model.to_data() == ['e', 'f', 'g', 'a', 'b', 'c', 'd']
