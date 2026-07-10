"""Shared fixtures for integration reused engine tests."""

from typing import Annotated, Callable, Type

import pytest
import pytest_cases as pc

from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.hub._registry import RunStateRegistry
from omnipy.shared.enums.job import JobType
from omnipy.shared.protocols.compute.job import (IsDagFlowTemplate,
                                                 IsFuncFlowTemplate,
                                                 IsLinearFlowTemplate,
                                                 IsTaskTemplate)
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry

from ....engine.conftest import all_flow_matrix_cases_all_engines_assert_runstate_mock_reg  # noqa
from ....engine.conftest import \
    all_flow_matrix_cases_all_engines_assert_runstate_mock_reg_engine  # type: ignore[attr-defined] # noqa
from ....engine.conftest import \
    all_flow_matrix_cases_all_engines_assert_runstate_mock_reg_engine_decorator  # type: ignore[attr-defined] # noqa
from ....engine.conftest import \
    all_flow_matrix_cases_all_engines_assert_runstate_mock_reg_registry  # type: ignore[attr-defined] # noqa
from ....engine.conftest import assert_runstate_engine_decorator  # noqa
from ....engine.conftest import mock_registry  # noqa
from ....engine.conftest import \
    nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg  # noqa
from ....engine.conftest import \
    nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg_engine  # type: ignore[attr-defined] # noqa
from ....engine.conftest import \
    nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg_engine_decorator  # type: ignore[attr-defined] # noqa
from ....engine.conftest import \
    nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg_registry  # type: ignore[attr-defined] # noqa
from ....engine.conftest import all_engines
from ....engine.helpers.classes import JobCase
from ....engine.helpers.functions import update_job_case_with_job


@pc.fixture(scope='function')
@pc.parametrize(
    'job_type', [JobType.TASK, JobType.LINEAR_FLOW, JobType.DAG_FLOW, JobType.FUNC_FLOW],
    ids=['task', 'linear_flow', 'dag_flow', 'func_flow'])
@pc.parametrize('task_template_cls', [TaskTemplate], ids=[''])
@pc.parametrize('linear_flow_template_cls', [LinearFlowTemplate], ids=[''])
@pc.parametrize('dag_flow_template_cls', [DagFlowTemplate], ids=[''])
@pc.parametrize('func_flow_template_cls', [FuncFlowTemplate], ids=[''])
def all_job_classes(
    job_type: JobType.Literals,
    task_template_cls: Type[IsTaskTemplate],
    linear_flow_template_cls: Type[IsLinearFlowTemplate],
    dag_flow_template_cls: Type[IsDagFlowTemplate],
    func_flow_template_cls: Type[IsFuncFlowTemplate],
):
    """Provide all job classes."""
    return (job_type,
            task_template_cls,
            linear_flow_template_cls,
            dag_flow_template_cls,
            func_flow_template_cls)


@pc.fixture(scope='function', name='plain_engine')
@pc.parametrize(engine_decorator=[None], ids=[''])
def no_engine_decorator(engine_decorator):
    """Provide no engine decorator."""
    return engine_decorator


@pc.fixture(scope='function')
@pc.parametrize(
    registry_cls=[RunStateRegistry],
    ids=['registry'],
)
def run_state_registry(
    runtime: Annotated[None, pytest.fixture],
    registry_cls: Type[IsRunStateRegistry],
):
    """Provide run state registry."""
    return registry_cls()


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='....engine.cases.tasks')
@pc.parametrize('job_classes', [all_job_classes], ids=[''])
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [no_engine_decorator])
@pc.parametrize('registry', [run_state_registry], ids=[''])
def all_func_types_real_jobs_all_engines_real_reg(
    job_case: JobCase,
    job_classes: tuple[JobType.Literals,
                       Type[IsTaskTemplate],
                       Type[IsLinearFlowTemplate],
                       Type[IsDagFlowTemplate],
                       Type[IsFuncFlowTemplate]],
    engine: IsEngine,
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    """Provide all func types real jobs all engines real reg."""
    (job_type,
     task_template_cls,
     linear_flow_template_cls,
     dag_flow_template_cls,
     func_flow_template_cls) = job_classes

    if job_type == JobType.LINEAR_FLOW:
        flow_template_cls = linear_flow_template_cls
    elif job_type == JobType.DAG_FLOW:
        flow_template_cls = dag_flow_template_cls
    elif job_type == JobType.FUNC_FLOW:
        flow_template_cls = func_flow_template_cls
    else:
        flow_template_cls = None

    return update_job_case_with_job(
        job_case,
        job_type,
        task_template_cls,
        flow_template_cls,
        engine,
        engine_decorator,
        registry,
    )


all_func_types_mock_jobs_all_engines_assert_runstate_mock_reg = \
    all_func_types_real_jobs_all_engines_real_reg
