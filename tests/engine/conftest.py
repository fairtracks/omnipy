from io import StringIO
import logging
from typing import Annotated, Callable, cast, Optional, Tuple, Type

import pytest
import pytest_cases as pc

from unifair.engine.local import LocalRunner
from unifair.engine.prefect import PrefectEngine
from unifair.engine.protocols import (IsEngine,
                                      IsFlowTemplate,
                                      IsJobTemplate,
                                      IsRunStateRegistry,
                                      IsTaskRunnerEngine,
                                      IsTaskTemplate)

from .helpers.classes import JobCase, JobRunnerStateChecker, JobType
from .helpers.functions import add_logger_to_registry, update_job_case_with_job
from .helpers.mocks import (MockDagFlow,
                            MockDagFlowTemplate,
                            MockEngineConfig,
                            MockFuncFlowTemplate,
                            MockJobRunnerSubclass,
                            MockRunStateRegistry,
                            MockTask,
                            MockTaskTemplate)

# JobTemplate subclasses


@pc.fixture(scope='function')
@pc.parametrize(
    task_template_cls=[MockTaskTemplate],
    ids=['m[task]'],
)
def mock_task_template(task_template_cls):
    return task_template_cls


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
    return cast(MockRunStateRegistry, add_logger_to_registry(registry))


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
    flow_template_cls: Optional[Type[IsFlowTemplate]],
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
    flow_template_cls: Optional[Type[IsFlowTemplate]],
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
    flow_template_cls: Optional[Type[IsFlowTemplate]],
    job_runner_subcls: Type[IsEngine],
):
    return job_type, task_template_cls, flow_template_cls, job_runner_subcls


# test_job_runner


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.tasks', has_tag='power')
@pc.parametrize(
    'job_mock_classes', [
        task_mock_classes,
        dag_flow_mock_classes,
        func_flow_mock_classes,
    ],
    ids=['', '', ''])
@pc.parametrize('engine_decorator', [no_verbose_config_engine_decorator])
@pc.parametrize('registry', [no_registry], ids=[''])
def power_mock_jobs_mock_runner_subcls_no_verbose_no_reg(
    job_case: JobCase,
    job_mock_classes: Tuple[JobType, Type[IsJobTemplate], Type[IsEngine]],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
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
        dag_flow_mock_classes,
        func_flow_mock_classes,
    ],
    ids=['', '', ''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def all_func_types_mock_jobs_mock_runner_subcls_assert_runstate_mock_reg(
    job_case: JobCase,
    job_mock_classes: Tuple[JobType, Type[IsJobTemplate], Type[IsEngine]],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
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
        dag_flow_mock_classes,
        func_flow_mock_classes,
    ],
    ids=['', '', ''])
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def all_func_types_mock_jobs_all_engines_assert_runstate_mock_reg(
    job_case: JobCase,
    job_classes: Tuple[JobType, Type[IsJobTemplate], Type[IsEngine]],
    engine: Type[IsEngine],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
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


# test_registry


@pytest.fixture(scope='function')
def str_stream() -> StringIO:
    return StringIO()


@pytest.fixture(scope='function')
def simple_logger() -> logging.Logger:
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    yield logger
    for handler in logger.handlers:
        logger.removeHandler(handler)


@pytest.fixture(scope='function')
def stream_logger(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
) -> logging.Logger:
    stream_handler = logging.StreamHandler(str_stream)
    simple_logger.addHandler(stream_handler)
    yield simple_logger
    simple_logger.removeHandler(stream_handler)


@pytest.fixture(scope='module')
def task_template_a() -> MockTaskTemplate:
    MockTaskTemplate.job_creator.engine = MockJobRunnerSubclass()

    @MockTaskTemplate(name='a')
    def concat_a(s: str) -> str:
        return s + 'a'

    return concat_a


@pytest.fixture(scope='module')
def task_template_b() -> MockTaskTemplate:
    MockTaskTemplate.job_creator.engine = MockJobRunnerSubclass()

    @MockTaskTemplate(name='b')
    def concat_b(s: str) -> str:
        return s + 'b'

    return concat_b


@pytest.fixture(scope='module')
def task_a(task_template_a) -> MockTask:
    return task_template_a.apply()


@pytest.fixture(scope='module')
def task_b(task_template_b) -> MockTask:
    return task_template_b.apply()


@pytest.fixture(scope='module')
def dag_flow_a(task_template_a, task_template_b) -> MockDagFlow:
    @MockDagFlowTemplate(task_template_a, task_template_b, name='a')
    def concat_a(s: str) -> str:
        ...

    return concat_a.apply()


@pytest.fixture(scope='module')
def dag_flow_b(task_template_a, task_template_b) -> MockDagFlow:
    @MockDagFlowTemplate(task_template_a, task_template_b, name='b')
    def concat_b(s: str) -> str:
        ...

    return concat_b.apply()
