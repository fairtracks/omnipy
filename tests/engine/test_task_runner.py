import pytest
import pytest_cases as pc

from .helpers.classes import JobCase
from .helpers.functions import extract_engine, run_job_test


@pc.parametrize(
    'job_case', [pc.fixture_ref('power_mock_job_mock_runner_subcls_no_verbose_no_reg')], ids=[''])
def test_job_runners_mock_job_no_verbose_no_reg_sync(job_case: JobCase) -> None:
    job = job_case.job

    for i in range(2):
        job_case.run_and_assert_results_func(job)

    engine = extract_engine(job)

    assert job.name == 'power'
    assert len(engine.finished_backend_tasks) == 2
    for backend_task in engine.finished_backend_tasks:
        assert backend_task.backend_verbose is False


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('all_func_types_mock_job_mock_runner_subcls_assert_runstate_mock_reg')],
    ids=[''])
@pytest.mark.asyncio
async def test_job_runners_mock_job_mock_runner_subcls_assert_runstate_mock_reg(
        job_case: JobCase) -> None:
    job = job_case.job

    for i in range(2):
        await run_job_test(job_case)

    engine = extract_engine(job)

    assert len(engine.finished_backend_tasks) == 2
    for backend_task in engine.finished_backend_tasks:
        assert backend_task.backend_verbose is True
