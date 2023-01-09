import pytest

from unifair.compute.task import TaskTemplate

from ..cases.raw.functions import power_m1_func


def test_property_fixed_params_default_task() -> None:

    power_m1_template = TaskTemplate(power_m1_func)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.fixed_params == {}

    power_m1 = power_m1_template.apply()
    assert power_m1(number=4, exponent=3) == 63

    for val in ({}, [], None):
        power_m1_template = TaskTemplate(power_m1_func, fixed_params=val)  # noqa
        for power_m1_obj in power_m1_template, power_m1_template.apply():
            assert power_m1_obj.fixed_params == {}


def test_property_fixed_params_last_args_task() -> None:

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


def test_property_fixed_params_first_arg_task() -> None:

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


def test_property_fixed_params_all_args_task() -> None:

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


def test_property_param_key_map_default_task() -> None:

    power_m1_template = TaskTemplate(power_m1_func)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.param_key_map == {}

    power_m1 = power_m1_template.apply()
    assert power_m1(number=4, exponent=3) == 63

    for val in ({}, [], None):
        power_m1_template = TaskTemplate(power_m1_func, param_key_map=val)
        for power_m1_obj in power_m1_template, power_m1_template.apply():
            assert power_m1_obj.param_key_map == {}


def test_property_param_key_map_task() -> None:

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


def test_property_param_key_map_validation_task() -> None:

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


def test_error_properties_param_key_map_and_fixed_params_unmatched_params_task() -> None:

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
