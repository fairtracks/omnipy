import pytest
import pytest_cases as pc

from .helpers.functions import run_task_test


@pc.parametrize(
    'task_case',
    [pc.fixture_ref('power_mock_task_mock_taskrun_subcls_with_backend_no_reg')],
    ids=[''],
)
def test_task_runner_mock_task_mock_engine_backend_verbose_no_reg_sync(task_case) -> None:
    task, run_and_assert_results = task_case
    run_and_assert_results(task)

    assert task.name == 'power'
    assert task.engine.backend_task.backend_verbose is False
    assert task.engine.backend_task.finished


@pc.parametrize(
    'task_case',
    [
        pc.fixture_ref('singlethread_mock_task_mock_taskrun_subcls_mock_reg'),
        pc.fixture_ref('multithread_mock_task_mock_taskrun_subcls_mock_reg'),
        pc.fixture_ref('multiprocess_mock_task_mock_taskrun_subcls_mock_reg')
    ],
    ids=['single', 'multithread', 'multiprocess'],
)
@pytest.mark.asyncio
async def test_task_runner_mock_task_mock_engine_mock_reg(task_case) -> None:
    await run_task_test(task_case)
