from typing import Annotated

from pydantic.fields import Undefined
import pytest

from omnipy.api.protocols.public.compute import IsDagFlowTemplate, IsTaskTemplate
from omnipy.compute.flow import FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.compute.typing import (mypy_fix_func_flow_template,
                                   mypy_fix_linear_flow_template,
                                   mypy_fix_task_template)
from omnipy.data.model import Model

from ..cases.raw.functions import power_m1_func
from ..helpers.mocks import MockLocalRunner


def test_property_result_key_default_task() -> None:

    power_m1_template = mypy_fix_task_template(TaskTemplate()(power_m1_func))

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key is Undefined
        assert not power_m1_obj.has_result_key

    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == 15
    assert not power_m1.has_result_key

    power_m1_template = mypy_fix_task_template(TaskTemplate(result_key=None)(power_m1_func))

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key is None
        assert not power_m1_obj.has_result_key


def test_property_result_key_task() -> None:

    power_m1_template = mypy_fix_task_template(
        TaskTemplate(result_key='i_have_the_power')(power_m1_func))

    for power_m1_obj in power_m1_template, power_m1_template.apply():
        assert power_m1_obj.result_key == 'i_have_the_power'
        assert power_m1_obj.has_result_key

    power_m1 = power_m1_template.apply()
    assert power_m1(4, 2) == {'i_have_the_power': 15}


def test_dag_flow_result_selector_key(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:

    assert my_double_power_m1_dag_flow.dag_flow_result_selector_key == None
    assert my_double_power_m1_dag_flow.run(4, 2) == 15

    my_dpm1_dag_flow_first_task_fixed_last_task_with_other_result_key = my_double_power_m1_dag_flow.refine(
        my_double_power_m1_dag_flow.task_templates[0].refine(result_key='number'),
        my_double_power_m1_dag_flow.task_templates[1].refine(result_key='other'),
    )

    assert my_dpm1_dag_flow_first_task_fixed_last_task_with_other_result_key.run(4, 2) == {
        'other': 244
    }

    my_dpm1_dag_flow_fixed_selector_key_not_matching_last_task_result_key = \
        my_dpm1_dag_flow_first_task_fixed_last_task_with_other_result_key.refine(
            dag_flow_result_selector_key='number',
        )

    with pytest.raises(ValueError):
        my_dpm1_dag_flow_fixed_selector_key_not_matching_last_task_result_key.run(4, 2)

    my_dpm1_dag_flow_fixed_selector_key_matching_last_task_result_key = \
        my_dpm1_dag_flow_fixed_selector_key_not_matching_last_task_result_key.refine(
            dag_flow_result_selector_key='other',
        )

    assert my_dpm1_dag_flow_fixed_selector_key_matching_last_task_result_key.run(4, 2) == 224


def test_error_dag_flow_result_selector_incorrect_key(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:
    my_dpm1_dag_flow_incorrect_selector_key = my_double_power_m1_dag_flow.refine(
        my_double_power_m1_dag_flow.task_templates[0].refine(result_key='number'),
        my_double_power_m1_dag_flow.task_templates[1].refine(result_key='other'),
        dag_flow_result_selector_key='number')

    with pytest.raises(ValueError):
        my_dpm1_dag_flow_incorrect_selector_key.run(4, 2)


def test_dag_flow_result_selector_key_is_none(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:
    my_dpm1_dag_flow_no_selector_key = my_double_power_m1_dag_flow.refine(
        dag_flow_result_selector_key=None,)

    assert my_dpm1_dag_flow_no_selector_key.run(4, 2) == {'dataset': 15}

    my_dpm1_dag_flow_fix_first_task_result_no_selector_key = my_dpm1_dag_flow_no_selector_key.refine(
        my_dpm1_dag_flow_no_selector_key.task_templates[0].refine(result_key='number'),
        my_double_power_m1_dag_flow.task_templates[1],
    )

    assert my_dpm1_dag_flow_fix_first_task_result_no_selector_key.run(4, 2) == {
        'number': 15, 'dataset': 224
    }

    my_dpm1_dag_flow_fixed_no_result_or_selector_keys = my_dpm1_dag_flow_fix_first_task_result_no_selector_key.refine(
        my_dpm1_dag_flow_fix_first_task_result_no_selector_key.task_templates[0],
        my_dpm1_dag_flow_fix_first_task_result_no_selector_key.task_templates[1].refine(
            result_key=None),
    )

    assert my_dpm1_dag_flow_fixed_no_result_or_selector_keys.run(4, 2) == {
        'number': 15, 'power_m1_func': 224
    }

    my_dpm1_dag_flow_unfixed_no_result_or_selector_keys = my_dpm1_dag_flow_fixed_no_result_or_selector_keys.refine(
        my_dpm1_dag_flow_fixed_no_result_or_selector_keys.task_templates[0].refine(result_key=None),
        my_dpm1_dag_flow_fixed_no_result_or_selector_keys.task_templates[1],
    )

    assert my_dpm1_dag_flow_unfixed_no_result_or_selector_keys.run(4, 2) == {'power_m1_func': 15}


def test_dag_flow_result_selector_key_empty_dag_flow(
        my_empty_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:

    assert my_empty_dag_flow.run(4) is None

    my_empty_dag_flow_with_selector_key = my_empty_dag_flow.refine(
        dag_flow_result_selector_key='number')

    assert my_empty_dag_flow_with_selector_key.run(4) is None

    my_empty_dag_flow_with_selector_key = my_empty_dag_flow.refine(
        dag_flow_result_selector_key=None)

    assert my_empty_dag_flow_with_selector_key.run(4) == {}


def test_error_dag_flow_result_selector_key_no_mapping_result(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:
    my_dpm1_dag_flow_no_mapping_result = my_double_power_m1_dag_flow.refine(
        *(task_template.refine(result_key=None)
          for task_template in my_double_power_m1_dag_flow.task_templates),)

    with pytest.raises(ValueError):
        my_dpm1_dag_flow_no_mapping_result.run(4, 2)

    my_dpm1_dag_flow_no_mapping_result_and_no_selector_key = \
        my_dpm1_dag_flow_no_mapping_result.refine(
            dag_flow_result_selector_key='power_m1_func',
        )

    assert my_dpm1_dag_flow_no_mapping_result_and_no_selector_key.run(4, 2) == 15


def test_error_default_result_key_for_dag_jobs_no_matching_selector_key(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:

    my_dpm1_dag_flow_incorrect_selector_key = my_double_power_m1_dag_flow.refine(
        default_result_key_for_dag_jobs='number')

    with pytest.raises(ValueError):
        assert my_dpm1_dag_flow_incorrect_selector_key.run(4, 2) == 224


def test_default_result_key_for_dag_jobs(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:

    assert my_double_power_m1_dag_flow.run(4, 2) == 15

    my_dpm1_dag_flow_fixed = my_double_power_m1_dag_flow.refine(
        default_result_key_for_dag_jobs='number',
        dag_flow_result_selector_key='number',
    )

    assert my_dpm1_dag_flow_fixed.run(4, 2) == 224


def test_default_result_key_for_dag_jobs_empty_dag_flow(
        my_empty_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:

    assert my_empty_dag_flow.run(4) is None

    my_empty_dag_flow_with_default_result_key = my_empty_dag_flow.refine(
        default_result_key_for_dag_jobs='number')

    assert my_empty_dag_flow_with_default_result_key.run(4) is None


def test_error_default_result_key_for_dag_jobs_is_none_no_matching_selector_key(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:

    my_dpm1_dag_flow_default_result_key_is_none = my_double_power_m1_dag_flow.refine(
        default_result_key_for_dag_jobs=None)

    with pytest.raises(ValueError):
        my_dpm1_dag_flow_default_result_key_is_none.run(4, 2)


def test_default_result_key_for_dag_jobs_is_none(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:

    my_dpm1_dag_flow_selector_and_default_result_keys_are_none = my_double_power_m1_dag_flow.refine(
        default_result_key_for_dag_jobs=None,
        dag_flow_result_selector_key=None,
    )

    assert my_dpm1_dag_flow_selector_and_default_result_keys_are_none.run(4, 2) == {
        'power_m1_func': 15
    }


def test_default_result_key_for_dag_jobs_overrides(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]) -> None:
    my_dpm1_dag_flow_first_task_no_result_key = my_double_power_m1_dag_flow.refine(
        my_double_power_m1_dag_flow.task_templates[0].refine(result_key=None),
        my_double_power_m1_dag_flow.task_templates[1],
        dag_flow_result_selector_key=None,
    )

    assert my_dpm1_dag_flow_first_task_no_result_key.run(4, 2) == {
        'power_m1_func': 15, 'dataset': 15
    }

    my_dpm1_dag_flow_first_task_fixed = my_dpm1_dag_flow_first_task_no_result_key.refine(
        my_dpm1_dag_flow_first_task_no_result_key.task_templates[0].refine(result_key='number'),
        my_dpm1_dag_flow_first_task_no_result_key.task_templates[1],
    )

    assert my_dpm1_dag_flow_first_task_fixed.run(4, 2) == {'number': 15, 'dataset': 224}

    my_dpm1_dag_flow_first_fixed_second_none = my_dpm1_dag_flow_first_task_fixed.refine(
        my_dpm1_dag_flow_first_task_fixed.task_templates[0],
        my_dpm1_dag_flow_first_task_fixed.task_templates[1].refine(result_key=None),
    )

    assert my_dpm1_dag_flow_first_fixed_second_none.run(4, 2) == {
        'number': 15, 'power_m1_func': 224
    }

    my_dpm1_dag_flow_first_fixed_second_none_default_reskey_other = \
        my_dpm1_dag_flow_first_fixed_second_none.refine(
            default_result_key_for_dag_jobs='other',
        )

    assert my_dpm1_dag_flow_first_fixed_second_none_default_reskey_other.run(4, 2) == {
        'number': 15, 'power_m1_func': 224
    }

    my_dpm1_dag_flow_first_fixed_default_reskey_other = \
        my_dpm1_dag_flow_first_fixed_second_none_default_reskey_other.refine(
            my_dpm1_dag_flow_first_fixed_second_none_default_reskey_other.task_templates[0],
            my_dpm1_dag_flow_first_fixed_second_none_default_reskey_other.task_templates[1].refine(
                update=False,
            )
        )

    assert my_dpm1_dag_flow_first_fixed_default_reskey_other.run(4, 2) == {
        'number': 15, 'other': 224
    }


def test_default_result_key_for_dag_jobs_ignored_for_other_job_types(
        mock_local_runner: Annotated[MockLocalRunner, pytest.fixture]):
    my_power_m1_task_template = mypy_fix_task_template(
        TaskTemplate(default_result_key_for_dag_jobs='blabla')(power_m1_func))
    assert my_power_m1_task_template.run(4, 2) == 15

    fixed_power_of_two_m1_task_template = my_power_m1_task_template.refine(
        fixed_params=dict(exponent=2))

    @mypy_fix_linear_flow_template
    @LinearFlowTemplate(
        fixed_power_of_two_m1_task_template,
        fixed_power_of_two_m1_task_template,
        default_result_key_for_dag_jobs='blabla')
    def my_double_power_of_two_m1_linear_flow(number: int | Model[int]):
        ...

    assert my_double_power_of_two_m1_linear_flow.run(4) == 224

    @mypy_fix_func_flow_template
    @FuncFlowTemplate(default_result_key_for_dag_jobs='blabla')
    def my_double_power_m1_func_flow(number: int | Model[int], exponent: int):
        first_result = my_power_m1_task_template(number, exponent)
        return my_power_m1_task_template(first_result, exponent)

    assert my_double_power_m1_func_flow.run(4, 2) == 224


def test_selector_key_and_default_result_key_with_dag_flow_result_key(
        my_double_power_m1_dag_flow: Annotated[IsDagFlowTemplate, pytest.fixture]):
    my_dpm1_dag_flow_with_result_key = my_double_power_m1_dag_flow.refine(result_key='output')

    assert my_dpm1_dag_flow_with_result_key.run(4, 2) == {'output': 15}

    my_dpm1_dag_flow_with_result_key_and_no_selector_key = \
        my_dpm1_dag_flow_with_result_key.refine(dag_flow_result_selector_key=None)

    assert my_dpm1_dag_flow_with_result_key_and_no_selector_key.run(4, 2) == {
        'output': {
            'dataset': 15
        }
    }

    my_dpm1_dag_flow_with_result_key_and_no_default_result_and_selector_keys = \
        my_dpm1_dag_flow_with_result_key_and_no_selector_key.refine(
            default_result_key_for_dag_jobs=None,
        )

    assert my_dpm1_dag_flow_with_result_key_and_no_default_result_and_selector_keys.run(4, 2) == {
        'output': {
            'power_m1_func': 15
        }
    }
