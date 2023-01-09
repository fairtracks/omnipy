from inspect import Parameter
from typing import Annotated

import pytest
import pytest_cases as pc

from unifair.compute.task import Task, TaskTemplate

from .cases.raw.functions import format_to_string_func, power_m1_func
from .cases.tasks import TaskCase
from .helpers.functions import assert_updated_wrapper
from .helpers.mocks import MockLocalRunner


def test_init() -> None:
    task_template = TaskTemplate(format_to_string_func)
    assert isinstance(task_template, TaskTemplate)  # noqa
    assert_updated_wrapper(task_template, format_to_string_func)

    with pytest.raises(TypeError):
        TaskTemplate('extra_positional_argument')(format_to_string_func)

    with pytest.raises(RuntimeError):
        Task(format_to_string_func)

    task = task_template.apply()  # noqa
    assert isinstance(task, Task)
    assert_updated_wrapper(task, format_to_string_func)


@pc.parametrize_with_cases('case', cases='.cases.tasks')
def test_task_run(mock_local_runner: Annotated[MockLocalRunner, pytest.fixture],
                  case: TaskCase) -> None:
    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is False

    task_template = TaskTemplate(case.task_func)
    assert_updated_wrapper(task_template, case.task_func)

    with pytest.raises(TypeError):
        task_template(*case.args, **case.kwargs)

    task = task_template.apply()
    assert_updated_wrapper(task, case.task_func)

    result = task(*case.args, **case.kwargs)

    case.assert_results_func(result)

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is True


def test_task_run_parameter_variants(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]) -> None:

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is False

    power_m1 = TaskTemplate(power_m1_func)

    assert power_m1.run(4, 3) == 63
    assert power_m1.run(4, exponent=3) == 63
    assert power_m1.run(number=4, exponent=3) == 63
    assert power_m1.run(4, 3, False) == 64
    assert power_m1.run(4, 3, minus_one=False) == 64
    assert power_m1.run(4, exponent=3, minus_one=False) == 64
    assert power_m1.run(number=4, exponent=3, minus_one=False) == 64

    if hasattr(mock_local_runner, 'finished'):
        assert mock_local_runner.finished is True


def test_error_missing_task_run_parameters() -> None:
    power_m1 = TaskTemplate(power_m1_func).apply()

    with pytest.raises(TypeError):
        power_m1()

    with pytest.raises(TypeError):
        power_m1(5)

    with pytest.raises(TypeError):
        power_m1(4, minus_one=False)


@pc.parametrize_with_cases('case', cases='.cases.tasks')
def test_property_param_signature_and_return_type(case: TaskCase) -> None:

    task_template = TaskTemplate(case.task_func)

    for task_obj in task_template, task_template.apply():
        case.assert_signature_and_return_type_func(task_obj)


def test_property_param_signature_and_return_type_immutable() -> None:

    task_template = TaskTemplate(format_to_string_func)

    for task_obj in task_template, task_template.apply():
        with pytest.raises(AttributeError):
            task_obj.param_signatures = {}  # noqa

        with pytest.raises(TypeError):
            task_obj.param_signatures['new'] = Parameter(  # noqa
                'new', Parameter.POSITIONAL_OR_KEYWORD, annotation=bool)

        with pytest.raises(AttributeError):
            task_obj.return_type = int


def test_property_fixed_params_default() -> None:

    power_m1_template = TaskTemplate(power_m1_func)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.fixed_params == {}

    power_m1 = power_m1_template.apply()
    assert power_m1(number=4, exponent=3) == 63

    for val in ({}, [], None):
        power_m1_template = TaskTemplate(power_m1_func, fixed_params=val)  # noqa
        for power_m1_obj in power_m1_template, power_m1_template.apply():
            assert power_m1_obj.fixed_params == {}


def test_property_fixed_params_last_args() -> None:

    square_template = TaskTemplate(
        power_m1_func,
        fixed_params=dict(
            exponent=2,
            minus_one=False,
        ),
    )

    for square_obj in square_template, square_template.apply():
        assert square_obj.fixed_params == {
            'exponent': 2,
            'minus_one': False,
        }

    square = square_template.apply()

    assert square(4) == 16
    assert square(number=5) == 25

    with pytest.raises(TypeError):
        square()

    with pytest.raises(TypeError):
        square(exponent=5)

    with pytest.raises(TypeError):
        square(minus_one=True)

    with pytest.raises(TypeError):
        square(4, 3)

        with pytest.raises(TypeError):
            square(4, minus_one=True)


def test_property_fixed_params_first_arg() -> None:

    two_power_m1_template = TaskTemplate(
        power_m1_func,
        fixed_params=dict(number=2),
    )

    for two_power_m1_obj in two_power_m1_template, two_power_m1_template.apply():
        assert two_power_m1_obj.fixed_params == {
            'number': 2,
        }

    two_power_m1 = two_power_m1_template.apply()
    assert two_power_m1(exponent=4) == 15
    assert two_power_m1(exponent=4, minus_one=False) == 16

    with pytest.raises(TypeError):
        two_power_m1()

    with pytest.raises(TypeError):
        two_power_m1(3)

    with pytest.raises(TypeError):
        two_power_m1(3, False)

    with pytest.raises(TypeError):
        two_power_m1(3, minus_one=False)

    with pytest.raises(TypeError):
        two_power_m1(minus_one=False)


def test_property_fixed_params_all_args() -> None:

    seven_template = TaskTemplate(
        power_m1_func,
        fixed_params=dict(
            number=2,
            exponent=3,
        ),
    )

    for seven_obj in seven_template, seven_template.apply():
        assert seven_obj.fixed_params == {
            'number': 2,
            'exponent': 3,
        }

    seven = seven_template.apply()
    assert seven() == 7
    assert seven(minus_one=False) == 8

    with pytest.raises(TypeError):
        seven(False)

    with pytest.raises(TypeError):
        seven(number=3)

    with pytest.raises(TypeError):
        seven(3, 4)

    with pytest.raises(TypeError):
        seven(3, 4, False)

    with pytest.raises(TypeError):
        seven(number=3, exponent=4)

    with pytest.raises(TypeError):
        seven(number=3, exponent=4, minus_one=False)


def test_property_param_key_map_default() -> None:

    power_m1_template = TaskTemplate(power_m1_func)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.param_key_map == {}

    power_m1 = power_m1_template.apply()
    assert power_m1(number=4, exponent=3) == 63

    for val in ({}, [], None):
        power_m1_template = TaskTemplate(power_m1_func, param_key_map=val)
        for power_m1_obj in power_m1_template, power_m1_template.apply():
            assert power_m1_obj.param_key_map == {}


def test_property_param_key_map() -> None:

    power_m1_template = TaskTemplate(
        power_m1_func,
        param_key_map=dict(
            number='n',
            minus_one='m',
        ),
    )

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.param_key_map == {
            'number': 'n',
            'minus_one': 'm',
        }

    power_m1 = power_m1_template.apply()

    assert power_m1(4, 3) == 63
    assert power_m1(n=4, exponent=3) == 63
    assert power_m1(4, exponent=3) == 63
    assert power_m1(4, 3, m=False) == 64
    assert power_m1(4, 3, False) == 64

    with pytest.raises(TypeError):
        power_m1(5)

    with pytest.raises(TypeError):
        power_m1(number=5, exponent=3)

    with pytest.raises(TypeError):
        power_m1(n=5, number=5, exponent=3)

    with pytest.raises(TypeError):
        power_m1(n=5, exponent=3, minus_one=False)

    with pytest.raises(TypeError):
        power_m1(n=5, exponent=3, m=False, minus_one=False)

    with pytest.raises(TypeError):
        power_m1(5, 3, extra_attr=123)


def test_property_param_key_map_validation() -> None:

    power_m1_template = TaskTemplate(
        power_m1_func, param_key_map=[
            ('number', 'n'),
            ('exponent', 'e'),
        ])  # noqa

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.param_key_map == {
            'number': 'n',
            'exponent': 'e',
        }

    with pytest.raises(ValueError):
        TaskTemplate(power_m1_func, param_key_map={'number': 'same', 'exponent': 'same'})


def test_property_result_key_default() -> None:

    power_m1_template = TaskTemplate(power_m1_func)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key is None

    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == 15

    power_m1_template = TaskTemplate(power_m1_func, result_key=None)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key is None


def test_property_result_key() -> None:

    power_m1_template = TaskTemplate(power_m1_func, result_key='i_have_the_power')

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key == 'i_have_the_power'

    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == {'i_have_the_power': 15}


def test_error_properties_param_key_map_and_fixed_params_unmatched_params() -> None:

    power_m1_template = TaskTemplate(power_m1_func)

    assert 'engine' not in power_m1_template.param_signatures

    with pytest.raises(KeyError):
        TaskTemplate(power_m1_func, param_key_map=dict(engine='motor'))

    with pytest.raises(KeyError):
        power_m1_template.refine(param_key_map=dict(engine='horsepower'))

    with pytest.raises(KeyError):
        TaskTemplate(power_m1_func, fixed_params=dict(engine='hyperdrive'))

    with pytest.raises(KeyError):
        power_m1_template.refine(fixed_params=dict(engine='antigravity'))
