from typing import Callable, Type

import pytest_cases as pc

from omnipy.api.protocols.private.compute.job import IsJobTemplate
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.compute import IsFlowTemplate, IsTaskTemplate
from omnipy.api.protocols.public.engine import IsTaskRunnerEngine
from omnipy.engine.local import LocalRunner
from omnipy.modules.prefect.engine.prefect import PrefectEngine

from .helpers.classes import JobCase, JobRunnerStateChecker, JobType
from .helpers.functions import update_job_case_with_job
from .helpers.mocks import (MockDagFlowTemplate,
                            MockEngineConfig,
                            MockFuncFlowTemplate,
                            MockJobRunnerSubclass,
                            MockLinearFlowTemplate,
                            MockRunStateRegistry,
                            MockTaskTemplate)

# Mock job templates


@pc.fixture(scope='function')
@pc.parametrize(
    task_template_cls=[MockTaskTemplate],
    ids=['m[task]'],
)
def mock_task_template(task_template_cls):
    return task_template_cls


@pc.fixture(scope='function')
@pc.parametrize(
    flow_template_cls=[MockLinearFlowTemplate],
    ids=['m[linearflow]'],
)
def mock_linear_flow_template(flow_template_cls):
    return flow_template_cls


@pc.fixture(scope='function')
@pc.parametrize(
    flow_template_cls=[MockDagFlowTemplate],
    ids=['m[dagflow]'],
)
def mock_dag_flow_template(flow_template_cls):
    return flow_template_cls


@pc.fixture(scope='function')
@pc.parametrize(
    flow_template_cls=[MockFuncFlowTemplate],
    ids=['m[funcflow]'],
)
def mock_func_flow_template(flow_template_cls):
    return flow_template_cls


# Engine


@pc.fixture(scope='function')
@pc.parametrize(
    task_runner_subcls=[MockJobRunnerSubclass],
    ids=['m[task_runner]'],
)
def mock_task_runner_subcls(task_runner_subcls):
    return task_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize(
    linear_flow_runner_subcls=[MockJobRunnerSubclass],
    ids=['m[linearflow_runner]'],
)
def mock_linear_flow_runner_subcls(linear_flow_runner_subcls):
    return linear_flow_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize(
    dag_flow_runner_subcls=[MockJobRunnerSubclass],
    ids=['m[dagflow_runner]'],
)
def mock_dag_flow_runner_subcls(dag_flow_runner_subcls):
    return dag_flow_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize(
    func_flow_runner_subcls=[MockJobRunnerSubclass],
    ids=['m[funcflow_runner]'],
)
def mock_func_flow_runner_subcls(func_flow_runner_subcls):
    return func_flow_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize(engine=[LocalRunner(), PrefectEngine()], ids=['[local]', '[prefect]'])
def all_engines(engine):
    return engine


# Engine decorators


@pc.fixture(scope='function', name='assertstate')
def assert_runstate_engine_decorator():
    def decorate_engine_with_runstate_checker(engine: IsTaskRunnerEngine) -> IsTaskRunnerEngine:
        return JobRunnerStateChecker(engine)

    return decorate_engine_with_runstate_checker


@pc.fixture(scope='function', name='no_verbose')
def no_verbose_config_engine_decorator():
    def decorate_engine_with_no_verbose_config(engine: IsEngine) -> IsEngine:
        engine.set_config(MockEngineConfig(backend_verbose=False))
        return engine

    return decorate_engine_with_no_verbose_config


# RunStateRegistry


@pc.fixture(scope='function')
@pc.parametrize(
    registry=[MockRunStateRegistry()],
    ids=['m[registry]'],
)
def mock_registry(registry):
    return registry


@pc.fixture(scope='function')
@pc.parametrize(registry=[None], ids=['no_registry'])
def no_registry(registry):
    return registry


# JobType-related classes


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.task], ids=['task'])
@pc.parametrize('task_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('flow_template_cls', [None], ids=[''])
@pc.parametrize('job_runner_subcls', [pc.fixture_ref(mock_task_runner_subcls)], ids=[''])
def task_mock_classes(
    job_type: JobType,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    job_runner_subcls: Type[IsEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.linear_flow], ids=['linear_flow'])
@pc.parametrize('task_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('flow_template_cls', [pc.fixture_ref(mock_linear_flow_template)], ids=[''])
@pc.parametrize('job_runner_subcls', [pc.fixture_ref(mock_linear_flow_runner_subcls)], ids=[''])
def linear_flow_mock_classes(
    job_type: JobType,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    job_runner_subcls: Type[IsEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.dag_flow], ids=['dag_flow'])
@pc.parametrize('task_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('flow_template_cls', [pc.fixture_ref(mock_dag_flow_template)], ids=[''])
@pc.parametrize('job_runner_subcls', [pc.fixture_ref(mock_dag_flow_runner_subcls)], ids=[''])
def dag_flow_mock_classes(
    job_type: JobType,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    job_runner_subcls: Type[IsEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.func_flow], ids=['func_flow'])
@pc.parametrize('task_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('flow_template_cls', [pc.fixture_ref(mock_func_flow_template)], ids=[''])
@pc.parametrize('job_runner_subcls', [pc.fixture_ref(mock_func_flow_runner_subcls)], ids=[''])
def func_flow_mock_classes(
    job_type: JobType,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    job_runner_subcls: Type[IsEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_subcls


# test_job_runner


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.tasks', has_tag='power')
@pc.parametrize(
    'job_mock_classes', [
        task_mock_classes,
        linear_flow_mock_classes,
        dag_flow_mock_classes,
        func_flow_mock_classes,
    ],
    ids=['', '', '', ''])
@pc.parametrize('engine_decorator', [no_verbose_config_engine_decorator])
@pc.parametrize('registry', [no_registry], ids=[''])
def power_mock_jobs_mock_runner_subcls_no_verbose_no_reg(
    job_case: JobCase,
    job_mock_classes: tuple[JobType, Type[IsJobTemplate], Type[IsEngine]],
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    job_type, task_template_cls, flow_template_cls, job_runner_subcls = job_mock_classes
    return update_job_case_with_job(
        job_case,
        job_type,
        task_template_cls,
        flow_template_cls,
        job_runner_subcls(),
        engine_decorator,
        registry,
    )


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.tasks')
@pc.parametrize(
    'job_mock_classes', [
        task_mock_classes,
        linear_flow_mock_classes,
        dag_flow_mock_classes,
        func_flow_mock_classes,
    ],
    ids=['', '', '', ''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def all_func_types_mock_jobs_mock_runner_subcls_assert_runstate_mock_reg(
    job_case: JobCase,
    job_mock_classes: tuple[JobType, Type[IsJobTemplate], Type[IsEngine]],
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    job_type, task_template_cls, flow_template_cls, job_runner_subcls = job_mock_classes
    return update_job_case_with_job(
        job_case,
        job_type,
        task_template_cls,
        flow_template_cls,
        job_runner_subcls(),
        engine_decorator,
        registry,
    )


# test_all_engines


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.tasks')
@pc.parametrize(
    'job_classes', [
        task_mock_classes,
        linear_flow_mock_classes,
        dag_flow_mock_classes,
        func_flow_mock_classes,
    ],
    ids=['', '', '', ''])
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def all_func_types_mock_jobs_all_engines_assert_runstate_mock_reg(
    job_case: JobCase,
    job_classes: tuple[JobType, Type[IsJobTemplate], Type[IsEngine]],
    engine: Type[IsEngine],
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    job_type, task_template_cls, flow_template_cls, job_runner_subcls = job_classes

    return update_job_case_with_job(
        job_case,
        job_type,
        task_template_cls,
        flow_template_cls,
        engine,
        engine_decorator,
        registry,
    )
