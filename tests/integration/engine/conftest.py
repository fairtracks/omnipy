from typing import Callable, Optional, Tuple, Type

import pytest_cases as pc

from unifair.compute.flow import DagFlowTemplate, FuncFlowTemplate
from unifair.compute.task import TaskTemplate
from unifair.engine.protocols import (IsDagFlowTemplate,
                                      IsEngine,
                                      IsFuncFlowTemplate,
                                      IsJobTemplate,
                                      IsRunStateRegistry,
                                      IsTaskTemplate)
from unifair.engine.registry import RunStateRegistry

from ...engine.conftest import all_engines
from ...engine.helpers.classes import JobCase, JobType
from ...engine.helpers.functions import update_job_case_with_job


@pc.fixture(scope='function')
@pc.parametrize(
    'job_type', [JobType.task, JobType.dag_flow, JobType.func_flow],
    ids=['task', 'dag_flow', 'func_flow'])
@pc.parametrize('task_template_cls', [TaskTemplate], ids=[''])
@pc.parametrize('dag_flow_template_cls', [DagFlowTemplate], ids=[''])
@pc.parametrize('func_flow_template_cls', [FuncFlowTemplate], ids=[''])
def all_job_classes(
    job_type: JobType,
    task_template_cls: Type[IsTaskTemplate],
    dag_flow_template_cls: Type[IsDagFlowTemplate],
    func_flow_template_cls: Type[IsFuncFlowTemplate],
):
    return job_type, task_template_cls, dag_flow_template_cls, func_flow_template_cls


@pc.fixture(scope='function', name='plain_engine')
@pc.parametrize(engine_decorator=[None], ids=[''])
def no_engine_decorator(engine_decorator):
    return engine_decorator


@pc.fixture(scope='function')
@pc.parametrize(
    registry=[RunStateRegistry()],
    ids=['registry'],
)
def run_state_registry(registry):
    return registry


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='...engine.cases.tasks')
@pc.parametrize('job_classes', [all_job_classes], ids=[''])
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [no_engine_decorator])
@pc.parametrize('registry', [run_state_registry], ids=[''])
def all_func_types_real_jobs_all_engines_real_reg(
    job_case: JobCase,
    job_classes: Tuple[JobType, Type[IsJobTemplate]],
    engine: Type[IsEngine],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
):
    job_type, task_template_cls, dag_flow_template_cls, func_flow_template_cls = job_classes

    # TODO: Fix job_type comparisons everywhere (bug due to pytest.fixture?)
    if job_type.value == JobType.dag_flow.value:
        flow_template_cls = dag_flow_template_cls
    elif job_type.value == JobType.func_flow.value:
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
