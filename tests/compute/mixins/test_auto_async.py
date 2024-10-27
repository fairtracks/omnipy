import asyncio
from inspect import isawaitable, iscoroutine

import pytest
import pytest_cases as pc

from omnipy import TaskTemplate

from ..cases.raw.functions import async_sleep_random_time_func, sync_sleep_random_time_func


@pc.parametrize('async_task', [False, True], ids=['sync_task', 'async_task'])
def test_synchronously_run_task_with_auto_async(async_task: bool) -> None:
    task_func = async_sleep_random_time_func if async_task else sync_sleep_random_time_func

    _assert_synchronizity_of_task_without_auto_async_is_same_as_task_func(async_task, task_func)

    task_auto = TaskTemplate(auto_async=True)(task_func).apply()
    seconds_auto = task_auto()
    assert not isawaitable(seconds_auto)
    assert seconds_auto <= 0.1


@pc.parametrize('async_task', [False, True], ids=['sync_task', 'async_task'])
@pytest.mark.anyio
async def test_asynchronously_run_task_with_auto_async(async_task: bool) -> None:
    task_func = async_sleep_random_time_func if async_task else sync_sleep_random_time_func

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
    task_no_auto = TaskTemplate(auto_async=False)(task_func).apply()
    seconds_no_auto = task_no_auto()
    if async_task:
        assert iscoroutine(seconds_no_auto)
    else:
        assert not iscoroutine(seconds_no_auto)
        assert seconds_no_auto <= 0.1
