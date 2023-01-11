from enum import Enum

from omnipy.compute.task import TaskTemplate

from ..cases.raw.functions import power_m1_func


class SerializeOutputsOptions(Enum):
    GLOBAL = 0
    OFF = 1
    WRITE = 2


class ResumePreviousRunOptions(Enum):
    GLOBAL = 0
    OFF = 1
    AUTO_READ_IGNORE_PARAMS = 2
    FORCE_READ_IGNORE_PARAMS = 3


def test_property_serialize_default_task() -> None:

    power_m1_template = TaskTemplate(power_m1_func)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key is None

    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == 15

    power_m1_template = TaskTemplate(power_m1_func, result_key=None)

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key is None


def test_property_result_key_task() -> None:

    power_m1_template = TaskTemplate(power_m1_func, result_key='i_have_the_power')

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key == 'i_have_the_power'

    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == {'i_have_the_power': 15}
