import pytest
import pytest_cases as pc

from ....engine.test_all_engines import test_flow_matrix_all_production_engines  # noqa
from ....engine.test_all_engines import \
    test_flow_matrix_all_production_engines_job_case  # type: ignore[attr-defined] # noqa
from ....engine.test_all_engines import \
    test_mock_tasks_all_engines_mock_registry_job_case  # type: ignore[attr-defined] # noqa
from ....engine.test_all_engines import \
    test_nested_flow_semantic_floor_all_production_engines  # noqa
from ....engine.test_all_engines import \
    test_nested_flow_semantic_floor_all_production_engines_job_case  # type: ignore[attr-defined] # noqa
from ....engine.test_all_engines import test_mock_tasks_all_engines_mock_registry

test_mock_tasks_all_engines_mock_registry  # noqa
test_flow_matrix_all_production_engines  # noqa
test_nested_flow_semantic_floor_all_production_engines  # noqa


@pc.parametrize(
    'job_case',
    [pc.fixture_ref('base_task_only_real_jobs_all_engines_real_reg')],
    ids=[''],
)
@pytest.mark.asyncio
async def test_basic_task_cases_all_engines_task_only(job_case):
    from ....engine.helpers.functions import run_job_test

    await run_job_test(job_case)
