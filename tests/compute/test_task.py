from inspect import Parameter
import json
from typing import Callable

import pytest

from unifair.compute.task import Task, TaskTemplate


@pytest.fixture
def action_func_no_params() -> Callable:
    def action_func_no_params() -> None:
        # backend.do_something()
        return

    return action_func_no_params


def test_init(format_to_string_func: Callable) -> None:
    task_template = TaskTemplate(format_to_string_func)
    assert isinstance(task_template, TaskTemplate)

    with pytest.raises(TypeError):
        TaskTemplate(format_to_string_func, 'extra_positional_argument')

    with pytest.raises(RuntimeError):
        Task(format_to_string_func)

    task = task_template.apply()
    assert isinstance(task, Task)


@pytest.fixture
def action_func_with_params() -> Callable:
    def action_func_with_params(command: str, *, verbose: bool = False) -> None:  # noqa
        # backend.run(command, verbose=verbose)
        return

    return action_func_with_params


@pytest.fixture
def data_import_func() -> Callable:
    def data_import_func() -> str:
        return '{"my_data": [123,234,345,456]}'

    return data_import_func


@pytest.fixture
def format_to_string_func() -> Callable:
    def format_to_string_func(text: str, number: int) -> str:
        return '{}: {}'.format(text, number)

    return format_to_string_func


def test_task_run_action_func_no_params(action_func_no_params: Callable) -> None:
    task_template = TaskTemplate(action_func_no_params)
    with pytest.raises(TypeError):
        task_template()  # noqa

    task = task_template.apply()
    assert task() is None


def test_task_run_action_func_with_params(action_func_with_params: Callable) -> None:
    task_template = TaskTemplate(action_func_with_params)
    with pytest.raises(TypeError):
        task_template('rm -rf *', verbose=True)  # noqa

    task = task_template.apply()
    assert task('rm -rf *', verbose=True) is None


def test_task_run_data_import_func(data_import_func: Callable) -> None:
    task_template = TaskTemplate(data_import_func)
    with pytest.raises(TypeError):
        task_template()  # noqa

    task = task_template.apply()
    json_data = task()
    assert type(json_data) is str
    assert json.loads(json_data) == dict(my_data=[123, 234, 345, 456])


def test_task_run_format_to_string_func(format_to_string_func: Callable) -> None:
    task_template = TaskTemplate(format_to_string_func)
    with pytest.raises(TypeError):
        task_template('Number', 12)  # noqa

    task = task_template.apply()
    assert task('Number', 12) == 'Number: 12'


@pytest.fixture
def power_m1_func() -> Callable:
    def power_m1_func(number: int, exponent: int, minus_one: bool = True) -> int:
        return number**exponent - (1 if minus_one else 0)

    return power_m1_func


def test_task_run_parameter_variants(power_m1_func: Callable) -> None:
    power_m1 = TaskTemplate(power_m1_func).apply()

    assert power_m1(4, 3) == 63
    assert power_m1(4, exponent=3) == 63
    assert power_m1(number=4, exponent=3) == 63
    assert power_m1(4, 3, False) == 64
    assert power_m1(4, 3, minus_one=False) == 64
    assert power_m1(4, exponent=3, minus_one=False) == 64
    assert power_m1(number=4, exponent=3, minus_one=False) == 64


def test_error_missing_task_run_parameters(power_m1_func: Callable) -> None:
    power_m1 = TaskTemplate(power_m1_func).apply()

    with pytest.raises(TypeError):
        power_m1()

    with pytest.raises(TypeError):
        power_m1(5)

    with pytest.raises(TypeError):
        power_m1(4, minus_one=False)


def test_property_param_signature_and_return_type_action_func_no_params(
        action_func_no_params: Callable) -> None:
    task_template = TaskTemplate(action_func_no_params)
    for task_obj in task_template, task_template.apply():
        assert task_obj.param_signatures == {}
        assert task_obj.return_type is None


def test_property_param_signature_and_return_type_data_import_func(
        data_import_func: Callable) -> None:
    task_template = TaskTemplate(data_import_func)
    for task_obj in task_template, task_template.apply():
        assert task_obj.param_signatures == {}
        assert task_obj.return_type is str


def test_property_param_signature_and_return_type_format_to_string_funcs(
        format_to_string_func: Callable) -> None:
    task_template = TaskTemplate(format_to_string_func)
    for task_obj in task_template, task_template.apply():
        assert task_obj.param_signatures == {
            'text': Parameter('text', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
            'number': Parameter('number', Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
        }
        assert task_obj.return_type is str


def test_property_param_signature_and_return_type_immutable(
        format_to_string_func: Callable) -> None:
    task_template = TaskTemplate(format_to_string_func)
    for task_obj in task_template, task_template.apply():
        with pytest.raises(AttributeError):
            task_obj.param_signatures = {}  # noqa

        with pytest.raises(TypeError):
            task_obj.param_signatures['new'] = Parameter(  # noqa
                'new', Parameter.POSITIONAL_OR_KEYWORD, annotation=bool)

        with pytest.raises(AttributeError):
            task_obj.return_type = int


def test_property_name_default(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func)
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.name == 'power_m1_func'

        with pytest.raises(AttributeError):
            power_m1_obj.name = 'cool_func'


def test_property_name_change(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func, name='power_m1')
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.name == 'power_m1'

        with pytest.raises(AttributeError):
            power_m1_obj.name = 'cool_func'


def test_property_name_validation(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func, name=None)
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.name == 'power_m1_func'

    with pytest.raises(ValueError):
        TaskTemplate(power_m1_func, name='')

    with pytest.raises(TypeError):
        TaskTemplate(power_m1_func, name=123)  # noqa


def test_property_fixed_params_default(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func)
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.fixed_params == {}

        with pytest.raises(AttributeError):
            power_m1_obj.fixed_params = {'number': 'num'}

        with pytest.raises(TypeError):
            power_m1_obj.fixed_params['number'] = 'num'  # noqa

    power_m1 = power_m1_template.apply()
    assert power_m1(number=4, exponent=3) == 63


def test_property_fixed_params_last_args(power_m1_func: Callable) -> None:
    square_template = TaskTemplate(power_m1_func, fixed_params=dict(exponent=2, minus_one=False))
    for square_obj in square_template, square_template.apply():
        assert square_obj.fixed_params == {'exponent': 2, 'minus_one': False}

        with pytest.raises(AttributeError):
            square_obj.fixed_params = {'number': 'num'}

        with pytest.raises(TypeError):
            square_obj.fixed_params['minus_one'] = True  # noqa

        with pytest.raises(TypeError):
            del square_obj.fixed_params['minus_one']  # noqa

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


def test_property_fixed_params_first_arg(power_m1_func: Callable) -> None:
    two_power_m1_template = TaskTemplate(power_m1_func, fixed_params=dict(number=2))  # noqa
    for two_power_m1_obj in two_power_m1_template, two_power_m1_template.apply():
        assert two_power_m1_obj.fixed_params == {'number': 2}

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


def test_property_fixed_params_all_args(power_m1_func: Callable) -> None:
    seven_template = TaskTemplate(power_m1_func, fixed_params=dict(number=2, exponent=3))  # noqa
    for seven_obj in seven_template, seven_template.apply():
        assert seven_obj.fixed_params == {'number': 2, 'exponent': 3}

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


def test_property_fixed_params_validation(power_m1_func: Callable) -> None:
    seven_template = TaskTemplate(
        power_m1_func, fixed_params=[('number', 4), ('exponent', 2)])  # noqa
    for seven_obj in seven_template, seven_template.apply():
        assert seven_obj.fixed_params == {'number': 4, 'exponent': 2}

    for val in ({}, [], None):
        power_m1_template = TaskTemplate(power_m1_func, fixed_params=val)  # noqa
        for power_m1_obj in power_m1_template, power_m1_template.apply():
            assert power_m1_obj.fixed_params == {}


def test_property_param_key_map_default(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func)
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.param_key_map == {}

        with pytest.raises(AttributeError):
            power_m1_obj.param_key_map = {'text': 'title'}

        with pytest.raises(TypeError):
            power_m1_obj.param_key_map['text'] = 'title'  # noqa

    power_m1 = power_m1_template.apply()

    assert power_m1(number=4, exponent=3) == 63


def test_property_param_key_map_change(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func, param_key_map=dict(number='n', minus_one='m'))
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.param_key_map == {'number': 'n', 'minus_one': 'm'}

        with pytest.raises(AttributeError):
            power_m1_obj.param_key_map = {}

        with pytest.raises(TypeError):
            power_m1_obj.param_key_map['number'] = 'n2'  # noqa

        with pytest.raises(TypeError):
            del power_m1_obj.param_key_map['minus_one']  # noqa

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
        power_m1(n=5, exponent=3, minus_one=False)


def test_property_param_key_map_validation(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(
        power_m1_func, param_key_map=[('number', 'n'), ('exponent', 'e')])  # noqa
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.param_key_map == {'number': 'n', 'exponent': 'e'}

    for val in ({}, [], None):
        power_m1_template = TaskTemplate(power_m1_func, param_key_map=val)
        for power_m1_obj in power_m1_template, power_m1_template.apply():
            assert power_m1_obj.param_key_map == {}

    with pytest.raises(ValueError):
        TaskTemplate(power_m1_func, param_key_map={'number': 'same', 'exponent': 'same'})


def test_property_result_key_default(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func)
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key is None

        with pytest.raises(AttributeError):
            power_m1_obj.result_key = 'i_have_the_power'

    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == 15


def test_property_result_key_change(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func, result_key='i_have_the_power')
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key == 'i_have_the_power'

        with pytest.raises(AttributeError):
            power_m1_obj.result_key = None

    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == {'i_have_the_power': 15}


def test_property_result_key_validation(power_m1_func: Callable) -> None:
    power_m1_template = TaskTemplate(power_m1_func, result_key=None)
    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key is None

    with pytest.raises(ValueError):
        TaskTemplate(power_m1_func, result_key='')

    with pytest.raises(TypeError):
        TaskTemplate(power_m1_func, result_key=123)  # noqa


def test_equal(format_to_string_func: Callable, power_m1_func: Callable) -> None:
    fts_tmpl = TaskTemplate(format_to_string_func)
    fts_tmpl_2 = TaskTemplate(format_to_string_func)
    for (fts_obj, fts_obj_2) in [(fts_tmpl, fts_tmpl_2), (fts_tmpl.apply(), fts_tmpl_2.apply())]:
        assert fts_obj == fts_obj_2

    pm1_tmpl = TaskTemplate(power_m1_func)
    for (fts_obj, pm1_obj) in [(fts_tmpl, pm1_tmpl), (fts_tmpl.apply(), pm1_tmpl.apply())]:
        assert fts_obj != pm1_obj

    pm1_tmpl_2 = TaskTemplate(power_m1_func, name='other')
    for (pm1_obj, pm1_obj_2) in [(pm1_tmpl, pm1_tmpl_2), (pm1_tmpl.apply(), pm1_tmpl_2.apply())]:
        assert pm1_obj != pm1_obj_2

    pm1_tmpl_3 = TaskTemplate(power_m1_func, fixed_params={'number': 2})
    for (pm1_obj, pm1_obj_3) in [(pm1_tmpl, pm1_tmpl_3), (pm1_tmpl.apply(), pm1_tmpl_3.apply())]:
        assert pm1_obj != pm1_obj_3

    pm1_tmpl_4 = TaskTemplate(power_m1_func, param_key_map={'number': 'num'})
    for (pm1_obj, pm1_obj_4) in [(pm1_tmpl, pm1_tmpl_4), (pm1_tmpl.apply(), pm1_tmpl_4.apply())]:
        assert pm1_obj != pm1_obj_4

    pm1_tmpl_5 = TaskTemplate(power_m1_func, result_key='result')
    for (pm1_obj, pm1_obj_5) in [(pm1_tmpl, pm1_tmpl_5), (pm1_tmpl.apply(), pm1_tmpl_5.apply())]:
        assert pm1_obj != pm1_obj_5


def test_refine_task_template_with_fixed_params(power_m1_func: Callable) -> None:
    # Plain task template
    power_m1_template = TaskTemplate(power_m1_func)
    power_m1 = power_m1_template.apply()
    assert power_m1(3, 2) == 8

    # Refine task template (update=True)
    square_template = power_m1_template.refine(fixed_params=dict(exponent=2, minus_one=False))
    assert square_template != power_m1_template
    for square_obj in square_template, square_template.apply():
        assert square_obj.fixed_params == dict(exponent=2, minus_one=False)
        assert square_obj.fixed_params.get('minus_one') is False

    square = square_template.apply()
    assert square != power_m1
    assert square(3) == 9

    # Refine task template with list of tuples format (update=True)
    cube_template = square_template.refine(fixed_params=[('exponent', 3)])  # noqa
    assert cube_template != square_template
    for cube_obj in cube_template, cube_template.apply():
        assert cube_obj.fixed_params == dict(exponent=3, minus_one=False)
        assert cube_obj.fixed_params.get('minus_one') is False

    cube = cube_template.apply()
    assert cube != square
    assert cube(3) == 27

    # Refine task template with update=False
    hypercube_template = cube_template.refine(fixed_params=dict(exponent=4), update=False)
    assert hypercube_template != cube_template
    for hypercube_obj in hypercube_template, hypercube_template.apply():
        assert hypercube_obj.fixed_params == dict(exponent=4)
        assert hypercube_obj.fixed_params.get('minus_one') is None

    hypercube = hypercube_template.apply()
    assert hypercube != cube
    assert hypercube(3) == 80

    # Resetting fixed_params does not work with update=True
    reset_power_m1_template = hypercube_template.refine(fixed_params={})
    assert reset_power_m1_template == hypercube_template
    assert reset_power_m1_template.fixed_params == dict(exponent=4)

    # Reset fixed_params with update=False
    for val in ({}, [], None):
        reset_power_m1_template = hypercube_template.refine(fixed_params=val, update=False)
        assert reset_power_m1_template == power_m1_template
        for reset_power_m1_obj in reset_power_m1_template, reset_power_m1_template.apply():
            assert reset_power_m1_obj.fixed_params == {}
            assert reset_power_m1_obj.fixed_params.get('minus_one') is None

    reset_power_m1 = reset_power_m1_template.apply()
    assert reset_power_m1 == power_m1
    assert reset_power_m1(3, 2) == 8


def test_refine_task_template_with_other_properties(power_m1_func: Callable) -> None:
    # Plain task template
    power_m1_template = TaskTemplate(power_m1_func)
    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == 15

    # Refine task template with all properties (update=True)
    my_power_template = power_m1_template.refine(
        name='magic_power',
        param_key_map=dict(number='num', exponent='exp'),
        result_key='by_the_power_of_grayskull',
    )
    assert my_power_template != power_m1_template
    for my_power_obj in my_power_template, my_power_template.apply():
        assert my_power_obj.name == 'magic_power'
        assert my_power_obj.param_key_map == dict(number='num', exponent='exp')
        assert my_power_obj.result_key == 'by_the_power_of_grayskull'

    my_power = my_power_template.apply()
    assert my_power != power_m1
    assert my_power(num=3, exp=3) == {'by_the_power_of_grayskull': 26}

    # Refine task template with single property (update=True)
    my_power_template_2 = my_power_template.refine(
        param_key_map=[('exponent', 'expo'), ('minus_one', 'min')],)  # noqa
    assert my_power_template_2 != my_power_template
    for my_power_obj_2 in my_power_template_2, my_power_template_2.apply():
        assert my_power_obj_2.name == 'magic_power'
        assert my_power_obj_2.param_key_map == dict(number='num', exponent='expo', minus_one='min')
        assert my_power_obj_2.result_key == 'by_the_power_of_grayskull'

    my_power_2 = my_power_template_2.apply()
    assert my_power_2 != my_power
    assert my_power_2(num=3, expo=3, min=False) == {'by_the_power_of_grayskull': 27}

    # Refine task template with single property (update=False)
    my_power_template_3 = my_power_template_2.refine(
        param_key_map=dict(exponent='expo', minus_one='min'), update=False)
    assert my_power_template_3 != my_power_template_2
    for my_power_obj_3 in my_power_template_3, my_power_template_3.apply():
        assert my_power_obj_3.name == 'power_m1_func'
        assert my_power_obj_3.param_key_map == dict(exponent='expo', minus_one='min')
        assert my_power_obj_3.result_key is None

    my_power_3 = my_power_template_3.apply()
    assert my_power_3 != my_power_2
    assert my_power_3(number=3, expo=3, min=False) == 27

    # Resetting param_key_map does not work with update=True
    my_power_template_4 = my_power_template_3.refine(param_key_map={})
    assert my_power_template_4 == my_power_template_3
    for my_power_obj_4 in my_power_template_4, my_power_template_4.apply():
        assert my_power_obj_4.param_key_map == dict(exponent='expo', minus_one='min')

    # Reset param_key_map with update=False
    for val in ({}, [], None):
        my_power_template_4 = my_power_template_3.refine(param_key_map=val, update=False)
        assert my_power_template_4 == power_m1_template
        for my_power_obj_4 in my_power_template_4, my_power_template_4.apply():
            assert my_power_obj_4.param_key_map == {}

    my_power_4 = my_power_template_4.apply()
    assert my_power_4 == power_m1
    assert my_power_4(number=3, exponent=3, minus_one=False) == 27


def test_revise_refine_task_template_with_fixed_params_and_other_properties(
        power_m1_func: Callable) -> None:
    # New task template with fixed params and other properties set
    square_template = TaskTemplate(power_m1_func).refine(
        name='square',
        param_key_map=dict(number='num', exponent='exp'),
        fixed_params=dict(exponent=2, minus_one=False),
    )
    for square_obj in square_template, square_template.apply():
        assert square_obj.name == 'square'
        assert square_obj.param_key_map == dict(number='num', exponent='exp')
        assert square_obj.result_key is None
        assert square_obj.fixed_params == {'exponent': 2, 'minus_one': False}

    square = square_template.apply()
    assert square(num=3) == 9

    # Revise task into task_template
    square_revised_template = square.revise()
    assert isinstance(square_revised_template, TaskTemplate)
    assert square_revised_template == square_template

    for square_revised_obj in square_revised_template, square_revised_template.apply():
        assert square_revised_obj.name == 'square'
        assert square_revised_obj.param_key_map == dict(number='num', exponent='exp')
        assert square_revised_obj.result_key is None
        assert square_revised_obj.fixed_params == {'exponent': 2, 'minus_one': False}

    # Refine revised task_template with update=False to reset param_key_map
    square_refined = square_revised_template.refine(
        name=square_revised_template.name,
        fixed_params=square_revised_template.fixed_params,
        update=False).apply()

    assert square_refined.name == 'square'
    assert square_refined.param_key_map == {}
    assert square_refined.result_key is None
    assert square_refined.fixed_params == {'exponent': 2, 'minus_one': False}

    assert square_refined(number=3) == 9

    # One-liner to reset task to original template
    power_reset = square_refined.revise().refine(update=False).apply()
    assert power_reset == TaskTemplate(power_m1_func).apply()
    assert power_reset.name == 'power_m1_func'
    assert power_reset.param_key_map == {}
    assert power_reset.result_key is None
    assert power_reset.fixed_params == {}


def test_revise_refine_dicts_are_copied(power_m1_func: Callable) -> None:
    square_template = TaskTemplate(
        power_m1_func,
        name='square',
        param_key_map=dict(number='num'),
        fixed_params=dict(exponent=2),
    )

    square_refined_template = square_template.refine(
        param_key_map=dict(exponent='exp'),
        fixed_params=dict(minus_one=False),
    )

    assert len(square_template.param_key_map) == 1
    assert len(square_template.fixed_params) == 1
    assert len(square_refined_template.param_key_map) == 2
    assert len(square_refined_template.fixed_params) == 2

    square = square_template.apply()
    square_revised_template = square.revise()
    square_revised_refined_template = square_revised_template.refine(
        param_key_map=dict(exponent='exp'),
        fixed_params=dict(minus_one=False),
    )

    assert len(square_template.param_key_map) == 1
    assert len(square_template.fixed_params) == 1
    assert len(square.param_key_map) == 1
    assert len(square.fixed_params) == 1
    assert id(square.param_key_map) != id(square_template.param_key_map)
    assert id(square.fixed_params) != id(square_template.fixed_params)

    assert len(square_revised_template.param_key_map) == 1
    assert len(square_revised_template.fixed_params) == 1
    assert id(square_revised_template.param_key_map) != id(square.param_key_map)
    assert id(square_revised_template.fixed_params) != id(square.fixed_params)

    assert len(square_revised_refined_template.param_key_map) == 2
    assert len(square_revised_refined_template.fixed_params) == 2


def test_error_properties_param_key_map_and_fixed_params_unmatched_params(
        power_m1_func: Callable) -> None:
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


#
# def test_task_template_as_decorator():
#     @TaskTemplate
#     def plus_one(number: int) -> int:
#         return number + 1
#
#     assert isinstance(plus_one, TaskTemplate)
#
#     plus_one = plus_one.apply()
#     assert isinstance(plus_one, Task)
#
#     assert plus_one(3) == 4
#
#
# def test_error_task_template_decorator_with_arguments(
#         mock_task_runner_engine_cls: Callable) -> None:
#
#     with pytest.raises(TypeError):
#
#         @TaskTemplate('something')
#         def plus_one(number: int) -> int:
#             return number + 1
#
#
# def test_unifair_task_template_decorator_with_keyword_arguments():
#     @unifair_task_template(
#         name='plus_one',
#         param_key_map=dict(number_a='number'),
#         fixed_params=dict(number_b=1),
#         result_key='plus_one',
#     )
#     def plus_func(number_a: int, number_b: int) -> int:
#         return number_a + number_b
#
#     assert isinstance(plus_func, TaskTemplate)
#
#     plus_one = plus_one.apply()
#     assert isinstance(plus_one, Task)
#
#     assert plus_one(3) == 4
#
#
# @pytest.fixture
# def power_func() -> Callable:
#     def _power_func(number: int, exponent: int) -> int:
#         return number**exponent
#
#     return _power_func
#
#
# @pytest.fixture
# def power(power_func):
#
#     return my_engine.task_decorator()(power_func)
