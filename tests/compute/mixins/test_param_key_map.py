import pytest

from unifair.compute.task import TaskTemplate

from ..cases.raw.functions import power_m1_func


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
