"""Tests for job runner engines."""

import pytest
import pytest_cases as pc

from omnipy.shared.enums.job import JobType

from .helpers.classes import JobCase
from .helpers.functions import extract_engine, run_job_test


@pc.parametrize(
    'job_case', [pc.fixture_ref('power_mock_jobs_mock_runner_cls_no_verbose_no_reg')], ids=[''])
def test_job_runners_mock_job_no_verbose_no_reg_sync(job_case: JobCase) -> None:
    job = job_case.job
    assert job is not None

    for i in range(2):
        job_case.run_and_assert_results_func(job)

    engine = extract_engine(job)

    assert job.name == 'power'
    if job_case.job_type == JobType.TASK:
        assert len(engine.finished_backend_tasks) == 2  # type: ignore[attr-defined]
    else:
        assert len(engine.finished_backend_tasks) == 4  # type: ignore[attr-defined]

    for backend_task in engine.finished_backend_tasks:  # type: ignore[attr-defined]
        assert backend_task.backend_verbose is False


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('all_func_types_mock_jobs_mock_runner_cls_assert_runstate_mock_reg')],
    ids=[''])
@pytest.mark.asyncio
async def test_job_runners_mock_job_mock_runner_cls_assert_runstate_mock_reg(
        job_case: JobCase) -> None:
    job = job_case.job
    assert job is not None

    for i in range(2):
        await run_job_test(job_case)

    engine = extract_engine(job)

    if job_case.job_type == JobType.TASK:
        assert len(engine.finished_backend_tasks) == 2  # type: ignore[attr-defined]
    else:
        assert len(engine.finished_backend_tasks) == 4  # type: ignore[attr-defined]

    for backend_task in engine.finished_backend_tasks:  # type: ignore[attr-defined]
        assert backend_task.backend_verbose is True
