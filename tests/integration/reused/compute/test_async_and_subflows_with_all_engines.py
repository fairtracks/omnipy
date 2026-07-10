import asyncio
from typing import Annotated, cast

import pytest

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.protocols.compute.job import IsDagFlow
from omnipy.util.helpers import resolve


def test_nested_async_child_flow_all_engines(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
) -> None:
    @TaskTemplate()
    def add_one(number: int) -> int:
        return number + 1

    @TaskTemplate()
    async def wait_and_double(number: int) -> int:
        await asyncio.sleep(0)
        return number * 2

    @TaskTemplate()
    async def wait_and_add_ten(number: int) -> int:
        await asyncio.sleep(0)
        return number + 10

    @LinearFlowTemplate(add_one, wait_and_double)
    async def async_linear_child(number: int) -> int:
        ...

    @FuncFlowTemplate()
    async def async_func_child(number: int) -> int:
        nested_result = await resolve(async_linear_child(number))
        return await wait_and_add_ten(nested_result)

    @FuncFlowTemplate()
    async def async_parent_flow(number: int) -> int:
        return await async_func_child(number)

    async_parent_job = async_parent_flow.apply()

    assert asyncio.run(resolve(async_parent_job(4))) == 20


def test_parent_child_parameter_routing_all_engines(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
) -> None:
    @TaskTemplate()
    def compute_parent_value(seed: int) -> int:
        return seed + 5

    @TaskTemplate()
    def compute_parent_multiplier(seed: int) -> int:
        return seed * 2

    @TaskTemplate()
    def scale_child_value(value: int, multiplier: int) -> int:
        return value * multiplier

    @TaskTemplate()
    def compute_child_checksum(value: int, scaled_value: int) -> int:
        return value + scaled_value

    @TaskTemplate()
    def finalize_parent_result(parent_value: int, child_checksum: int) -> int:
        return child_checksum - parent_value

    @DagFlowTemplate(
        scale_child_value.refine(
            param_key_map={
                'value': 'child_value',
                'multiplier': 'child_multiplier',
            },
            result_key='scaled_value',
        ),
        compute_child_checksum.refine(param_key_map={'value': 'child_value'}),
    )
    def routed_child_flow(child_value: int, child_multiplier: int) -> int:
        ...

    @DagFlowTemplate(
        compute_parent_value.refine(result_key='parent_value'),
        compute_parent_multiplier.refine(result_key='parent_multiplier'),
        routed_child_flow.refine(
            param_key_map={
                'child_value': 'parent_value',
                'child_multiplier': 'parent_multiplier',
            },
            result_key='child_checksum',
        ),
        finalize_parent_result,
    )
    def routed_parent_flow(seed: int) -> int:
        ...

    routed_parent_job = routed_parent_flow.apply()

    assert routed_parent_job(3) == 48


def test_child_flow_replacement_via_refine_revise_all_engines(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
) -> None:
    @TaskTemplate()
    def compute_left_value(number: int) -> int:
        return number + 1

    @TaskTemplate()
    def compute_right_value(number: int) -> int:
        return number * 2

    @TaskTemplate()
    def combine_child_values(left_value: int, right_value: int) -> int:
        return left_value + right_value

    @TaskTemplate()
    def multiply_combined_value(combined_value: int) -> int:
        return combined_value * 2

    @TaskTemplate()
    def subtract_from_combined_value(combined_value: int) -> int:
        return combined_value - 3

    @TaskTemplate()
    def return_child_result(child_result: int) -> int:
        return child_result

    @LinearFlowTemplate(combine_child_values, multiply_combined_value)
    def initial_linear_child(left_value: int, right_value: int) -> int:
        ...

    @LinearFlowTemplate(combine_child_values, subtract_from_combined_value)
    def replacement_linear_child(left_value: int, right_value: int) -> int:
        ...

    @DagFlowTemplate(
        compute_left_value.refine(result_key='left_value'),
        compute_right_value.refine(result_key='right_value'),
        initial_linear_child.refine(result_key='child_result'),
        return_child_result,
    )
    def dag_parent_with_replaceable_child(number: int) -> int:
        ...

    initial_job = dag_parent_with_replaceable_child.apply()
    initial_result = initial_job(4)

    dag_job = cast(IsDagFlow, initial_job)
    revised_child_templates = list(dag_job.child_job_templates)
    revised_child_templates[2] = replacement_linear_child.refine(result_key='child_result')
    revised_job = dag_job.revise().refine(*revised_child_templates).apply()

    revised_result = revised_job(4)

    assert initial_result == 26
    assert revised_result == 10
    assert revised_result != initial_result
