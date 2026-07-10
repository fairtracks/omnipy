"""Shared fixtures for engine tests."""

from typing import Callable, Type

import pytest
import pytest_cases as pc

from omnipy.components.prefect.engine.prefect import PrefectEngine
from omnipy.components.prefect.lazy_import import prefect_test_harness
from omnipy.engine.local import LocalRunner
from omnipy.shared.enums.job import JobType
from omnipy.shared.protocols.compute.job import IsFlowTemplate, IsTaskTemplate
from omnipy.shared.protocols.engine.job_runner import IsJobRunnerEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry

from .helpers.classes import ComposedFlowCase, JobCase, JobRunnerStateChecker
from .helpers.functions import apply_composed_flow_case, update_job_case_with_job
from .helpers.mocks import (MockDagFlowTemplate,
                            MockEngineConfig,
                            MockFuncFlowTemplate,
                            MockJobRunnerSubclass,
                            MockLinearFlowTemplate,
                            MockRunStateRegistry,
                            MockTaskTemplate)

# Prefect


@pytest.fixture(autouse=True, scope='package')
def prefect_test_fixture():
    with prefect_test_harness():
        yield


# Mock job templates


@pc.fixture(scope='function')
@pc.parametrize(
    task_template_cls=[MockTaskTemplate],
    ids=['m[task]'],
)
def mock_task_template(task_template_cls):
    """Provide the mock task template fixture."""
    return task_template_cls


@pc.fixture(scope='function')
@pc.parametrize(
    flow_template_cls=[MockLinearFlowTemplate],
    ids=['m[linearflow]'],
)
def mock_linear_flow_template(flow_template_cls):
    """Provide the mock linear flow template fixture."""
    return flow_template_cls


@pc.fixture(scope='function')
@pc.parametrize(
    flow_template_cls=[MockDagFlowTemplate],
    ids=['m[dagflow]'],
)
def mock_dag_flow_template(flow_template_cls):
    """Provide the mock dag flow template fixture."""
    return flow_template_cls


@pc.fixture(scope='function')
@pc.parametrize(
    flow_template_cls=[MockFuncFlowTemplate],
    ids=['m[funcflow]'],
)
def mock_func_flow_template(flow_template_cls):
    """Provide the mock func flow template fixture."""
    return flow_template_cls


# Engine


@pc.fixture(scope='function')
@pc.parametrize(
    task_job_runner_cls=[MockJobRunnerSubclass],
    ids=['m[task_runner]'],
)
def mock_task_job_runner_cls(task_job_runner_cls):
    return task_job_runner_cls


@pc.fixture(scope='function')
@pc.parametrize(
    linear_flow_job_runner_cls=[MockJobRunnerSubclass],
    ids=['m[linearflow_runner]'],
)
def mock_linear_flow_job_runner_cls(linear_flow_job_runner_cls):
    return linear_flow_job_runner_cls


@pc.fixture(scope='function')
@pc.parametrize(
    dag_flow_job_runner_cls=[MockJobRunnerSubclass],
    ids=['m[dagflow_runner]'],
)
def mock_dag_flow_job_runner_cls(dag_flow_job_runner_cls):
    return dag_flow_job_runner_cls


@pc.fixture(scope='function')
@pc.parametrize(
    func_flow_job_runner_cls=[MockJobRunnerSubclass],
    ids=['m[funcflow_runner]'],
)
def mock_func_flow_job_runner_cls(func_flow_job_runner_cls):
    return func_flow_job_runner_cls


@pc.fixture(scope='function')
@pc.parametrize(engine=[LocalRunner(), PrefectEngine()], ids=['[local]', '[prefect]'])
def all_engines(engine) -> IsJobRunnerEngine:
    return engine


# Engine decorators


@pc.fixture(scope='function', name='assertstate')
def assert_runstate_engine_decorator():
    def decorate_engine_with_runstate_checker(engine: IsJobRunnerEngine) -> IsJobRunnerEngine:
        return JobRunnerStateChecker(engine)

    return decorate_engine_with_runstate_checker


@pc.fixture(scope='function', name='no_verbose')
def no_verbose_config_engine_decorator():
    def decorate_engine_with_no_verbose_config(engine: IsJobRunnerEngine) -> IsJobRunnerEngine:
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
    """Provide the mock registry fixture."""
    return registry


@pc.fixture(scope='function')
@pc.parametrize(registry=[None], ids=['no_registry'])
def no_registry(registry):
    """Provide the no registry fixture."""
    return registry


# JobType-related classes


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.TASK], ids=['task'])
@pc.parametrize('task_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('flow_template_cls', [None], ids=[''])
@pc.parametrize('job_runner_cls', [pc.fixture_ref(mock_task_job_runner_cls)], ids=[''])
def task_mock_classes(
    job_type: JobType.Literals,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    job_runner_cls: Type[IsJobRunnerEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_cls


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.LINEAR_FLOW], ids=['linear_flow'])
@pc.parametrize('task_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('flow_template_cls', [pc.fixture_ref(mock_linear_flow_template)], ids=[''])
@pc.parametrize('job_runner_cls', [pc.fixture_ref(mock_linear_flow_job_runner_cls)], ids=[''])
def linear_flow_mock_classes(
    job_type: JobType.Literals,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    job_runner_cls: Type[IsJobRunnerEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_cls


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.DAG_FLOW], ids=['dag_flow'])
@pc.parametrize('task_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('flow_template_cls', [pc.fixture_ref(mock_dag_flow_template)], ids=[''])
@pc.parametrize('job_runner_cls', [pc.fixture_ref(mock_dag_flow_job_runner_cls)], ids=[''])
def dag_flow_mock_classes(
    job_type: JobType.Literals,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    job_runner_cls: Type[IsJobRunnerEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_cls


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.FUNC_FLOW], ids=['func_flow'])
@pc.parametrize('task_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('flow_template_cls', [pc.fixture_ref(mock_func_flow_template)], ids=[''])
@pc.parametrize('job_runner_cls', [pc.fixture_ref(mock_func_flow_job_runner_cls)], ids=[''])
def func_flow_mock_classes(
    job_type: JobType.Literals,
    task_template_cls: Type[IsTaskTemplate],
    flow_template_cls: Type[IsFlowTemplate] | None,
    job_runner_cls: Type[IsJobRunnerEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_cls


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
def power_mock_jobs_mock_runner_cls_no_verbose_no_reg(
    job_case: JobCase,
    job_mock_classes: tuple[
        JobType.Literals,
        Type[IsTaskTemplate],
        Type[IsFlowTemplate],
        Type[IsJobRunnerEngine],
    ],
    engine_decorator: Callable[[IsJobRunnerEngine], IsJobRunnerEngine] | None,
    registry: IsRunStateRegistry | None,
):
    job_type, task_template_cls, flow_template_cls, job_runner_cls = job_mock_classes
    return update_job_case_with_job(
        job_case,
        job_type,
        task_template_cls,
        flow_template_cls,
        job_runner_cls(),
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
def all_func_types_mock_jobs_mock_runner_cls_assert_runstate_mock_reg(
    job_case: JobCase,
    job_mock_classes: tuple[
        JobType.Literals,
        Type[IsTaskTemplate],
        Type[IsFlowTemplate],
        Type[IsJobRunnerEngine],
    ],
    engine_decorator: Callable[[IsJobRunnerEngine], IsJobRunnerEngine] | None,
    registry: IsRunStateRegistry | None,
):
    job_type, task_template_cls, flow_template_cls, job_runner_cls = job_mock_classes
    return update_job_case_with_job(
        job_case,
        job_type,
        task_template_cls,
        flow_template_cls,
        job_runner_cls(),
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
    job_classes: tuple[
        JobType.Literals,
        Type[IsTaskTemplate],
        Type[IsFlowTemplate],
        Type[IsJobRunnerEngine],
    ],
    engine: IsJobRunnerEngine,
    engine_decorator: Callable[[IsJobRunnerEngine], IsJobRunnerEngine] | None,
    registry: IsRunStateRegistry | None,
):
    job_type, task_template_cls, flow_template_cls, _job_runner_cls = job_classes

    return update_job_case_with_job(
        job_case,
        job_type,
        task_template_cls,
        flow_template_cls,
        engine,
        engine_decorator,
        registry,
    )


@pc.fixture(scope='function')
@pc.parametrize_with_cases(
    'job_case',
    cases='.cases.flows',
    has_tag='matrix',
)
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def all_flow_matrix_cases_all_engines_assert_runstate_mock_reg(
    job_case: ComposedFlowCase,
    engine: IsEngine,
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    if engine_decorator:
        engine = engine_decorator(engine)
    apply_composed_flow_case(job_case, engine, registry)
    return job_case


@pc.fixture(scope='function')
@pc.parametrize_with_cases(
    'job_case',
    cases='.cases.flows',
    has_tag='semantic-floor',
)
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def nested_flow_semantic_floor_cases_all_engines_assert_runstate_mock_reg(
    job_case: ComposedFlowCase,
    engine: IsEngine,
    engine_decorator: Callable[[IsEngine], IsEngine] | None,
    registry: IsRunStateRegistry | None,
):
    if engine_decorator:
        engine = engine_decorator(engine)
    apply_composed_flow_case(job_case, engine, registry)
    return job_case
