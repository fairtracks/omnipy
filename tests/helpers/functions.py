import json
import subprocess
import sys

from omnipy.data.model import Model
from omnipy.shared.typedefs import TypeForm
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


def get_pip_installed_packages() -> set[str]:
    reqs_json = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--format=json'])
    reqs = json.loads(reqs_json)
    return set(req['name'] for req in reqs)
