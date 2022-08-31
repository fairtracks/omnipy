from inspect import Parameter
from typing import Union

import pytest

from unifair.compute.task import Task, TaskTemplate


@pytest.fixture
def simple_func():
    def simple_func(text: str, number: int) -> str:
        return '{}: {}'.format(text, number)

    return simple_func


def _assert_default_values(task_obj: Union[TaskTemplate, Task]):
    assert task_obj.param_signatures == {
        'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
        'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
    }
    assert task_obj.return_type == str

    assert task_obj.name == 'simple_func'
    assert task_obj.param_key_map == {}
    assert task_obj.result_key is None
    assert task_obj.fixed_params == {}


def test_simple_task_run_in_default_state(simple_func):
    task_template = TaskTemplate(simple_func)
    assert isinstance(task_template, TaskTemplate)

    task = task_template.apply()
    assert isinstance(task, Task)

    assert task('Number', 12) == 'Number: 12'

    _assert_default_values(task_template)
    _assert_default_values(task)


@pytest.fixture
def power_func():
    def power_func(number: int, exponent: int, minus_one: bool = True) -> int:
        return number**exponent - (1 if minus_one else 0)

    return power_func


def test_runtime_task_parameters(power_func):
    power_template = TaskTemplate(power_func)
    with pytest.raises(TypeError):
        power_template()

    power = power_template.apply()

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


def test_name(power_func):
    power_template = TaskTemplate(power_func, name=None)
    assert power_template.name == 'power_func'

    power = power_template.apply()
    assert power.name == 'power_func'

    power_template = TaskTemplate(power_func, name='power')
    assert power_template.name == 'power'

    power = power_template.apply()
    assert power.name == 'power'

    with pytest.raises(ValueError):
        TaskTemplate(power_func, name='')

    power_template = TaskTemplate(power_func, name=123)
    assert power_template.name == '123'

    power = power_template.apply()
    assert power.name == '123'


def test_task_result_key(power_func):
    power_template = TaskTemplate(power_func, result_key=None)
    assert power_template.result_key is None

    power = power_template.apply()
    assert power.result_key is None
    assert power(4, 2) == 15

    power_template = TaskTemplate(power_func, result_key='power')
    assert power_template.result_key == 'power'

    power = power_template.apply()
    assert power.result_key == 'power'
    assert power(4, 2) == {'power': 15}

    with pytest.raises(ValueError):
        TaskTemplate(power_func, result_key='')

    power_template = TaskTemplate(power_func, result_key=123)
    assert power_template.result_key == '123'

    power = power_template.apply()
    assert power.result_key == '123'
    assert power(4, 2) == {'123': 15}


def test_task_param_key_map(power_func):
    power_template = TaskTemplate(
        power_func, param_key_map=dict(
            number='n',
            exponent='e',
            minus_one='m',
        ))

    assert power_template.param_key_map == {'number': 'n', 'exponent': 'e', 'minus_one': 'm'}

    power = power_template.apply()
    assert power.param_key_map == dict(number='n', exponent='e', minus_one='m')

    assert power(n=4, e=2) == 15

    with pytest.raises(TypeError):
        power(number=4, exponent=2)

    power_template = TaskTemplate(
        power_func, param_key_map=[('number', 'n'), ('exponent', 'e')])  # noqa
    assert power_template.param_key_map == {'number': 'n', 'exponent': 'e'}

    with pytest.raises(ValueError):
        TaskTemplate(power_func, param_key_map={'number': 'n', 'exponent': 'n'})

    power_template = TaskTemplate(power_func, param_key_map={'number': 'n'})  # noqa
    assert power_template.param_key_map == {'number': 'n'}

    power = power_template.apply()
    assert power.param_key_map == {'number': 'n'}

    assert power(n=3, exponent=2) == 8

    power_template = TaskTemplate(power_func, param_key_map=None)  # noqa
    assert power_template.param_key_map == {}

    power_template = TaskTemplate(power_func, param_key_map={})  # noqa
    assert power_template.param_key_map == {}

    power_template = TaskTemplate(power_func, param_key_map=[])  # noqa
    assert power_template.param_key_map == {}

    power = power_template.apply()
    assert power.param_key_map == {}

    assert power(number=3, exponent=2) == 8


def test_fixed_task_parameters(power_func):
    square_template = TaskTemplate(power_func, fixed_params=dict(exponent=2, minus_one=False))
    square = square_template.apply()
    assert square(4) == 16
    assert square.fixed_params['exponent'] == 2
    assert square.fixed_params['minus_one'] is False

    assert square(number=5) == 25

    seven_template = TaskTemplate(power_func, fixed_params=[('number', 2), ('exponent', 3)])  # noqa
    seven = seven_template.apply()

    assert seven() == 7
    assert seven_template.fixed_params == {'number': 2, 'exponent': 3}
    assert seven.fixed_params == {'number': 2, 'exponent': 3}

    power_template = TaskTemplate(power_func, fixed_params=None)  # noqa
    assert power_template.fixed_params == {}

    power_template = TaskTemplate(power_func, fixed_params={})
    assert power_template.fixed_params == {}

    power_template = TaskTemplate(power_func, fixed_params=[])  # noqa
    assert power_template.fixed_params == {}

    power = power_template.apply()
    assert power.param_key_map == {}

    assert power(number=2, exponent=3) == 7


def test_error_missing_or_duplicate_runtime_task_params_with_fixed(power_func):
    square = TaskTemplate(power_func, fixed_params=dict(exponent=2, minus_one=False)).apply()

    with pytest.raises(TypeError):
        square()

    with pytest.raises(TypeError):
        square(4, 3)

    with pytest.raises(TypeError):
        square(4, minus_one=False)


def test_error_fixed_param_not_in_func_signature(power_func):
    with pytest.raises(KeyError):
        TaskTemplate(power_func, fixed_params=dict(engine='hyperdrive'))

    task_template = TaskTemplate(power_func)

    assert 'engine' not in task_template.fixed_params


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
        task_obj.param_key_map = {'text': 'title'}

    with pytest.raises(TypeError):
        task_obj.param_key_map['text'] = 'title'

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


def test_refine_task_template_with_fixed_params(power_func):
    power_template = TaskTemplate(power_func)
    power = power_template.apply()

    assert power(4, 2) == 15

    square_template = power_template.refine(fixed_params=dict(exponent=2, minus_one=False))
    assert square_template.fixed_params == dict(exponent=2, minus_one=False)

    square = square_template.apply()

    assert square.fixed_params['minus_one'] is False
    assert square(3) == 9

    cube_template = square_template.refine(fixed_params=[('exponent', 3)])  # noqa
    assert cube_template.fixed_params == dict(exponent=3, minus_one=False)

    cube = cube_template.apply()

    assert cube.fixed_params['minus_one'] is False
    assert cube(3) == 27

    hypercube_template = cube_template.refine(fixed_params=dict(exponent=4), update=False)
    assert hypercube_template.fixed_params == dict(exponent=4)

    hypercube = hypercube_template.apply()

    assert hypercube.fixed_params.get('minus_one') is None
    assert hypercube(3) == 80

    reset_power_template = hypercube_template.refine(fixed_params={})
    assert reset_power_template.fixed_params == dict(exponent=4)

    reset_power_template = hypercube_template.refine(fixed_params={}, update=False)
    assert reset_power_template.fixed_params == {}

    reset_power_template = hypercube_template.refine(fixed_params=[], update=False)  # noqa
    assert reset_power_template.fixed_params == {}

    reset_power_template = hypercube_template.refine(fixed_params=None, update=False)  # noqa
    assert reset_power_template.fixed_params == {}

    reset_power = reset_power_template.apply()

    assert reset_power.fixed_params.get('minus_one') is None
    assert reset_power(4, 2) == 15


def test_refine_task_template_with_config_change(power_func):
    power_template = TaskTemplate(power_func)
    power = power_template.apply()

    assert power(4, 2) == 15

    my_power_template = power_template.refine(
        name='my_power',
        param_key_map=dict(number='num', exponent='exp'),
        result_key='my_power_result',
    )
    my_power = my_power_template.apply()

    assert my_power(num=3, exp=3) == {'my_power_result': 26}
    assert my_power.name == 'my_power'
    assert my_power.param_key_map == dict(number='num', exponent='exp')
    assert my_power.result_key == 'my_power_result'

    my_power_template = my_power_template.refine(
        param_key_map=[('exponent', 'expo'), ('minus_one', 'min')],)  # noqa
    my_power = my_power_template.apply()

    assert my_power(num=3, expo=3, min=False) == {'my_power_result': 27}
    assert my_power.name == 'my_power'
    assert my_power.param_key_map == dict(number='num', exponent='expo', minus_one='min')
    assert my_power.result_key == 'my_power_result'

    my_power_template = power_template.refine(
        param_key_map=dict(exponent='expo', minus_one='min'), update=False)
    my_power = my_power_template.apply()

    assert my_power(number=3, expo=3, min=False) == 27
    assert my_power.name == 'power_func'
    assert my_power.param_key_map == dict(exponent='expo', minus_one='min')
    assert my_power.result_key is None

    my_new_power_template = my_power_template.refine(param_key_map={})
    assert my_new_power_template.param_key_map == dict(exponent='expo', minus_one='min')

    my_new_power_template = my_power_template.refine(param_key_map={}, update=False)
    assert my_new_power_template.param_key_map == {}

    my_new_power_template = my_power_template.refine(param_key_map=[], update=False)  # noqa
    assert my_new_power_template.param_key_map == {}

    my_new_power_template = my_power_template.refine(param_key_map=None, update=False)  # noqa
    assert my_new_power_template.param_key_map == {}

    my_new_power = my_new_power_template.apply()

    assert my_new_power(number=3, exponent=3, minus_one=False) == 27
    assert my_new_power.param_key_map == {}


def test_revise_refine_task_template_with_fixed_params_and_config_change(power_func):
    square = TaskTemplate(power_func).refine(
        name='square',
        param_key_map=dict(number='num', exponent='exp'),
        fixed_params=dict(exponent=2, minus_one=False),
    ).apply()

    assert square(num=3) == 9

    assert square.name == 'square'
    assert square.param_key_map == dict(number='num', exponent='exp')
    assert square.result_key is None
    assert square.fixed_params == {'exponent': 2, 'minus_one': False}

    square_revised_template = square.revise()
    assert isinstance(square_revised_template, TaskTemplate)

    assert square_revised_template.name == 'square'
    assert square_revised_template.param_key_map == dict(number='num', exponent='exp')
    assert square_revised_template.result_key is None
    assert square_revised_template.fixed_params == {'exponent': 2, 'minus_one': False}

    square_refined = square_revised_template.refine(
        name=square_revised_template.name,
        fixed_params=square_revised_template.fixed_params,
        update=False).apply()

    assert square_refined.name == 'square'
    assert square_refined.param_key_map == {}
    assert square_refined.result_key is None
    assert square_refined.fixed_params == {'exponent': 2, 'minus_one': False}

    power_reset = square_refined.revise().refine(update=False).apply()

    assert power_reset.name == 'power_func'
    assert power_reset.param_key_map == {}
    assert power_reset.result_key is None
    assert power_reset.fixed_params == {}


# TODO: test that different TaskTemplates and Tasks do not edit same dicts
def test_no_shared_dicts(power_func):
    square_template = TaskTemplate(
        power_func,
        name='square',
        param_key_map=dict(number='num'),
        fixed_params=dict(exponent=2),
    )

    square = square_template.apply()
    square_refined_template = square_template.refine(
        param_key_map=dict(exponent='exp'),
        fixed_params=dict(minus_one=False),
    )
    square_revised_template = square.revise()
    square_revised_refined_template = square_revised_template.refine(
        param_key_map=dict(exponent='exp'),
        fixed_params=dict(minus_one=False),
    )

    assert len(square_refined_template.param_key_map) == 2
    assert len(square_refined_template.fixed_params) == 2

    assert len(square_revised_refined_template.param_key_map) == 2
    assert len(square_revised_refined_template.fixed_params) == 2

    assert len(square_revised_template.param_key_map) == 1
    assert len(square_revised_template.fixed_params) == 1

    assert len(square_template.param_key_map) == 1
    assert len(square_template.fixed_params) == 1

    assert len(square.param_key_map) == 1
    assert len(square.fixed_params) == 1


def test_error_refine_task_unmatched_params(power_func):
    power_template = TaskTemplate(power_func)

    with pytest.raises(KeyError):
        _power_template = TaskTemplate(power_func, param_key_map={'engine': 'motor'})

    with pytest.raises(KeyError):
        _power_template = TaskTemplate(power_func, fixed_params={'engine': 'volkswagen'})

    with pytest.raises(KeyError):
        _cube = power_template.refine(param_key_map={'engine': 'horsepower'})

    with pytest.raises(KeyError):
        _cube = power_template.refine(fixed_params={'engine': 'toyota'})
