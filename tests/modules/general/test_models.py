from pydantic import ValidationError
import pytest

from omnipy.modules.general.models import NotIterableExceptStrOrBytesModel


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
