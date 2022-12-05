from io import StringIO
import logging
from typing import Annotated, Callable, cast, Optional, Tuple, Type

import pytest
import pytest_cases as pc

from unifair.compute.task import TaskTemplate
from unifair.engine.local import LocalRunner
from unifair.engine.prefect import PrefectEngine
from unifair.engine.protocols import IsEngine, IsJobTemplate, IsRunStateRegistry, IsTaskRunnerEngine

from .helpers.classes import JobCase, JobType, TaskRunnerStateChecker
from .helpers.functions import add_logger_to_registry, update_job_case_with_job
from .helpers.mocks import (MockEngineConfig,
                            MockRunStateRegistry,
                            MockTask,
                            MockTaskRunnerSubclass,
                            MockTaskTemplate)

# JobTemplate subclasses


@pc.fixture(scope='function')
@pc.parametrize(
    task_template_cls=[MockTaskTemplate],
    ids=['m[task]'],
)
def mock_task_template(task_template_cls):
    return task_template_cls


# Engine


@pc.fixture(scope='function')
@pc.parametrize(
    task_runner_subcls=[MockTaskRunnerSubclass],
    ids=['m[taskrunner]'],
)
def mock_task_runner_subcls(task_runner_subcls):
    return task_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize(engine=[LocalRunner(), PrefectEngine()], ids=['[local]', '[prefect]'])
def all_engines(engine):
    return engine


# Engine decorators


@pc.fixture(scope='function', name='assertstate')
def assert_runstate_engine_decorator():
    def decorate_engine_with_runstate_checker(engine: IsTaskRunnerEngine) -> IsTaskRunnerEngine:
        return TaskRunnerStateChecker(engine)

    return decorate_engine_with_runstate_checker


@pc.fixture(scope='function', name='no_verbose')
def no_verbose_config_engine_decorator():
    def decorate_engine_with_no_verbose_config(engine: IsEngine) -> IsEngine:
        engine.set_config(MockEngineConfig(backend_verbose=False))
        return engine

    return decorate_engine_with_no_verbose_config


@pc.fixture(scope='function', name='')
@pc.parametrize(engine_decorator=[None], ids=[''])
def no_engine_decorator(engine_decorator):
    return engine_decorator


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
@pc.parametrize('job_type', [JobType.task])
@pc.parametrize('job_template_cls', [pc.fixture_ref(mock_task_template)], ids=[''])
@pc.parametrize('job_runner_subcls', [pc.fixture_ref(mock_task_runner_subcls)], ids=[''])
def task_mock_classes(job_type: JobType,
                      job_template_cls: Type[IsJobTemplate],
                      job_runner_subcls: Type[IsEngine]):
    return job_type, job_template_cls, job_runner_subcls


@pc.fixture(scope='function')
@pc.parametrize('job_type', [JobType.task])
@pc.parametrize('job_template_cls', [TaskTemplate], ids=[''])
def all_job_classes(job_type: JobType, job_template_cls: Tuple[JobType, Type[IsJobTemplate]]):
    return job_type, job_template_cls


# test_job_runner


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.tasks', has_tag='power')
@pc.parametrize('job_mock_classes', [task_mock_classes], ids=[''])
@pc.parametrize('engine_decorator', [no_verbose_config_engine_decorator])
@pc.parametrize('registry', [no_registry], ids=[''])
def power_mock_job_mock_runner_subcls_no_verbose_no_reg(
    job_case: JobCase,
    job_mock_classes: Tuple[JobType, Type[IsJobTemplate], Type[IsEngine]],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
):
    job_type, job_template_cls, job_runner_subcls = job_mock_classes
    return update_job_case_with_job(job_case,
                                    job_type,
                                    job_template_cls,
                                    job_runner_subcls(),
                                    engine_decorator,
                                    registry)


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.tasks')
@pc.parametrize('job_mock_classes', [task_mock_classes], ids=[''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def all_func_types_mock_job_mock_runner_subcls_assert_runstate_mock_reg(
    job_case: JobCase,
    job_mock_classes: Tuple[JobType, Type[IsJobTemplate], Type[IsEngine]],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
):
    job_type, job_template_cls, job_runner_subcls = job_mock_classes
    return update_job_case_with_job(job_case,
                                    job_type,
                                    job_template_cls,
                                    job_runner_subcls(),
                                    engine_decorator,
                                    registry)


# test_all_engines


@pc.fixture(scope='function')
@pc.parametrize_with_cases('job_case', cases='.cases.tasks')
@pc.parametrize('job_classes', [all_job_classes], ids=[''])
@pc.parametrize('engine', [all_engines], ids=[''])
@pc.parametrize('engine_decorator', [assert_runstate_engine_decorator])
@pc.parametrize('registry', [mock_registry], ids=[''])
def all_func_types_all_engines_assert_runstate_mock_reg(
    job_case: JobCase,
    job_classes: Tuple[JobType, Type[IsJobTemplate]],
    engine: Type[IsEngine],
    engine_decorator: Optional[Callable[[IsEngine], IsEngine]],
    registry: Optional[IsRunStateRegistry],
):
    job_type, job_template_cls = job_classes
    return update_job_case_with_job(job_case,
                                    job_type,
                                    job_template_cls,
                                    engine,
                                    engine_decorator,
                                    registry)


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
def task_a() -> MockTask:
    def concat_a(s: str) -> str:
        return s + 'a'

    return MockTask(concat_a, name='a')


@pytest.fixture(scope='module')
def task_b() -> MockTask:
    def concat_b(s: str) -> str:
        return s + 'b'

    return MockTask(concat_b, name='b')
