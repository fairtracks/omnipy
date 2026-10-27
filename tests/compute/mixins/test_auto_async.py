"""Test auto_async task mixin behavior."""

import asyncio
from collections.abc import AsyncGenerator, Callable, Coroutine
from inspect import isawaitable, iscoroutine
from typing import Annotated, Any, TypeAlias

import pytest
import pytest_cases as pc

from omnipy import FuncFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.shared.protocols.compute.job import IsJobTemplate

from ..cases.raw.functions import async_sleep_random_time_func, sync_sleep_random_time_func

ReturnFloatCallable: TypeAlias = Callable[[], float | Coroutine[Any, Any, float]]


@pc.parametrize('async_task', [False, True], ids=['sync_task', 'async_task'])
def test_synchronously_run_task_with_auto_async(async_task: bool) -> None:
    task_func: ReturnFloatCallable = (
        async_sleep_random_time_func if async_task else sync_sleep_random_time_func
    )
    _assert_synchronizity_of_task_without_auto_async_is_same_as_task_func(async_task, task_func)

    task_auto = TaskTemplate(auto_async=True)(task_func).apply()
    seconds_auto: float | Coroutine[Any, Any, float] = task_auto()
    assert not isawaitable(seconds_auto)
    assert seconds_auto <= 0.1


@pc.parametrize('async_task', [False, True], ids=['sync_task', 'async_task'])
@pytest.mark.anyio
async def test_asynchronously_run_task_with_auto_async(async_task: bool) -> None:
    task_func: ReturnFloatCallable = (
        async_sleep_random_time_func if async_task else sync_sleep_random_time_func
    )

    _assert_synchronizity_of_task_without_auto_async_is_same_as_task_func(async_task, task_func)

    task_auto = TaskTemplate(auto_async=True)(task_func).apply()
    seconds_auto = task_auto()
    if async_task:
        assert isinstance(seconds_auto, asyncio.Task)
        assert await seconds_auto <= 0.1
    else:
        assert not isawaitable(seconds_auto)
        assert seconds_auto <= 0.1


def _assert_synchronizity_of_task_without_auto_async_is_same_as_task_func(async_task, task_func):
    """Assert non-auto_async tasks preserve callable synchrony."""
    task_no_auto = TaskTemplate(auto_async=False)(task_func).apply()
    seconds_no_auto = task_no_auto()
    if async_task:
        assert iscoroutine(seconds_no_auto)
    else:
        assert not iscoroutine(seconds_no_auto)
        assert seconds_no_auto <= 0.1


@pc.fixture(scope='function')
@pc.parametrize('auto_async', [False, True])
@pc.parametrize('is_flow', [False, True], ids=['task', 'flow'])
def numbers_template(auto_async: bool, is_flow: bool) -> IsJobTemplate:

    async def numbers() -> AsyncGenerator[int, None]:
        for number in range(3):
            yield number

    if is_flow:
        return FuncFlowTemplate(auto_async=auto_async)(numbers)
    else:
        return TaskTemplate(auto_async=auto_async)(numbers)


async def _consume(stream: AsyncGenerator[int, None]) -> list[int]:
    return [number async for number in stream]


def test_async_generator_auto_async_without_running_loop(
    numbers_template: Annotated[IsJobTemplate, pc.fixture],
) -> None:
    stream = numbers_template.run()
    assert asyncio.run(_consume(stream)) == [0, 1, 2]


@pytest.mark.anyio
async def test_async_generator_auto_async_with_running_loop(
    numbers_template: Annotated[IsJobTemplate, pc.fixture],
) -> None:
    stream = numbers_template.run()
    assert await _consume(stream) == [0, 1, 2]
