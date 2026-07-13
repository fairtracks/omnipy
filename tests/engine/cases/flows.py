import asyncio
from typing import AsyncGenerator, AsyncIterator, Awaitable, cast, Generator

import pytest_cases as pc

from omnipy import Void
from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.job import IsDagFlow, IsFuncArgJob
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.util.callable_types import CallableType
from omnipy.util.helpers import resolve

from ..helpers.classes import ComposedFlowCase
from ..helpers.functions import apply_job, assert_job_state


def assert_case_callable_type_and_finished_state(
    job: IsFuncArgJob,
    expected_callable_type: CallableType.Literals,
) -> None:
    assert job.callable_type is expected_callable_type
    assert_job_state(job, [RunState.FINISHED])


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
            yield from Void()  # For generator signature only; never run.

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
            async for _ in Void():  # For generator signature only; never run.
                yield _

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
            yield from Void()  # For generator signature only; never run.

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
            async for _ in Void():  # For generator signature only; never run.
                yield _

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


@pc.case(
    id='linear-parent-child-with-linear-child',
    tags=['semantic-floor', 'linear-parent', 'linear-child', 'linear-parent-child'],
)
def case_linear_parent_with_linear_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def add_two(number: int) -> int:
            return number + 2

        @TaskTemplate()
        def multiply_by_three(number: int) -> int:
            return number * 3

        @TaskTemplate()
        def subtract_one(number: int) -> int:
            return number - 1

        # Linear Child Flow
        @LinearFlowTemplate(multiply_by_three, subtract_one)
        def linear_child(number: int) -> int:
            ...

        # Linear Parent Flow
        @LinearFlowTemplate(add_two, linear_child)
        def linear_parent(number: int) -> int:
            ...

        return apply_job(linear_parent, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(4) == 17
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='linear-parent-child-with-linear-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-parent-child-with-dag-child',
    tags=['semantic-floor', 'linear-parent', 'dag-child', 'linear-parent-child'],
)
def case_linear_parent_with_dag_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def add_one(number: int) -> int:
            return number + 1

        @TaskTemplate()
        def compute_base(number: int) -> int:
            return number * 3

        @TaskTemplate()
        def compute_bonus(number: int) -> int:
            return number - 2

        @TaskTemplate()
        def combine_base_and_bonus(base: int, bonus: int) -> int:
            return base + bonus

        # DAG Child Flow
        @DagFlowTemplate(
            compute_base.refine(result_key='base'),
            compute_bonus.refine(result_key='bonus'),
            combine_base_and_bonus,
        )
        def dag_child(number: int) -> int:
            ...

        # Linear Parent Flow
        @LinearFlowTemplate(add_one, dag_child)
        def linear_parent(number: int) -> int:
            ...

        return apply_job(linear_parent, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(5) == 22
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='linear-parent-child-with-dag-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-parent-child-with-func-child',
    tags=['semantic-floor', 'linear-parent', 'func-child', 'linear-parent-child'],
)
def case_linear_parent_with_func_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def double_number(number: int) -> int:
            return number * 2

        @TaskTemplate()
        def add_five(number: int) -> int:
            return number + 5

        @TaskTemplate()
        def multiply_by_four(number: int) -> int:
            return number * 4

        # Func Child Flow
        @FuncFlowTemplate()
        def func_child(number: int) -> int:
            buffered_number = add_five(number)
            return multiply_by_four(buffered_number)

        # Linear Parent Flow
        @LinearFlowTemplate(double_number, func_child)
        def linear_parent(number: int) -> int:
            ...

        return apply_job(linear_parent, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(3) == 44
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='linear-parent-child-with-func-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-parent-child-with-linear-child',
    tags=['semantic-floor', 'dag-parent', 'linear-child'],
)
def case_dag_parent_with_linear_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def compute_base_value(number: int) -> int:
            return number + 4

        @TaskTemplate()
        def compute_branch_value(number: int) -> int:
            return number * 2

        @TaskTemplate()
        def combine_parent_branches(base_value: int, branch_value: int) -> int:
            return base_value + branch_value

        @TaskTemplate()
        def subtract_branch_offset(total_value: int) -> int:
            return total_value - 3

        # Linear Child Flow
        @LinearFlowTemplate(combine_parent_branches, subtract_branch_offset)
        def linear_child_from_dag_parent(base_value: int, branch_value: int) -> int:
            ...

        # DAG Parent Flow
        @DagFlowTemplate(
            compute_base_value.refine(result_key='base_value'),
            compute_branch_value.refine(result_key='branch_value'),
            linear_child_from_dag_parent,
        )
        def dag_parent_with_linear_child(number: int) -> int:
            ...

        return apply_job(dag_parent_with_linear_child, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(5) == 16
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='dag-parent-child-with-linear-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-parent-child-with-dag-child',
    tags=['semantic-floor', 'dag-parent', 'dag-child'],
)
def case_dag_parent_with_dag_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Parent Tasks
        @TaskTemplate()
        def compute_left_value(number: int) -> int:
            return number + 1

        @TaskTemplate()
        def compute_right_value(number: int) -> int:
            return number * 4

        # Child Tasks
        @TaskTemplate()
        def compute_child_total(left_value: int, right_value: int) -> int:
            return left_value + right_value

        @TaskTemplate()
        def compute_child_gap(left_value: int, right_value: int) -> int:
            return right_value - left_value

        @TaskTemplate()
        def combine_child_total_and_gap(child_total: int, child_gap: int) -> int:
            return child_total + child_gap

        # DAG Child Flow
        @DagFlowTemplate(
            compute_child_total.refine(result_key='child_total'),
            compute_child_gap.refine(result_key='child_gap'),
            combine_child_total_and_gap,
        )
        def dag_child_from_dag_parent(left_value: int, right_value: int) -> int:
            ...

        # DAG Parent Flow
        @DagFlowTemplate(
            compute_left_value.refine(result_key='left_value'),
            compute_right_value.refine(result_key='right_value'),
            dag_child_from_dag_parent,
        )
        def dag_parent_with_dag_child(number: int) -> int:
            ...

        return apply_job(dag_parent_with_dag_child, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(3) == 24
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='dag-parent-child-with-dag-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-parent-child-with-func-child',
    tags=['semantic-floor', 'dag-parent', 'func-child'],
)
def case_dag_parent_with_func_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Parent Tasks
        @TaskTemplate()
        def compute_primary_value(number: int) -> int:
            return number + 2

        @TaskTemplate()
        def compute_secondary_value(number: int) -> int:
            return number * 3

        # Func Child Tasks
        @TaskTemplate()
        def add_child_inputs(primary_value: int, secondary_value: int) -> int:
            return primary_value + secondary_value

        @TaskTemplate()
        def square_child_input(number: int) -> int:
            return number * number

        # Func Child Flow
        @FuncFlowTemplate()
        def func_child_from_dag_parent(primary_value: int, secondary_value: int) -> int:
            combined_value = add_child_inputs(primary_value, secondary_value)
            return square_child_input(combined_value)

        # DAG Parent Flow
        @DagFlowTemplate(
            compute_primary_value.refine(result_key='primary_value'),
            compute_secondary_value.refine(result_key='secondary_value'),
            func_child_from_dag_parent,
        )
        def dag_parent_with_func_child(number: int) -> int:
            ...

        return apply_job(dag_parent_with_func_child, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(2) == 100
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='dag-parent-child-with-func-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-parent-child-routing',
    tags=['semantic-floor', 'dag-parent', 'dag-routing'],
)
def case_dag_parent_child_routing() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Parent Tasks
        @TaskTemplate()
        def compute_mapped_input(seed: int) -> int:
            return seed + 5

        @TaskTemplate()
        def compute_mapped_multiplier(seed: int) -> int:
            return seed * 2

        # Child Tasks
        @TaskTemplate()
        def scale_child_value(value: int, multiplier: int) -> int:
            return value * multiplier

        @TaskTemplate()
        def compute_child_checksum(value: int, scaled_value: int) -> int:
            return value + scaled_value

        @TaskTemplate()
        def finalize_parent_routed_result(mapped_input: int, child_checksum: int) -> int:
            return child_checksum - mapped_input

        # DAG Child Flow
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
        def dag_child_with_routing(child_value: int, child_multiplier: int) -> int:
            ...

        # DAG Parent Flow
        @DagFlowTemplate(
            compute_mapped_input.refine(result_key='mapped_input'),
            compute_mapped_multiplier.refine(result_key='mapped_multiplier'),
            dag_child_with_routing.refine(
                param_key_map={
                    'child_value': 'mapped_input',
                    'child_multiplier': 'mapped_multiplier',
                },
                result_key='child_checksum',
            ),
            finalize_parent_routed_result,
        )
        def dag_parent_child_routing(seed: int) -> int:
            ...

        return apply_job(dag_parent_child_routing, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(3) == 48
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='dag-parent-child-routing',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-parent-child-refine-revise',
    tags=['semantic-floor', 'dag-parent', 'dag-refine-revise'],
)
def case_dag_parent_child_refine_revise() -> ComposedFlowCase[[int], int]:  # noqa: C901
    expected_callable_type = CallableType.SYNC_FUNCTION

    # Parent Tasks
    @TaskTemplate()
    def compute_left_value(number: int) -> int:
        return number + 1

    @TaskTemplate()
    def compute_right_value(number: int) -> int:
        return number * 2

    # Child Tasks
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

    # Child Flows
    @LinearFlowTemplate(combine_child_values, multiply_combined_value)
    def initial_linear_child(left_value: int, right_value: int) -> int:
        ...

    @LinearFlowTemplate(combine_child_values, subtract_from_combined_value)
    def replacement_linear_child(left_value: int, right_value: int) -> int:
        ...

    # DAG Parent Flow
    @DagFlowTemplate(
        compute_left_value.refine(result_key='left_value'),
        compute_right_value.refine(result_key='right_value'),
        initial_linear_child.refine(result_key='child_result'),
        return_child_result,
    )
    def dag_parent_child_refine_revise(number: int) -> int:
        ...

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        return apply_job(dag_parent_child_refine_revise, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        initial_result = job(4)
        assert initial_result == 26
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

        dag_job = cast(IsDagFlow, job)
        revised_child_templates = list(dag_job.child_job_templates)
        revised_child_templates[2] = replacement_linear_child.refine(result_key='child_result')

        revised_job = dag_job.revise().refine(*revised_child_templates).apply()
        revised_result = revised_job(4)

        assert revised_result == 10
        assert revised_result != initial_result
        assert_case_callable_type_and_finished_state(revised_job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='dag-parent-child-refine-revise',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-calls-linear-child',
    tags=['semantic-floor', 'func-flow-calls-flow'],
)
def case_func_flow_calls_linear_child() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
        @TaskTemplate()
        def add_three(number: int) -> int:
            return number + 3

        @TaskTemplate()
        def double_number(number: int) -> int:
            return number * 2

        # Linear Child Flow
        @LinearFlowTemplate(add_three, double_number)
        def linear_child_flow(number: int) -> int:
            ...

        # Func Parent Flow
        @FuncFlowTemplate()
        def func_parent_calls_linear_child(number: int) -> int:
            return linear_child_flow(number)

        return apply_job(func_parent_calls_linear_child, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(4) == 14
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='func-flow-calls-linear-child',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-mixed-sync-async',
    tags=['semantic-floor', 'func-flow-mixed-async'],
)
def case_func_flow_mixed_sync_async() -> ComposedFlowCase[[int], Awaitable[int]]:
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Sync Tasks
        @TaskTemplate()
        def add_two(number: int) -> int:
            return number + 2

        @TaskTemplate()
        def square_number(number: int) -> int:
            return number * number

        # Async Task
        @TaskTemplate()
        async def wait_and_add_five(number: int) -> int:
            await asyncio.sleep(0)
            return number + 5

        # Sync Child Flow
        @LinearFlowTemplate(add_two, square_number)
        def sync_linear_child(number: int) -> int:
            ...

        # Async Child Flow
        @FuncFlowTemplate()
        async def async_child_flow(number: int) -> int:
            return await wait_and_add_five(number)

        # Func Parent Flow
        @FuncFlowTemplate()
        async def func_parent_mixed_sync_async(number: int) -> int:
            sync_child_result = sync_linear_child(number)
            return await async_child_flow(sync_child_result)

        return apply_job(func_parent_mixed_sync_async, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        result = await resolve(job(3))
        assert result == 30
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], Awaitable[int]](
        name='func-flow-mixed-sync-async',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-sync-generator-child-sync-function',
    tags=['semantic-floor', 'func-flow-child-sg-parent-sf'],
)
def case_func_flow_sync_generator_child_sync_function() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @FuncFlowTemplate()
        def func_flow_sync_generator_child_sync_function(number: int) -> int:
            return sum(values(number))

        return apply_job(func_flow_sync_generator_child_sync_function, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job(2) == 9
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='func-flow-sync-generator-child-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-async-coroutine-child-async-generator',
    tags=['semantic-floor', 'func-flow-child-ac-parent-ag'],
)
def case_func_flow_async_coroutine_child_async_generator(
) -> ComposedFlowCase[[int], AsyncGenerator]:
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def compute_start(number: int) -> int:
            await asyncio.sleep(0)
            return number * 2

        @FuncFlowTemplate()
        async def func_flow_async_coroutine_child_async_generator(number: int) -> AsyncGenerator:
            start = await compute_start(number)
            for value in range(start, start + 3):
                await asyncio.sleep(0)
                yield value

        return apply_job(func_flow_async_coroutine_child_async_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        values = []
        async for value in job(3):
            values.append(value)
        assert values == [6, 7, 8]
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], AsyncGenerator](
        name='func-flow-async-coroutine-child-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-async-generator-child-async-coroutine',
    tags=['semantic-floor', 'func-flow-child-ag-parent-ac'],
)
def case_func_flow_async_generator_child_async_coroutine(
) -> ComposedFlowCase[[int], Awaitable[int]]:
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @FuncFlowTemplate()
        async def func_flow_async_generator_child_async_coroutine(number: int) -> int:
            total = 0
            async for value in emit_async_values(number):
                total += value
            return total

        return apply_job(func_flow_async_generator_child_async_coroutine, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        result = await resolve(job(2))
        assert result == 9
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], Awaitable[int]](
        name='func-flow-async-generator-child-async-coroutine',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-async-generator-child-sync-generator',
    tags=['semantic-floor', 'func-flow-child-ag-parent-sg'],
)
def case_func_flow_async_generator_child_sync_generator(
) -> ComposedFlowCase[[int], Generator]:
    expected_callable_type = CallableType.SYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @FuncFlowTemplate()
        def func_flow_async_generator_child_sync_generator(number: int) -> Generator:
            yield emit_async_values(number)

        return apply_job(func_flow_async_generator_child_sync_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        nested_generators = tuple(job(2))
        assert len(nested_generators) == 1

        nested_values = []
        async for value in nested_generators[0]:
            nested_values.append(value)

        assert nested_values == [2, 3, 4]
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], Generator](
        name='func-flow-async-generator-child-sync-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-sync-generator-child-async-coroutine',
    tags=['semantic-floor', 'func-flow-child-sg-parent-ac'],
)
def case_func_flow_sync_generator_child_async_coroutine(
) -> ComposedFlowCase[[int], Awaitable[int]]:
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @FuncFlowTemplate()
        async def func_flow_sync_generator_child_async_coroutine(number: int) -> int:
            await asyncio.sleep(0)
            return sum(values(number))

        return apply_job(func_flow_sync_generator_child_async_coroutine, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        result = await resolve(job(2))
        assert result == 9
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], Awaitable[int]](
        name='func-flow-sync-generator-child-async-coroutine',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-sync-generator-child-async-generator',
    tags=['semantic-floor', 'func-flow-child-sg-parent-ag'],
)
def case_func_flow_sync_generator_child_async_generator(
) -> ComposedFlowCase[[int], AsyncGenerator]:
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @FuncFlowTemplate()
        async def func_flow_sync_generator_child_async_generator(number: int) -> AsyncGenerator:
            for value in values(number):
                await asyncio.sleep(0)
                yield value * 2

        return apply_job(func_flow_sync_generator_child_async_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        values = []
        async for value in job(2):
            values.append(value)
        assert values == [4, 6, 8]
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], AsyncGenerator](
        name='func-flow-sync-generator-child-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-async-coroutine-child-sync-generator',
    tags=['semantic-floor', 'func-flow-child-ac-parent-sg'],
)
def case_func_flow_async_coroutine_child_sync_generator(
) -> ComposedFlowCase[[int], Generator]:
    expected_callable_type = CallableType.SYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def compute_value(number: int) -> int:
            await asyncio.sleep(0)
            return number * 2

        @FuncFlowTemplate()
        def func_flow_async_coroutine_child_sync_generator(number: int) -> Generator:
            yield compute_value(number)
            yield compute_value(number + 1)

        return apply_job(func_flow_async_coroutine_child_sync_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        yielded_awaitables = tuple(job(3))
        assert len(yielded_awaitables) == 2

        resolved_values = [await resolve(awaitable) for awaitable in yielded_awaitables]
        assert resolved_values == [6, 8]
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], Generator](
        name='func-flow-async-coroutine-child-sync-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-async-coroutine-child-sync-function',
    tags=['semantic-floor', 'func-flow-child-ac-parent-sf'],
)
def case_func_flow_async_coroutine_child_sync_function() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def compute_value(number: int) -> int:
            await asyncio.sleep(0)
            return number * 2

        @FuncFlowTemplate()
        def func_flow_async_coroutine_child_sync_function(number: int):
            return compute_value(number)

        return apply_job(func_flow_async_coroutine_child_sync_function, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        result = await resolve(job(3))
        assert result == 6
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='func-flow-async-coroutine-child-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-async-generator-child-sync-function',
    tags=['semantic-floor', 'func-flow-child-ag-parent-sf'],
)
def case_func_flow_async_generator_child_sync_function() -> ComposedFlowCase[[int], int]:
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @FuncFlowTemplate()
        def func_flow_async_generator_child_sync_function(number: int):
            return emit_async_values(number)

        return apply_job(func_flow_async_generator_child_sync_function, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        result = await resolve(job(2))
        values = []
        async for value in result:
            values.append(value)
        assert values == [2, 3, 4]
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], int](
        name='func-flow-async-generator-child-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-terminal-sync-generator',
    tags=['semantic-floor', 'linear-flow-early-async-generator'],
)
def case_linear_flow_early_async_terminal_sync_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def add_one(number: int) -> int:
            return number + 1

        @TaskTemplate()
        async def double_number(number: int) -> int:
            await asyncio.sleep(0)
            return number * 2

        @TaskTemplate()
        def add_two(number: int) -> int:
            return number + 2

        @TaskTemplate()
        def emit_sync_series(limit: int) -> Generator:
            for value in range(limit, limit + 3):
                yield value

        @LinearFlowTemplate(add_one, double_number, add_two, emit_sync_series)
        async def linear_flow_early_async_terminal_sync_generator(number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(linear_flow_early_async_terminal_sync_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [8, 9, 10]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-flow-early-async-terminal-sync-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-terminal-async-generator',
    tags=['semantic-floor', 'linear-flow-early-async-generator'],
)
def case_linear_flow_early_async_terminal_async_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def add_one(number: int) -> int:
            return number + 1

        @TaskTemplate()
        async def double_number(number: int) -> int:
            await asyncio.sleep(0)
            return number * 2

        @TaskTemplate()
        def add_two(number: int) -> int:
            return number + 2

        @TaskTemplate()
        async def emit_async_series(limit: int) -> AsyncGenerator:
            for value in range(limit, limit + 3):
                await asyncio.sleep(0)
                yield value

        @LinearFlowTemplate(add_one, double_number, add_two, emit_async_series)
        async def linear_flow_early_async_terminal_async_generator(number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(linear_flow_early_async_terminal_async_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [8, 9, 10]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-flow-early-async-terminal-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-terminal-sync-generator',
    tags=['semantic-floor', 'dag-flow-early-async-generator'],
)
def case_dag_flow_early_async_terminal_sync_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def compute_base(number: int) -> dict[str, int]:
            return {'base': number + 1}

        @TaskTemplate()
        async def compute_async_value(base: int) -> int:
            await asyncio.sleep(0)
            return base * 2

        @TaskTemplate()
        def compute_limit(async_value: int) -> int:
            return async_value + 2

        @TaskTemplate()
        def emit_sync_series(limit: int) -> Generator:
            for value in range(limit, limit + 3):
                yield value

        @DagFlowTemplate(
            compute_base,
            compute_async_value.refine(result_key='async_value'),
            compute_limit.refine(result_key='limit'),
            emit_sync_series,
        )
        async def dag_flow_early_async_terminal_sync_generator(number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(dag_flow_early_async_terminal_sync_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [8, 9, 10]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='dag-flow-early-async-terminal-sync-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-terminal-async-generator',
    tags=['semantic-floor', 'dag-flow-early-async-generator'],
)
def case_dag_flow_early_async_terminal_async_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def compute_base(number: int) -> dict[str, int]:
            return {'base': number + 1}

        @TaskTemplate()
        async def compute_async_value(base: int) -> int:
            await asyncio.sleep(0)
            return base * 2

        @TaskTemplate()
        def compute_limit(async_value: int) -> int:
            return async_value + 2

        @TaskTemplate()
        async def emit_async_series(limit: int) -> AsyncGenerator:
            for value in range(limit, limit + 3):
                await asyncio.sleep(0)
                yield value

        @DagFlowTemplate(
            compute_base,
            compute_async_value.refine(result_key='async_value'),
            compute_limit.refine(result_key='limit'),
            emit_async_series,
        )
        async def dag_flow_early_async_terminal_async_generator(number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(dag_flow_early_async_terminal_async_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [8, 9, 10]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='dag-flow-early-async-terminal-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-generator-terminal-async-coroutine',
    tags=['semantic-floor', 'linear-flow-early-async-generator'],
)
def case_linear_flow_early_async_generator_terminal_async_coroutine(  # noqa: C901
) -> ComposedFlowCase[[int], Awaitable[int]]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        async def sum_async_values(values: AsyncGenerator) -> int:
            total = 0
            async for value in values:
                total += value
            return total

        @LinearFlowTemplate(emit_async_values, sum_async_values)
        async def linear_flow_early_async_generator_terminal_async_coroutine(number: int) -> int:
            ...

        return apply_job(linear_flow_early_async_generator_terminal_async_coroutine,
                         engine,
                         registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 9
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='linear-flow-early-async-generator-terminal-async-coroutine',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-generator-terminal-async-generator',
    tags=['semantic-floor', 'linear-flow-early-async-generator'],
)
def case_linear_flow_early_async_generator_terminal_async_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        async def emit_async_series(values: AsyncGenerator) -> AsyncGenerator:
            async for value in values:
                await asyncio.sleep(0)
                yield value * 2

        @LinearFlowTemplate(emit_async_values, emit_async_series)
        async def linear_flow_early_async_generator_terminal_async_generator(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(linear_flow_early_async_generator_terminal_async_generator,
                         engine,
                         registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [4, 6, 8]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-flow-early-async-generator-terminal-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-generator-terminal-async-coroutine',
    tags=['semantic-floor', 'dag-flow-early-async-generator'],
)
def case_dag_flow_early_async_generator_terminal_async_coroutine(  # noqa: C901
) -> ComposedFlowCase[[int], Awaitable[int]]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        async def sum_async_values(values: AsyncGenerator) -> int:
            total = 0
            async for value in values:
                total += value
            return total

        @DagFlowTemplate(emit_async_values.refine(result_key='values'), sum_async_values)
        async def dag_flow_early_async_generator_terminal_async_coroutine(number: int) -> int:
            ...

        return apply_job(dag_flow_early_async_generator_terminal_async_coroutine, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 9
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='dag-flow-early-async-generator-terminal-async-coroutine',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-generator-terminal-async-generator',
    tags=['semantic-floor', 'dag-flow-early-async-generator'],
)
def case_dag_flow_early_async_generator_terminal_async_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        async def emit_async_series(values: AsyncGenerator) -> AsyncGenerator:
            async for value in values:
                await asyncio.sleep(0)
                yield value * 2

        @DagFlowTemplate(emit_async_values.refine(result_key='values'), emit_async_series)
        async def dag_flow_early_async_generator_terminal_async_generator(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(dag_flow_early_async_generator_terminal_async_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [4, 6, 8]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='dag-flow-early-async-generator-terminal-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-generator-middle-sync-terminal-async-coroutine',
    tags=['semantic-floor', 'linear-flow-early-async-generator'],
)
def case_linear_flow_early_async_generator_middle_sync_terminal_async_coroutine(  # noqa: C901
) -> ComposedFlowCase[[int], Awaitable[int]]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        def pass_values_through(values: AsyncGenerator) -> AsyncGenerator:
            return values

        @TaskTemplate()
        async def sum_async_values(values: AsyncGenerator) -> int:
            total = 0
            async for value in values:
                total += value
            return total

        @LinearFlowTemplate(emit_async_values, pass_values_through, sum_async_values)
        async def linear_flow_early_async_generator_middle_sync_terminal_async_coroutine(
                number: int) -> int:
            ...

        return apply_job(linear_flow_early_async_generator_middle_sync_terminal_async_coroutine,
                         engine,
                         registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 9
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='linear-flow-early-async-generator-middle-sync-terminal-async-coroutine',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-generator-middle-sync-terminal-async-generator',
    tags=['semantic-floor', 'linear-flow-early-async-generator'],
)
def case_linear_flow_early_async_generator_middle_sync_terminal_async_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        def pass_values_through(values: AsyncGenerator) -> AsyncGenerator:
            return values

        @TaskTemplate()
        async def emit_async_from_values(values: AsyncGenerator) -> AsyncGenerator:
            async for value in values:
                await asyncio.sleep(0)
                yield value * 2

        @LinearFlowTemplate(emit_async_values, pass_values_through, emit_async_from_values)
        async def linear_flow_early_async_generator_middle_sync_terminal_async_generator(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(linear_flow_early_async_generator_middle_sync_terminal_async_generator,
                         engine,
                         registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [4, 6, 8]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-flow-early-async-generator-middle-sync-terminal-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-generator-independent-sync-terminal-async-coroutine',
    tags=['semantic-floor', 'dag-flow-early-async-generator'],
)
def case_dag_flow_early_async_generator_independent_sync_terminal_async_coroutine(  # noqa: C901
) -> ComposedFlowCase[[int], Awaitable[int]]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        def compute_offset(number: int) -> int:
            return number + 10

        @TaskTemplate()
        async def sum_async_values(values: AsyncGenerator, offset: int) -> int:
            total = 0
            async for value in values:
                total += value
            return total + offset

        @DagFlowTemplate(
            emit_async_values.refine(result_key='values'),
            compute_offset.refine(result_key='offset'),
            sum_async_values)
        async def dag_flow_early_async_generator_independent_sync_terminal_async_coroutine(
                number: int) -> int:
            ...

        return apply_job(
            dag_flow_early_async_generator_independent_sync_terminal_async_coroutine,
            engine,
            registry,
        )

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 21
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='dag-flow-early-async-generator-independent-sync-terminal-async-coroutine',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-sync-generator-terminal-sync-generator',
    tags=['semantic-floor', 'linear-flow-early-sync-generator'],
)
def case_linear_flow_early_sync_generator_terminal_sync_generator(  # noqa: C901
) -> ComposedFlowCase[[int], Generator]:  # noqa: C901
    expected_callable_type = CallableType.SYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @TaskTemplate()
        def emit_sync_from_values(values: Generator) -> Generator:
            for value in values:
                yield value * 2

        @LinearFlowTemplate(values, emit_sync_from_values)
        def linear_flow_early_sync_generator_terminal_sync_generator(number: int) -> Generator:
            yield from Void()  # For generator signature only; never run.

        return apply_job(linear_flow_early_sync_generator_terminal_sync_generator, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        assert tuple(job(2)) == (4, 6, 8)
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Generator](
        name='linear-flow-early-sync-generator-terminal-sync-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-sync-generator-terminal-sync-generator',
    tags=['semantic-floor', 'dag-flow-early-sync-generator'],
)
def case_dag_flow_early_sync_generator_terminal_sync_generator(  # noqa: C901
) -> ComposedFlowCase[[int], Generator]:  # noqa: C901
    expected_callable_type = CallableType.SYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @TaskTemplate()
        def emit_sync_from_values(values: Generator) -> Generator:
            for value in values:
                yield value * 2

        @DagFlowTemplate(values.refine(result_key='values'), emit_sync_from_values)
        def dag_flow_early_sync_generator_terminal_sync_generator(number: int) -> Generator:
            yield from Void()  # For generator signature only; never run.

        return apply_job(dag_flow_early_sync_generator_terminal_sync_generator, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        assert tuple(job(2)) == (4, 6, 8)
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Generator](
        name='dag-flow-early-sync-generator-terminal-sync-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-generator-independent-sync-terminal-async-generator',
    tags=['semantic-floor', 'dag-flow-early-async-generator'],
)
def case_dag_flow_early_async_generator_independent_sync_terminal_async_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        def compute_offset(number: int) -> int:
            return number + 10

        @TaskTemplate()
        async def emit_async_from_values(values: AsyncGenerator, offset: int) -> AsyncGenerator:
            async for value in values:
                await asyncio.sleep(0)
                yield value + offset

        @DagFlowTemplate(
            emit_async_values.refine(result_key='values'),
            compute_offset.refine(result_key='offset'),
            emit_async_from_values)
        async def dag_flow_early_async_generator_independent_sync_terminal_async_generator(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(
            dag_flow_early_async_generator_independent_sync_terminal_async_generator,
            engine,
            registry,
        )

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [14, 15, 16]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='dag-flow-early-async-generator-independent-sync-terminal-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-generator-terminal-sync-function',
    tags=['semantic-floor', 'linear-flow-early-async-generator'],
)
def case_linear_flow_early_async_generator_terminal_sync_function(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        def pass_values_through(values: AsyncGenerator) -> AsyncIterator[int]:
            return values

        @LinearFlowTemplate(emit_async_values, pass_values_through)
        async def linear_flow_early_async_generator_terminal_sync_function(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For async-generator signature only; never run.
                yield _

        return apply_job(linear_flow_early_async_generator_terminal_sync_function,
                         engine,
                         registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [2, 3, 4]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-flow-early-async-generator-terminal-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-generator-terminal-sync-generator',
    tags=['semantic-floor', 'linear-flow-early-async-generator'],
)
def case_linear_flow_early_async_generator_terminal_sync_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        def emit_sync_wrapped_values(values: AsyncGenerator) -> Generator:
            yield values

        @LinearFlowTemplate(emit_async_values, emit_sync_wrapped_values)
        async def linear_flow_early_async_generator_terminal_sync_generator(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For async-generator signature only; never run.
                yield _

        return apply_job(linear_flow_early_async_generator_terminal_sync_generator,
                         engine,
                         registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        wrapped_values = []
        async for values in result:
            nested_values = []
            async for value in values:
                nested_values.append(value)
            wrapped_values.append(tuple(nested_values))
        assert wrapped_values == [(2, 3, 4)]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-flow-early-async-generator-terminal-sync-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-async-terminal-sync-function',
    tags=['semantic-floor', 'linear-flow-early-async-function'],
)
def case_linear_flow_early_async_terminal_sync_function(  # noqa: C901
) -> ComposedFlowCase[[int], Awaitable[int]]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def add_one(number: int) -> int:
            return number + 1

        @TaskTemplate()
        async def double_number(number: int) -> int:
            await asyncio.sleep(0)
            return number * 2

        @TaskTemplate()
        def add_five(number: int) -> int:
            return number + 5

        @LinearFlowTemplate(add_one, double_number, add_five)
        async def linear_flow_early_async_terminal_sync_function(number: int) -> int:
            ...

        return apply_job(linear_flow_early_async_terminal_sync_function, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 11
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='linear-flow-early-async-terminal-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-sync-generator-terminal-sync-function',
    tags=['semantic-floor', 'linear-flow-early-sync-generator'],
)
def case_linear_flow_early_sync_generator_terminal_sync_function(  # noqa: C901
) -> ComposedFlowCase[[int], int]:  # noqa: C901
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @TaskTemplate()
        def sum_values(values: Generator) -> int:
            return sum(values)

        @TaskTemplate()
        def add_five(total: int) -> int:
            return total + 5

        @LinearFlowTemplate(values, sum_values, add_five)
        def linear_flow_early_sync_generator_terminal_sync_function(number: int) -> int:
            ...

        return apply_job(linear_flow_early_sync_generator_terminal_sync_function, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        assert job(2) == 14
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], int](
        name='linear-flow-early-sync-generator-terminal-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-sync-generator-terminal-async-coroutine',
    tags=['semantic-floor', 'linear-flow-early-sync-generator'],
)
def case_linear_flow_early_sync_generator_terminal_async_coroutine(  # noqa: C901
) -> ComposedFlowCase[[int], Awaitable[int]]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @TaskTemplate()
        async def sum_values_async(values: Generator) -> int:
            await asyncio.sleep(0)
            return sum(values) * 2

        @LinearFlowTemplate(values, sum_values_async)
        async def linear_flow_early_sync_generator_terminal_async_coroutine(number: int) -> int:
            ...

        return apply_job(linear_flow_early_sync_generator_terminal_async_coroutine,
                         engine,
                         registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 18
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='linear-flow-early-sync-generator-terminal-async-coroutine',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='linear-flow-early-sync-generator-terminal-async-generator',
    tags=['semantic-floor', 'linear-flow-early-sync-generator'],
)
def case_linear_flow_early_sync_generator_terminal_async_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @TaskTemplate()
        async def emit_async_series(values: Generator) -> AsyncGenerator:
            for value in values:
                await asyncio.sleep(0)
                yield value * 2

        @LinearFlowTemplate(values, emit_async_series)
        async def linear_flow_early_sync_generator_terminal_async_generator(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(linear_flow_early_sync_generator_terminal_async_generator,
                         engine,
                         registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [4, 6, 8]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='linear-flow-early-sync-generator-terminal-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-terminal-sync-function',
    tags=['semantic-floor', 'dag-flow-early-async-function'],
)
def case_dag_flow_early_async_terminal_sync_function(  # noqa: C901
) -> ComposedFlowCase[[int], Awaitable[int]]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def compute_base(number: int) -> dict[str, int]:
            return {'base': number + 1}

        @TaskTemplate()
        async def compute_async_value(base: int) -> int:
            await asyncio.sleep(0)
            return base * 2

        @TaskTemplate()
        def finish_value(base: int, async_value: int) -> int:
            return base + async_value

        @DagFlowTemplate(
            compute_base,
            compute_async_value.refine(result_key='async_value'),
            finish_value,
        )
        async def dag_flow_early_async_terminal_sync_function(number: int) -> int:
            ...

        return apply_job(dag_flow_early_async_terminal_sync_function, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 9
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='dag-flow-early-async-terminal-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-sync-generator-terminal-sync-function',
    tags=['semantic-floor', 'dag-flow-early-sync-generator'],
)
def case_dag_flow_early_sync_generator_terminal_sync_function(  # noqa: C901
) -> ComposedFlowCase[[int], int]:  # noqa: C901
    expected_callable_type = CallableType.SYNC_FUNCTION

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @TaskTemplate()
        def sum_values(values: Generator) -> int:
            return sum(values)

        @DagFlowTemplate(values, sum_values)
        def dag_flow_early_sync_generator_terminal_sync_function(number: int) -> int:
            ...

        return apply_job(dag_flow_early_sync_generator_terminal_sync_function, engine, registry)

    def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        assert job(2) == 9
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], int](
        name='dag-flow-early-sync-generator-terminal-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-sync-generator-terminal-async-coroutine',
    tags=['semantic-floor', 'dag-flow-early-sync-generator'],
)
def case_dag_flow_early_sync_generator_terminal_async_coroutine(  # noqa: C901
) -> ComposedFlowCase[[int], Awaitable[int]]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @TaskTemplate()
        async def sum_values_async(values: Generator) -> int:
            await asyncio.sleep(0)
            return sum(values) * 2

        @DagFlowTemplate(values, sum_values_async)
        async def dag_flow_early_sync_generator_terminal_async_coroutine(number: int) -> int:
            ...

        return apply_job(dag_flow_early_sync_generator_terminal_async_coroutine, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = await resolve(job(2))
        assert result == 18
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], Awaitable[int]](
        name='dag-flow-early-sync-generator-terminal-async-coroutine',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-sync-generator-terminal-async-generator',
    tags=['semantic-floor', 'dag-flow-early-sync-generator'],
)
def case_dag_flow_early_sync_generator_terminal_async_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        def values(number: int) -> Generator:
            for value in range(number, number + 3):
                yield value

        @TaskTemplate()
        async def emit_async_series(values: Generator) -> AsyncGenerator:
            for value in values:
                await asyncio.sleep(0)
                yield value * 2

        @DagFlowTemplate(values, emit_async_series)
        async def dag_flow_early_sync_generator_terminal_async_generator(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For generator signature only; never run.
                yield _

        return apply_job(dag_flow_early_sync_generator_terminal_async_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [4, 6, 8]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='dag-flow-early-sync-generator-terminal-async-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-generator-terminal-sync-function',
    tags=['semantic-floor', 'dag-flow-early-async-generator'],
)
def case_dag_flow_early_async_generator_terminal_sync_function(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        def pass_values_through(values: AsyncGenerator) -> AsyncIterator[int]:
            return values

        @DagFlowTemplate(emit_async_values.refine(result_key='values'), pass_values_through)
        async def dag_flow_early_async_generator_terminal_sync_function(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For async-generator signature only; never run.
                yield _

        return apply_job(dag_flow_early_async_generator_terminal_sync_function, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        values = []
        async for value in result:
            values.append(value)
        assert values == [2, 3, 4]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='dag-flow-early-async-generator-terminal-sync-function',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='dag-flow-early-async-generator-terminal-sync-generator',
    tags=['semantic-floor', 'dag-flow-early-async-generator'],
)
def case_dag_flow_early_async_generator_terminal_sync_generator(  # noqa: C901
) -> ComposedFlowCase[[int], AsyncGenerator]:  # noqa: C901
    expected_callable_type = CallableType.ASYNC_GENERATOR

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        @TaskTemplate()
        async def emit_async_values(number: int) -> AsyncGenerator:
            for value in range(number, number + 3):
                await asyncio.sleep(0)
                yield value

        @TaskTemplate()
        def emit_sync_wrapped_values(values: AsyncGenerator) -> Generator:
            yield values

        @DagFlowTemplate(emit_async_values.refine(result_key='values'), emit_sync_wrapped_values)
        async def dag_flow_early_async_generator_terminal_sync_generator(
                number: int) -> AsyncGenerator:
            async for _ in Void():  # For async-generator signature only; never run.
                yield _

        return apply_job(dag_flow_early_async_generator_terminal_sync_generator, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        assert job.callable_type is expected_callable_type
        result = job(2)
        wrapped_values = []
        async for values in result:
            nested_values = []
            async for value in values:
                nested_values.append(value)
            wrapped_values.append(tuple(nested_values))
        assert wrapped_values == [(2, 3, 4)]
        assert_job_state(job, [RunState.FINISHED])

    return ComposedFlowCase[[int], AsyncGenerator](
        name='dag-flow-early-async-generator-terminal-sync-generator',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )


@pc.case(
    id='func-flow-nested-async-support-gap',
    tags=['semantic-floor', 'func-flow-nested-async-gap'],
)
def case_func_flow_nested_async_support_gap() -> ComposedFlowCase[[int], Awaitable[int]]:
    expected_callable_type = CallableType.ASYNC_COROUTINE

    def build_job(engine: IsEngine, registry: IsRunStateRegistry | None) -> IsFuncArgJob:
        # Tasks
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

        # Nested Async Child Flow
        @LinearFlowTemplate(add_one, wait_and_double)
        async def async_linear_grandchild(number: int) -> int:
            ...

        @FuncFlowTemplate()
        async def async_func_child(number: int) -> int:
            nested_result = await resolve(async_linear_grandchild(number))
            return await wait_and_add_ten(nested_result)

        # Func Parent Flow
        @FuncFlowTemplate()
        async def func_parent_nested_async(number: int) -> int:
            return await async_func_child(number)

        return apply_job(func_parent_nested_async, engine, registry)

    async def run_and_assert_results(job: IsFuncArgJob) -> None:
        # Compatibility probe: expected to pass on both engines; remove if stable.
        result = await resolve(job(4))

        assert result == 20
        assert_case_callable_type_and_finished_state(job, expected_callable_type)

    return ComposedFlowCase[[int], Awaitable[int]](
        name='func-flow-nested-async-support-gap',
        build_job_func=build_job,
        run_and_assert_results_func=run_and_assert_results,
        expected_callable_type=expected_callable_type,
    )
