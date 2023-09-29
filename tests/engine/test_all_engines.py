import os

import pytest
import pytest_cases as pc

from .helpers.classes import JobCase
from .helpers.functions import run_job_test


@pytest.mark.skipif(
    os.getenv('OMNIPY_FORCE_SKIPPED_TEST') != '1',
    reason="""
TODO: Stopped working in some Prefect version between 2.10.10 and 2.13.3
""")
@pc.parametrize(
    'job_case',
    [pc.fixture_ref('all_func_types_mock_jobs_all_engines_assert_runstate_mock_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_mock_tasks_all_engines_mock_registry(job_case: JobCase) -> None:
    await run_job_test(job_case)
