import pytest

from omnipy.api.typedefs import TypeForm
from omnipy.data.model import Model
from omnipy.util.helpers import ensure_plain_type


def assert_model(model: object, target_type: TypeForm, contents: object):
    assert isinstance(model, Model)
    assert model.outer_type(with_args=True) == target_type, \
        f'{model.outer_type(with_args=True)} != {target_type}'
    assert model.contents == contents, f'{model.contents} != {contents}'


def assert_val(value: object, target_type: TypeForm, contents: object):
    assert not isinstance(value, Model)
    assert isinstance(value, ensure_plain_type(target_type))
    assert value == contents, f'{value} != {contents}'
