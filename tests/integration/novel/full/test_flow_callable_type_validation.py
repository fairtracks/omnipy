from inspect import Parameter
from typing import Annotated

import pytest

import omnipy as om
from omnipy.util.callable_types import CallableType
from omnipy.util.helpers import resolve


async def test_flow_callable_type_validation(
        runtime_all_engines: Annotated[None, pytest.fixture],  # noqa
) -> None:
    @om.TaskTemplate()
    def seed_linear_value(seed: int) -> int:
        return seed + 1

    @om.TaskTemplate()
    async def finish_linear_value(number: int) -> int:
        return number * 10

    @om.TaskTemplate()
    def branch_left(seed: int) -> dict[str, int]:
        return {'branch_left': seed + 4}

    @om.TaskTemplate()
    async def branch_right(branch_left: int) -> int:
        return branch_left * 3

    @om.TaskTemplate()
    async def branch_right_revised(branch_left: int) -> int:
        return branch_left * 5

    @om.LinearFlowTemplate(seed_linear_value, finish_linear_value)
    async def linear_async_submission_flow(seed: int) -> int:
        ...

    @om.DagFlowTemplate(branch_left, branch_right)
    async def dag_async_submission_flow(seed: int) -> int:
        ...

    assert linear_async_submission_flow.param_signatures == {
        'seed': Parameter('seed', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
    }
    assert linear_async_submission_flow.return_type == int
    assert linear_async_submission_flow.callable_type is CallableType.ASYNC_COROUTINE
    assert linear_async_submission_flow.apply().callable_type is CallableType.ASYNC_COROUTINE
    assert await resolve(linear_async_submission_flow.run(2)) == 30
    assert await resolve(linear_async_submission_flow.apply()(2)) == 30

    linear_refined = linear_async_submission_flow.refine(
        name='linear_async_submission_flow_refined')
    assert linear_refined.callable_type is CallableType.ASYNC_COROUTINE
    assert linear_refined.apply().callable_type is CallableType.ASYNC_COROUTINE
    assert await resolve(linear_refined.run(3)) == 40

    assert dag_async_submission_flow.param_signatures == {
        'seed': Parameter('seed', Parameter.POSITIONAL_OR_KEYWORD, annotation=int),
    }
    assert dag_async_submission_flow.return_type == int
    assert dag_async_submission_flow.callable_type is CallableType.ASYNC_COROUTINE
    assert dag_async_submission_flow.apply().callable_type is CallableType.ASYNC_COROUTINE
    assert await resolve(dag_async_submission_flow.run(2)) == 18
    assert await resolve(dag_async_submission_flow.apply()(2)) == 18

    dag_job = dag_async_submission_flow.apply()
    revised_children = list(dag_job.child_job_templates)
    revised_children[1] = branch_right_revised
    revised_dag = dag_job.revise().refine(*revised_children, update=False)

    assert revised_dag.callable_type is CallableType.ASYNC_COROUTINE
    assert revised_dag.apply().callable_type is CallableType.ASYNC_COROUTINE
    assert await resolve(revised_dag.run(2)) == 30
    assert await resolve(revised_dag.apply()(2)) == 30
