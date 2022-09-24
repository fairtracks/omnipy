from functools import partial
from io import StringIO
import logging
from typing import Annotated, cast

import pytest
import pytest_cases as pc

from unifair.engine.local import LocalRunner

from .helpers.functions import add_logger_to_registry, convert_func_to_task
from .helpers.mocks import (MockEngineConfig,
                            MockRunStateRegistry,
                            MockTask,
                            MockTaskRunnerEngine,
                            MockTaskTemplate,
                            TaskRunnerStateChecker)

# TaskTemplate


@pc.fixture(scope='function')
@pc.parametrize(
    task_template_cls=[MockTaskTemplate],
    ids=['m[task]'],
)
def mock_task_template(task_template_cls):
    return task_template_cls


# TaskRunnerEngine


@pc.fixture(scope='function')
@pc.parametrize(
    engine=[MockTaskRunnerEngine()],
    ids=['assertinitrun[taskrunner-m[engine]]'],
)
def mock_task_runner_subclass_with_assert(engine):
    return TaskRunnerStateChecker(engine)


@pc.fixture(scope='function')
@pc.parametrize(
    engine=[MockTaskRunnerEngine()],
    ids=['taskrunner-m[engine]'],
)
def mock_task_runner_subclass_no_verbose(engine):
    engine.set_config(MockEngineConfig(backend_verbose=False))
    return engine


# Engine


@pc.fixture(scope='function')
@pc.parametrize(
    engine=[
        LocalRunner(),
    ],
    ids=[
        'assertinitrun[local]',
    ],
)
def all_engines_with_assert(engine):
    return TaskRunnerStateChecker(engine)


# RunStateRegistry


@pc.fixture(scope='function')
@pc.parametrize(
    registry=[MockRunStateRegistry()],
    ids=['m[registry]'],
)
def mock_registry(registry):
    return cast(MockRunStateRegistry, add_logger_to_registry(registry))


@pc.fixture(scope='function')
@pc.parametrize(registry=[None], ids=['no-registry'])
def no_registry(registry):
    return registry


# Task factory


def task_from_func_cases_with_param_fixtures(
    func_case_tag: str,
    task_template_cls_fixture: str,
    engine_fixture: str,
    registry_fixture: str,
):
    @pc.fixture(scope='function')
    @pc.parametrize_with_cases(
        'name, func, run_and_assert_results', cases='.cases_tasks', has_tag=func_case_tag)
    @pc.parametrize(
        'task_template_cls, engine, registry',
        [
            (
                pc.fixture_ref(task_template_cls_fixture),
                pc.fixture_ref(engine_fixture),
                pc.fixture_ref(registry_fixture),
            ),
        ],
        idgen='with')
    def get_task(name, func, run_and_assert_results, task_template_cls, engine, registry):
        task = convert_func_to_task(name, func, task_template_cls, engine, registry)
        return task, run_and_assert_results

    return get_task


# test_task_runner

mock_task_mock_taskrun_subcls = partial(
    task_from_func_cases_with_param_fixtures,
    task_template_cls_fixture='mock_task_template',
)

power_mock_task_mock_taskrun_subcls_with_backend_no_reg = mock_task_mock_taskrun_subcls(
    func_case_tag='power',
    engine_fixture='mock_task_runner_subclass_no_verbose',
    registry_fixture='no_registry')

mock_task_mock_taskrun_subcls_mock_reg = partial(
    mock_task_mock_taskrun_subcls,
    engine_fixture='mock_task_runner_subclass_with_assert',
    registry_fixture='mock_registry')

singlethread_mock_task_mock_taskrun_subcls_mock_reg = mock_task_mock_taskrun_subcls_mock_reg(
    func_case_tag='singlethread')

multithread_mock_task_mock_taskrun_subcls_mock_reg = mock_task_mock_taskrun_subcls_mock_reg(
    func_case_tag='multithread')

multiprocess_mock_task_mock_taskrun_subcls_mock_reg = mock_task_mock_taskrun_subcls_mock_reg(
    func_case_tag='multiprocess')

# test_all_engines

mock_task_all_engines_mock_reg = partial(
    task_from_func_cases_with_param_fixtures,
    task_template_cls_fixture='mock_task_template',
    engine_fixture='all_engines_with_assert',
    registry_fixture='mock_registry')

singlethread_mock_task_all_engines_mock_reg = mock_task_all_engines_mock_reg(
    func_case_tag='singlethread')

multithread_mock_task_all_engines_mock_reg = mock_task_all_engines_mock_reg(
    func_case_tag='multithread')

multiprocess_mock_task_all_engines_mock_reg = mock_task_all_engines_mock_reg(
    func_case_tag='multiprocess')

# test_registry


@pytest.fixture(scope='function')
def str_stream() -> StringIO:
    return StringIO()


@pytest.fixture(scope='function')
def simple_logger() -> logging.Logger:
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    return logger


@pytest.fixture(scope='function')
def stream_logger(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
) -> logging.Logger:

    simple_logger.addHandler(logging.StreamHandler(str_stream))
    return simple_logger


@pytest.fixture(scope='module')
def task_a() -> MockTask:
    def concat_a(s: str) -> str:
        return s + 'a'

    return MockTask('a', concat_a)


@pytest.fixture(scope='module')
def task_b() -> MockTask:
    def concat_b(s: str) -> str:
        return s + 'b'

    return MockTask('b', concat_b)
