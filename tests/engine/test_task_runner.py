import pytest
import pytest_cases as pc

from .helpers.functions import extract_engine, run_task_test


@pc.parametrize(
    'task_case',
    [pc.fixture_ref('power_mock_task_mock_taskrun_subcls_config_no_verbose_reg')],
    ids=[''],
)
def test_task_runner_mock_task_mock_engine_config_no_verbose_reg_sync(task_case) -> None:
    task, run_and_assert_results = task_case

    for i in range(2):
        run_and_assert_results(task)

    engine = extract_engine(task)

    assert task.name == 'power'
    assert len(engine.finished_backend_tasks) == 2
    for backend_task in engine.finished_backend_tasks:
        assert backend_task.backend_verbose is False


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
    for i in range(2):
        await run_task_test(task_case)

    task, _run_and_assert_results = task_case
    engine = extract_engine(task)

    assert len(engine.finished_backend_tasks) == 2
    for backend_task in engine.finished_backend_tasks:
        assert backend_task.backend_verbose is True
