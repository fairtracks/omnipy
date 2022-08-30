from inspect import Parameter
from typing import Union

import pytest

from unifair.compute.task import Task, TaskTemplate


@pytest.fixture
def simple_func():
    def simple_func(text: str, number: int) -> str:
        return '{}: {}'.format(text, number)

    return simple_func

    # mytask = TaskTemplate(simple_func, fixed_params={'text': 'Number'})
    # mytask_template = mytask.refine(name='mytask')
    # mytask = mytask_template.apply()
    # mytask_template_2 = mytask.revise()


def test_simple_task_run(simple_func):
    mytask = TaskTemplate(simple_func).apply()
    assert mytask('Number', 12) == 'Number: 12'

    assert mytask.param_signatures == {
        'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
        'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    }
    assert mytask.return_type == str

    assert mytask.name == 'simple_func'
    assert mytask.param_map_keys == {}
    assert mytask.result_key is None
    assert mytask.fixed_params == {}


def _assert_config_properties_immutable(task_obj: Union[TaskTemplate, Task]):
    with pytest.raises(AttributeError):
        task_obj.param_signatures = {}  # noqa

    with pytest.raises(TypeError):
        task_obj.param_signatures['new'] = Parameter(
            'new', Parameter.POSITIONAL_OR_KEYWORD, annotation=bool)

    with pytest.raises(AttributeError):
        task_obj.return_type = int

    with pytest.raises(AttributeError):
        task_obj.name = 'cool_func'

    with pytest.raises(AttributeError):
        task_obj.param_map_keys = {'text': 'title'}

    with pytest.raises(TypeError):
        task_obj.param_map_keys['text'] = 'title'

    with pytest.raises(AttributeError):
        task_obj.result_key = 'cool_func'

    with pytest.raises(AttributeError):
        task_obj.fixed_params = {'title': 'Integer'}

    with pytest.raises(TypeError):
        task_obj.fixed_params['title'] = 'Integer'


def test_task_properties_immutable(simple_func):
    task_template = TaskTemplate(simple_func)
    _assert_config_properties_immutable(task_template)

    task = task_template.apply()
    _assert_config_properties_immutable(task)


@pytest.fixture
def power_func():
    def power_func(number: int, exponent: int, minus_one: bool = True) -> int:
        return number**exponent - (1 if minus_one else 0)

    return power_func


def test_runtime_task_parameters(power_func):
    power = TaskTemplate(power_func).apply()

    assert power(4, 3) == 63
    assert 'exponent' not in power.fixed_params
    assert 'minus_one' not in power.fixed_params

    assert power(4, 3, False) == 64
    assert 'minus_one' not in power.fixed_params

    assert power(number=5, exponent=2) == 24
    assert 'number' not in power.fixed_params
    assert 'exponent' not in power.fixed_params


def test_error_missing_runtime_task_parameters(power_func):
    power = TaskTemplate(power_func).apply()

    with pytest.raises(TypeError):
        power()

    with pytest.raises(TypeError):
        power(5)

    with pytest.raises(TypeError):
        power(4, minus_one=False)


def test_fixed_task_parameters(power_func):
    square = TaskTemplate(power_func, fixed_params=dict(exponent=2, minus_one=False)).apply()
    assert square(4) == 16
    assert square.fixed_params['exponent'] == 2
    assert square.fixed_params['minus_one'] is False

    assert square(number=5) == 25


def test_error_missing_or_duplicate_runtime_task_params_with_fixed(power_func):
    square = TaskTemplate(power_func, fixed_params=dict(exponent=2, minus_one=False)).apply()

    with pytest.raises(TypeError):
        square()

    with pytest.raises(TypeError):
        square(4, 3)

    with pytest.raises(TypeError):
        square(4, minus_one=False)


def test_error_parameter_not_in_func_signature(power_func):
    with pytest.raises(KeyError):
        TaskTemplate(power_func, fixed_params=dict(engine='hyperdrive'))

    task = TaskTemplate(power_func)

    with pytest.raises(KeyError):
        _mytask = task.fixed_params['engine']
