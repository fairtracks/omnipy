from typing import AsyncGenerator, Awaitable, cast, Generator

import pytest_cases as pc

from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.job import HasJobCreator, IsFuncArgJob
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.util.callable_types import CallableType
from omnipy.util.helpers import resolve

from ..helpers.classes import ComposedFlowCase
from ..helpers.functions import assert_job_state
from .raw.functions import async_range, async_wait_a_bit, sync_range
from .tasks import sync_double, sync_increment


@pc.case(
    id='linear-flow-sync-function-terminal-child',
    tags=['matrix', 'linear-flow', 'sync', 'function'],
)
def case_linear_flow_sync_function_terminal_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        task_template_cls = TaskTemplate
        parent_task_template = task_template_cls(name='linear_sync_function_parent')(sync_increment)
        terminal_task_template = task_template_cls(name='linear_sync_function_terminal')(sync_double)
        linear_flow_template = LinearFlowTemplate(
            parent_task_template,
            terminal_task_template,
            name='linear_flow_sync_function_terminal',
        )(sync_double)

        cast(HasJobCreator, task_template_cls).job_creator.set_engine(engine)
        if registry:
            engine.set_registry(registry)

        return linear_flow_template.apply()

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        assert job(3) == 8
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], int](
        name='linear-sync-function-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-sync-generator-terminal-child',
    tags=['matrix', 'linear-flow', 'sync', 'generator'],
)
def case_linear_flow_sync_generator_terminal_child() -> ComposedFlowCase[[int], Generator]:
    expected_callable_type = CallableType.SYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        task_template_cls = TaskTemplate
        parent_task_template = task_template_cls(name='linear_sync_generator_parent')(sync_increment)
        terminal_task_template = task_template_cls(name='linear_sync_generator_terminal')(sync_range)
        linear_flow_template = LinearFlowTemplate(
            parent_task_template,
            terminal_task_template,
            name='linear_flow_sync_generator_terminal',
        )(sync_range)

        cast(HasJobCreator, task_template_cls).job_creator.set_engine(engine)
        if registry:
            engine.set_registry(registry)

        return linear_flow_template.apply()

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(4)
        assert tuple(result) == (0, 1, 2, 3, 4)
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Generator](
        name='linear-sync-generator-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-async-coroutine-terminal-child',
    tags=['matrix', 'linear-flow', 'async', 'coroutine'],
)
def case_linear_flow_async_coroutine_terminal_child() -> ComposedFlowCase[[float], Awaitable[float]]:
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        task_template_cls = TaskTemplate
        parent_task_template = task_template_cls(name='linear_async_coroutine_parent')(sync_double)
        terminal_task_template = task_template_cls(name='linear_async_coroutine_terminal')(
            async_wait_a_bit)
        linear_flow_template = LinearFlowTemplate(
            parent_task_template,
            terminal_task_template,
            name='linear_flow_async_coroutine_terminal',
        )(async_wait_a_bit)

        cast(HasJobCreator, task_template_cls).job_creator.set_engine(engine)
        if registry:
            engine.set_registry(registry)

        return linear_flow_template.apply()

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(0.005))
        assert result == 0.01
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[float], Awaitable[float]](
        name='linear-async-coroutine-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-async-generator-terminal-child',
    tags=['matrix', 'linear-flow', 'async', 'generator'],
)
def case_linear_flow_async_generator_terminal_child() -> ComposedFlowCase[[int], AsyncGenerator]:
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        task_template_cls = TaskTemplate
        parent_task_template = task_template_cls(name='linear_async_generator_parent')(sync_increment)
        terminal_task_template = task_template_cls(name='linear_async_generator_terminal')(async_range)
        linear_flow_template = LinearFlowTemplate(
            parent_task_template,
            terminal_task_template,
            name='linear_flow_async_generator_terminal',
        )(async_range)

        cast(HasJobCreator, task_template_cls).job_creator.set_engine(engine)
        if registry:
            engine.set_registry(registry)

        return linear_flow_template.apply()

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(4)
        values = []
        async for value in result:
            values.append(value)
        assert values == [0, 1, 2, 3, 4]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-async-generator-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )
