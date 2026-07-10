import asyncio
from typing import AsyncGenerator, Awaitable, Generator

import pytest_cases as pc

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.job import IsFuncArgJob
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.util.callable_types import CallableType
from omnipy.util.helpers import resolve

from ..helpers.classes import ComposedFlowCase
from ..helpers.functions import apply_job, assert_job_state


@pc.case(
    id='linear-flow-sync-function-terminal-child',
    tags=['matrix', 'linear-flow', 'sync', 'function'],
)
def case_linear_flow_sync_function_terminal_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def add_two(number: int) -> int:
            return number + 2

        @TaskTemplate()
        def square_number(number: int) -> int:
            return number * number

        @TaskTemplate()
        def subtract_one(number: int) -> int:
            return number - 1

        # Linear Flow
        @LinearFlowTemplate(add_two, square_number, subtract_one)
        def linear_flow_sync_function_terminal(number: int) -> int:
            ...

        return apply_job(linear_flow_sync_function_terminal, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        assert job(3) == 24
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
        # Tasks
        @TaskTemplate()
        def normalize_count(count: int) -> int:
            return count + 1

        @TaskTemplate()
        def double_count(count: int) -> int:
            return count * 2

        @TaskTemplate()
        def generate_tripled_values(stop: int) -> Generator:
            for value in range(stop):
                yield value * 3

        # Linear Flow
        @LinearFlowTemplate(normalize_count, double_count, generate_tripled_values)
        def linear_flow_sync_generator_terminal(count: int) -> Generator:
            if False:
                yield count

        return apply_job(linear_flow_sync_generator_terminal, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(3)
        assert tuple(result) == (0, 3, 6, 9, 12, 15, 18, 21)
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
def case_linear_flow_async_coroutine_terminal_child() -> ComposedFlowCase[[int], Awaitable[int]]:
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def add_two_milliseconds(milliseconds: int) -> int:
            return milliseconds + 2

        @TaskTemplate()
        def double_milliseconds(milliseconds: int) -> int:
            return milliseconds * 2

        @TaskTemplate()
        async def wait_and_return_milliseconds(milliseconds: int) -> int:
            await asyncio.sleep(milliseconds / 1000)
            return milliseconds + 1

        # Linear Flow
        @LinearFlowTemplate(
            add_two_milliseconds,
            double_milliseconds,
            wait_and_return_milliseconds,
        )
        async def linear_flow_async_coroutine_terminal(milliseconds: int) -> int:
            ...

        return apply_job(linear_flow_async_coroutine_terminal, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 9
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
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
        # Tasks
        @TaskTemplate()
        def add_one(number: int) -> int:
            return number + 1

        @TaskTemplate()
        def add_two(number: int) -> int:
            return number + 2

        @TaskTemplate()
        async def emit_offset_series(limit: int) -> AsyncGenerator:
            for value in range(limit):
                await asyncio.sleep(0)
                yield value + 100

        # Linear Flow
        @LinearFlowTemplate(add_one, add_two, emit_offset_series)
        async def linear_flow_async_generator_terminal(number: int) -> AsyncGenerator:
            if False:
                yield number

        return apply_job(linear_flow_async_generator_terminal, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [100, 101, 102, 103, 104]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-async-generator-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-sync-function-terminal-child',
    tags=['matrix', 'dag-flow', 'sync', 'function'],
)
def case_dag_flow_sync_function_terminal_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def compute_base_number(number: int) -> int:
            return number + 2

        @TaskTemplate()
        def compute_branch_bonus(number: int) -> int:
            return number * 3

        @TaskTemplate()
        def combine_base_and_bonus(base_number: int, branch_bonus: int) -> int:
            return base_number + branch_bonus

        # DAG Flow
        @DagFlowTemplate(
            compute_base_number.refine(result_key='base_number'),
            compute_branch_bonus.refine(result_key='branch_bonus'),
            combine_base_and_bonus,
        )
        def dag_flow_sync_function_terminal(number: int) -> int:
            ...

        return apply_job(dag_flow_sync_function_terminal, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        assert job(3) == 14
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], int](
        name='dag-sync-function-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-sync-generator-terminal-child',
    tags=['matrix', 'dag-flow', 'sync', 'generator'],
)
def case_dag_flow_sync_generator_terminal_child() -> ComposedFlowCase[[int], Generator]:
    expected_callable_type = CallableType.SYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def compute_window_start(number: int) -> int:
            return number + 1

        @TaskTemplate()
        def compute_window_size(number: int) -> int:
            return number + 2

        @TaskTemplate()
        def generate_window(start: int, window_size: int) -> Generator:
            for value in range(start, start + window_size):
                yield value

        # DAG Flow
        @DagFlowTemplate(
            compute_window_start.refine(result_key='start'),
            compute_window_size.refine(result_key='window_size'),
            generate_window,
        )
        def dag_flow_sync_generator_terminal(number: int) -> Generator:
            if False:
                yield number

        return apply_job(dag_flow_sync_generator_terminal, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(3)
        assert tuple(result) == (4, 5, 6, 7, 8)
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Generator](
        name='dag-sync-generator-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-async-coroutine-terminal-child',
    tags=['matrix', 'dag-flow', 'async', 'coroutine'],
)
def case_dag_flow_async_coroutine_terminal_child() -> ComposedFlowCase[[int], Awaitable[int]]:
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def compute_wait_milliseconds(number: int) -> int:
            return number + 2

        @TaskTemplate()
        def compute_multiplier(number: int) -> int:
            return number + 3

        @TaskTemplate()
        async def wait_and_scale(wait_milliseconds: int, multiplier: int) -> int:
            await asyncio.sleep(wait_milliseconds / 1000)
            return wait_milliseconds * multiplier

        # DAG Flow
        @DagFlowTemplate(
            compute_wait_milliseconds.refine(result_key='wait_milliseconds'),
            compute_multiplier.refine(result_key='multiplier'),
            wait_and_scale,
        )
        async def dag_flow_async_coroutine_terminal(number: int) -> int:
            ...

        return apply_job(dag_flow_async_coroutine_terminal, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(4))
        assert result == 42
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='dag-async-coroutine-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-async-generator-terminal-child',
    tags=['matrix', 'dag-flow', 'async', 'generator'],
)
def case_dag_flow_async_generator_terminal_child() -> ComposedFlowCase[[int], AsyncGenerator]:
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def compute_series_start(number: int) -> int:
            return number + 10

        @TaskTemplate()
        def compute_series_step(number: int) -> int:
            return number + 1

        @TaskTemplate()
        async def emit_stepped_series(start: int, step: int) -> AsyncGenerator:
            for index in range(4):
                await asyncio.sleep(0)
                yield start + step * index

        # DAG Flow
        @DagFlowTemplate(
            compute_series_start.refine(result_key='start'),
            compute_series_step.refine(result_key='step'),
            emit_stepped_series,
        )
        async def dag_flow_async_generator_terminal(number: int) -> AsyncGenerator:
            if False:
                yield number

        return apply_job(dag_flow_async_generator_terminal, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(3)
        values = []
        async for value in result:
            values.append(value)
        assert values == [13, 17, 21, 25]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='dag-async-generator-terminal-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-sync-function-body',
    tags=['matrix', 'func-flow', 'sync', 'function'],
)
def case_func_flow_sync_function_body() -> ComposedFlowCase[[int, int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def multiply_number(number: int, factor: int) -> int:
            return number * factor

        @TaskTemplate()
        def add_two(number: int) -> int:
            return number + 2

        # Func Flow
        @FuncFlowTemplate()
        def func_flow_sync_function_body(number: int, factor: int) -> int:
            multiplied_number = multiply_number(number, factor)
            return add_two(multiplied_number)

        return apply_job(func_flow_sync_function_body, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        assert job(4, 3) == 14
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int, int], int](
        name='func-flow-sync-function-body',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-sync-generator-body',
    tags=['matrix', 'func-flow', 'sync', 'generator'],
)
def case_func_flow_sync_generator_body() -> ComposedFlowCase[[int], Generator]:
    expected_callable_type = CallableType.SYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def normalize_count(count: int) -> int:
            return count + 1

        @TaskTemplate()
        def generate_square_sequence(count: int) -> Generator:
            for value in range(count):
                yield value * value

        # Func Flow
        @FuncFlowTemplate()
        def func_flow_sync_generator_body(count: int) -> Generator:
            normalized_count = normalize_count(count)
            yield from generate_square_sequence(normalized_count)

        return apply_job(func_flow_sync_generator_body, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        generator = job(3)
        assert tuple(generator) == (0, 1, 4, 9)
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Generator](
        name='func-flow-sync-generator-body',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-async-coroutine-body',
    tags=['matrix', 'func-flow', 'async', 'coroutine'],
)
def case_func_flow_async_coroutine_body() -> ComposedFlowCase[[int], Awaitable[int]]:
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def add_buffer_milliseconds(milliseconds: int) -> int:
            return milliseconds + 3

        @TaskTemplate()
        async def wait_and_double_milliseconds(milliseconds: int) -> int:
            await asyncio.sleep(milliseconds / 1000)
            return milliseconds * 2

        # Func Flow
        @FuncFlowTemplate()
        async def func_flow_async_coroutine_body(milliseconds: int) -> int:
            buffered_milliseconds = add_buffer_milliseconds(milliseconds)
            return await wait_and_double_milliseconds(buffered_milliseconds)

        return apply_job(func_flow_async_coroutine_body, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 10
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='func-flow-async-coroutine-body',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-async-generator-body',
    tags=['matrix', 'func-flow', 'async', 'generator'],
)
def case_func_flow_async_generator_body() -> ComposedFlowCase[[int], AsyncGenerator]:
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def compute_series_start(number: int) -> int:
            return number * 2

        @TaskTemplate()
        async def emit_three_values(start: int) -> AsyncGenerator:
            for value in range(start, start + 3):
                await asyncio.sleep(0)
                yield value

        # Func Flow
        @FuncFlowTemplate()
        async def func_flow_async_generator_body(number: int) -> AsyncGenerator:
            series_start = compute_series_start(number)
            async for value in emit_three_values(series_start):
                yield value

        return apply_job(func_flow_async_generator_body, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(4)
        values = []
        async for value in result:
            values.append(value)
        assert values == [8, 9, 10]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='func-flow-async-generator-body',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )
