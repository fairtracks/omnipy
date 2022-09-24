import pytest
import pytest_cases as pc

from engine.helpers.functions import assert_task_state
from unifair.engine.constants import RunState


@pc.parametrize(
    'task_case',
    [
        pc.fixture_ref('sync_function_task_all_engines_mock_rest'),
        pc.fixture_ref('sync_coroutine_task_all_engines_mock_rest')
    ],
    ids=['sync-function', 'sync-coroutine'])
def test_sync_tasks_all_engines_mock_rest(task_case) -> None:
    task, args, kwargs, assert_result = task_case
    result = task(*args, **kwargs)
    assert_result(task, result)
    assert_task_state(task, RunState.FINISHED)


@pc.parametrize(
    'task_case',
    [
        pc.fixture_ref('async_function_task_all_engines_mock_rest'),
        pc.fixture_ref('async_coroutine_task_all_engines_mock_rest')
    ],
    ids=['async-function', 'async-coroutine'])
@pytest.mark.asyncio
async def test_async_tasks_all_engines_mock_rest(task_case) -> None:
    task, args, kwargs, assert_result = task_case
    result = task(*args, **kwargs)
    await assert_result(task, result)
    assert_task_state(task, RunState.FINISHED)
