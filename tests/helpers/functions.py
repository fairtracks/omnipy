from omnipy import Model
from omnipy.api.typedefs import TypeForm
from omnipy.util.helpers import ensure_plain_type


def assert_model(model: object, target_type: TypeForm, contents: object):
    assert isinstance(model, Model)
    assert model.outer_type(with_args=True) == target_type, \
        f'{model.outer_type(with_args=True)} != {target_type}'
    assert model.contents == contents, f'{model.contents} != {contents}'


def assert_val(value: object, target_type: TypeForm, contents: object):
    assert not isinstance(value, Model)
    assert isinstance(value, ensure_plain_type(target_type))
    assert value == contents


def assert_model_or_val(dyn_convert: bool,
                        model_or_val: object,
                        target_type: TypeForm,
                        contents: object):
    if dyn_convert:
        assert_model(model_or_val, target_type, contents)
    else:
        assert_val(model_or_val, target_type, contents)
