# mypy: disable-error-code="attr-defined"
# pyright: reportAttributeAccessIssue=false
import pytest
import pytest_cases as pc

from ....engine.test_all_engines import (
    test_flow_matrix_all_production_engines,
    test_flow_matrix_all_production_engines_job_case,
    test_mock_tasks_all_engines_mock_registry,
    test_mock_tasks_all_engines_mock_registry_job_case,
    test_nested_flow_semantic_floor_all_production_engines,
    test_nested_flow_semantic_floor_all_production_engines_job_case,
)

__all__ = [
    'test_flow_matrix_all_production_engines',
    'test_flow_matrix_all_production_engines_job_case',
    'test_mock_tasks_all_engines_mock_registry',
    'test_mock_tasks_all_engines_mock_registry_job_case',
    'test_nested_flow_semantic_floor_all_production_engines',
    'test_nested_flow_semantic_floor_all_production_engines_job_case',
]


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('base_task_only_real_jobs_all_engines_real_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_basic_task_cases_all_engines_task_only(job_case):
    from ....engine.helpers.functions import run_job_test

    await run_job_test(job_case)
