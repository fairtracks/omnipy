from inspect import Parameter

import pytest
import pytest_cases as pc

from unifair.compute.task import Task, TaskTemplate

from .cases.raw.functions import format_to_string_func, power_m1_func
from .cases.tasks import TaskCase


def test_init() -> None:
    task_template = TaskTemplate(format_to_string_func)
    assert isinstance(task_template, TaskTemplate)

    with pytest.raises(TypeError):
        TaskTemplate(format_to_string_func, 'extra_positional_argument')

    with pytest.raises(RuntimeError):
        Task(format_to_string_func)

    task = task_template.apply()
    assert isinstance(task, Task)


@pc.parametrize_with_cases('case', cases='.cases.tasks')
def test_task_run(mock_local_runner, case: TaskCase) -> None:

    assert mock_local_runner.finished is False
    task_template = TaskTemplate(case.func)

    with pytest.raises(TypeError):
        task_template(*case.args, **case.kwargs)  # noqa

    task = task_template.apply()
    result = task(*case.args, **case.kwargs)

    assert task.name == case.name
    assert mock_local_runner.finished is True
    case.assert_func(result)


def test_task_run_parameter_variants(mock_local_runner) -> None:

    assert mock_local_runner.finished is False
    power_m1 = TaskTemplate(power_m1_func).apply()

    assert power_m1(4, 3) == 63
    assert power_m1(4, exponent=3) == 63
    assert power_m1(number=4, exponent=3) == 63
    assert power_m1(4, 3, False) == 64
    assert power_m1(4, 3, minus_one=False) == 64
    assert power_m1(4, exponent=3, minus_one=False) == 64
    assert power_m1(number=4, exponent=3, minus_one=False) == 64

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

    task_template = TaskTemplate(case.func)

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


def test_property_name_default() -> None:

    power_m1_template = TaskTemplate(power_m1_func)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.name == 'power_m1_func'


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


def test_refine_task_template_with_other_properties() -> None:

    # Plain task template
    power_m1_template = TaskTemplate(power_m1_func)
    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == 15

    # Refine task template with all properties (update=True)
    my_power_template = power_m1_template.refine(
        name='magic_power',
        param_key_map=dict(number='num', exponent='exp'),
        result_key='by_the_power_of_grayskull',
        fixed_params=dict(exponent=3),
    )
    assert my_power_template != power_m1_template
    for my_power_obj in my_power_template, my_power_template.apply():
        assert my_power_obj.name == 'magic_power'
        assert my_power_obj.param_key_map == dict(number='num', exponent='exp')
        assert my_power_obj.result_key == 'by_the_power_of_grayskull'
        assert my_power_obj.fixed_params == {'exponent': 3}

    my_power = my_power_template.apply()
    assert my_power != power_m1
    assert my_power(num=3) == {'by_the_power_of_grayskull': 26}

    # Refine task template with two properties (update=True)
    my_power_template_2 = my_power_template.refine(
        param_key_map=[('number', 'numb'), ('minus_one', 'min')],)  # noqa
    assert my_power_template_2 != my_power_template
    for my_power_obj_2 in my_power_template_2, my_power_template_2.apply():
        assert my_power_obj_2.name == 'magic_power'
        assert my_power_obj_2.param_key_map == dict(number='numb', exponent='exp', minus_one='min')
        assert my_power_obj_2.result_key == 'by_the_power_of_grayskull'
        assert my_power_obj_2.fixed_params == {'exponent': 3}

    my_power_2 = my_power_template_2.apply()
    assert my_power_2 != my_power
    assert my_power_2(numb=3, min=False) == {'by_the_power_of_grayskull': 27}

    # Refine task template with single property (update=False)
    my_power_template_3 = my_power_template_2.refine(
        fixed_params=dict(number=3, minus_one=False), update=False)
    assert my_power_template_3 != my_power_template_2
    for my_power_obj_3 in my_power_template_3, my_power_template_3.apply():
        assert my_power_obj_3.name == 'power_m1_func'
        assert my_power_obj_3.param_key_map == {}
        assert my_power_obj_3.result_key is None
        assert my_power_obj_3.fixed_params == dict(number=3, minus_one=False)

    my_power_3 = my_power_template_3.apply()
    assert my_power_3 != my_power_2
    assert my_power_3(exponent=3) == 27

    # One-liner to reset properties to default values
    my_power_4 = my_power_3.revise().refine(update=False).apply()
    assert my_power_4 == power_m1
    assert my_power_4(number=3, exponent=3, minus_one=False) == 27


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
