import pytest
import pytest_cases as pc

from .helpers.functions import run_task_test


@pc.parametrize(
    'task_case',
    [
        pc.fixture_ref('singlethread_mock_task_all_engines_mock_reg'),
        pc.fixture_ref('multithread_mock_task_all_engines_mock_reg'),
        pc.fixture_ref('multiprocess_mock_task_all_engines_mock_reg')
    ],
    ids=['single', 'multithread', 'multiprocess'],
)
@pytest.mark.asyncio
async def test_mock_tasks_all_engines_mock_registry(task_case) -> None:
    await run_task_test(task_case)
