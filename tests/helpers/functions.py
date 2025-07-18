import json
import subprocess
import sys

from omnipy.data.model import Model
from omnipy.shared.typedefs import TypeForm
from omnipy.util.helpers import all_type_variants, ensure_plain_type


def assert_model(model: object, target_type: TypeForm, content: object):
    assert isinstance(model, Model)
    assert model.outer_type(with_args=True) == target_type, \
        f'{model.outer_type(with_args=True)} != {target_type}'
    assert model.content == content, f'{model.content} != {content}'


def assert_val(value: object, target_type: TypeForm, content: object):
    assert not isinstance(value, Model)
    assert any(
        isinstance(value, ensure_plain_type(_type)) for _type in all_type_variants(target_type))
    assert value == content, f'{value} != {content}'


def assert_model_or_val(model_or_val: object, target_type: TypeForm, content: object) -> None:
    if isinstance(model_or_val, Model):
        assert_model(model_or_val, target_type, content)
    else:
        assert_val(model_or_val, target_type, content)


def get_pip_installed_packages() -> set[str]:
    reqs_json = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--format=json'])
    reqs = json.loads(reqs_json)
    return set(req['name'] for req in reqs)
