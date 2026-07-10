"""Tests for cross-engine behavior."""

import pytest
import pytest_cases as pc

from .helpers.classes import ComposedFlowCase, JobCase
from .helpers.functions import run_job_test


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('all_func_types_mock_jobs_all_engines_assert_runstate_mock_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_mock_tasks_all_engines_mock_registry(job_case: JobCase) -> None:
    """Test mock tasks all engines mock registry."""
    await run_job_test(job_case)


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('all_flow_matrix_cases_all_engines_assert_runstate_mock_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_flow_matrix_all_production_engines(job_case: ComposedFlowCase) -> None:
    await run_job_test(job_case)


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_nested_flow_semantic_floor_all_production_engines(
    job_case: ComposedFlowCase,
) -> None:
    await run_job_test(job_case)
