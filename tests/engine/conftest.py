import asyncio
from functools import partial
from io import StringIO
import logging
from time import sleep
from typing import Annotated, Awaitable, Callable, cast

import pytest
import pytest_cases as pc

from unifair.engine.local import LocalRunner
from unifair.engine.protocols import IsTaskRunnerEngine
from unifair.engine.registry import RunStateRegistry

from .cases_local import CallableTaskCases
from .helpers.functions import add_logger_to_registry, convert_func_to_task
from .helpers.mocks import (MockEngineConfig,
                            MockRunStateRegistry,
                            MockTask,
                            MockTaskRunnerEngine,
                            MockTaskTemplate,
                            TaskRunnerStateChecker)


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


@pytest.fixture(scope='function')
def mock_run_state_registry() -> MockRunStateRegistry:
    return MockRunStateRegistry()


@pytest.fixture(scope='function')
def mock_run_state_registry_with_logger() -> MockRunStateRegistry:
    return cast(MockRunStateRegistry, add_logger_to_registry(MockRunStateRegistry()))


@pytest.fixture(scope='function')
def run_state_registry_with_logger() -> RunStateRegistry:
    return cast(RunStateRegistry, add_logger_to_registry(RunStateRegistry()))


@pytest.fixture(scope='function')
def mock_task_runner_engine_no_verbose(
        mock_run_state_registry: Annotated[MockRunStateRegistry,
                                           pytest.fixture]) -> IsTaskRunnerEngine:
    engine = MockTaskRunnerEngine()
    engine.set_config(MockEngineConfig(backend_verbose=False))
    MockTaskTemplate.set_engine(engine)
    engine.set_registry(mock_run_state_registry)
    return engine


@pytest.fixture(scope='module')
def sync_power_task_template() -> MockTaskTemplate:
    def power(number: int, exponent: int):
        return number**exponent

    return MockTaskTemplate('power', power)


@pytest.fixture(scope='module')
def sync_wait_a_bit_task_template() -> MockTaskTemplate:
    def sync_wait_a_bit(seconds: float) -> float:
        sleep(seconds)
        return seconds

    return MockTaskTemplate('sync_wait_a_bit', sync_wait_a_bit)


@pytest.fixture(scope='function')
def sync_wait_a_bit(
    mock_task_runner_engine_no_verbose,
    sync_wait_a_bit_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> MockTask:

    return sync_wait_a_bit_task_template.apply()


@pytest.fixture(scope='function')
def sync_assert_results_wait_a_bit(
        sync_wait_a_bit: Annotated[MockTask, pytest.fixture]) -> Callable[[float], None]:
    def assert_results_sync_wait_a_bit(seconds: float):
        assert sync_wait_a_bit(seconds) == seconds

    return assert_results_sync_wait_a_bit


@pytest.fixture(scope='module')
def async_wait_a_bit_task_template() -> MockTaskTemplate:
    async def async_wait_a_bit(seconds: float) -> float:
        await asyncio.sleep(seconds)
        return seconds

    return MockTaskTemplate('async_wait_a_bit', async_wait_a_bit)


@pytest.fixture(scope='function')
def async_wait_a_bit(
    mock_task_runner_engine_no_verbose,
    async_wait_a_bit_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> MockTask:

    return async_wait_a_bit_task_template.apply()


@pytest.fixture(scope='function')
def async_assert_results_wait_a_bit(
        async_wait_a_bit: Annotated[MockTask, pytest.fixture]) -> \
            Callable[[float], Awaitable[None]]:
    async def async_assert_results_wait_a_bit(seconds: float) -> None:
        assert await async_wait_a_bit(seconds) == seconds

    return async_assert_results_wait_a_bit


@pytest.fixture(scope='function')
def async_run_assert_results_wait_a_bit(
        async_assert_results_wait_a_bit: Annotated[Callable[[float], Awaitable[None]], pytest.fixture]) -> \
            Callable[[float], None]:
    def run(seconds: float) -> None:
        asyncio.run(async_assert_results_wait_a_bit(seconds))

    return run


@pytest.fixture(scope='module')
def sync_wait_for_send_twice_task_template() -> MockTaskTemplate:
    def sync_wait_for_send_twice():
        for i in range(2):
            value = yield
            yield i, value

    return MockTaskTemplate('sync_wait_for_send_twice', sync_wait_for_send_twice)


@pytest.fixture(scope='function')
def sync_wait_for_send_twice(
    mock_task_runner_engine_no_verbose,
    sync_wait_for_send_twice_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> MockTask:

    return sync_wait_for_send_twice_task_template.apply()


@pytest.fixture(scope='module')
def async_wait_for_send_twice_task_template() -> MockTaskTemplate:
    async def async_wait_for_send_twice():
        for i in range(2):
            value = yield
            yield i, value

    return MockTaskTemplate('async_wait_for_send_twice', async_wait_for_send_twice)


@pytest.fixture(scope='function')
def async_wait_for_send_twice(
    mock_task_runner_engine_no_verbose,
    async_wait_for_send_twice_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> MockTask:

    return async_wait_for_send_twice_task_template.apply()


@pc.fixture(scope='function')
@pc.parametrize(
    task_template_cls=[MockTaskTemplate],
    ids=['mtask'],
)
def mock_task_template(task_template_cls):
    return task_template_cls


@pc.fixture(scope='function')
@pc.parametrize(
    engine=[
        TaskRunnerStateChecker(LocalRunner()),
    ],
    ids=[
        'local',
    ],
)
def all_engines_with_assert(engine):
    return engine


@pc.fixture(scope='function')
@pc.parametrize(
    registry=[pc.fixture_ref(mock_run_state_registry_with_logger)],
    ids=['mregistry'],
)
def mock_registry(registry):
    return registry


def create_task_from_func_cases_with_parametrized_fixtures(func_case_tag: str,
                                                           task_template_cls_fixture: str,
                                                           engine_fixture: str,
                                                           registry_fixture: str):
    @pc.fixture(scope='function')
    @pc.parametrize_with_cases(
        'name, func, args, kwargs, assert_result', cases=CallableTaskCases, has_tag=func_case_tag)
    @pc.parametrize(
        'task_template_cls, engine, registry',
        [
            (
                pc.fixture_ref(task_template_cls_fixture),
                pc.fixture_ref(engine_fixture),
                pc.fixture_ref(registry_fixture),
            ),
        ],
        idgen=func_case_tag)
    def get_task(name, func, args, kwargs, assert_result, task_template_cls, engine, registry):
        task = convert_func_to_task(name, func, task_template_cls, engine, registry)
        return task, args, kwargs, assert_result

    return get_task


create_task_all_engines_mock_rest = partial(
    create_task_from_func_cases_with_parametrized_fixtures,
    task_template_cls_fixture='mock_task_template',
    engine_fixture='all_engines_with_assert',
    registry_fixture='mock_registry',
)

sync_function_task_all_engines_mock_rest = create_task_all_engines_mock_rest(
    func_case_tag='sync function')

sync_coroutine_task_all_engines_mock_rest = create_task_all_engines_mock_rest(
    func_case_tag='sync generator-coroutine')

async_function_task_all_engines_mock_rest = create_task_all_engines_mock_rest(
    func_case_tag='async coroutine')

async_coroutine_task_all_engines_mock_rest = create_task_all_engines_mock_rest(
    func_case_tag='async generator-coroutine')
