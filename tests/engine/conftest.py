import asyncio
from io import StringIO
import logging
from time import sleep
from typing import Annotated, Awaitable, Callable

import pytest

from unifair.engine.protocols import RuntimeConfigProtocol

from .helpers.mocks import (MockEngineConfig,
                            MockRunStateRegistry,
                            MockRuntimeConfig,
                            MockTask,
                            MockTaskRunnerEngine,
                            MockTaskTemplate)


@pytest.fixture(scope='function')
def str_stream() -> StringIO:
    return StringIO()


@pytest.fixture(scope='function')
def simple_logger() -> logging.Logger:
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    return logger


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
def runtime_mock_task_runner_no_verbose() -> RuntimeConfigProtocol:
    config = MockEngineConfig(verbose=False)
    registry = MockRunStateRegistry()
    return MockRuntimeConfig(  # noqa
        engine=MockTaskRunnerEngine(config, registry),
        registry=registry,
    )


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
    runtime_mock_task_runner_no_verbose: Annotated[RuntimeConfigProtocol, pytest.fixture],
    sync_wait_a_bit_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> MockTask:
    MockTaskTemplate.set_runtime(runtime_mock_task_runner_no_verbose)
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
    runtime_mock_task_runner_no_verbose: Annotated[RuntimeConfigProtocol, pytest.fixture],
    async_wait_a_bit_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> MockTask:
    MockTaskTemplate.set_runtime(runtime_mock_task_runner_no_verbose)
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
    runtime_mock_task_runner_no_verbose: Annotated[RuntimeConfigProtocol, pytest.fixture],
    sync_wait_for_send_twice_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> MockTask:
    MockTaskTemplate.set_runtime(runtime_mock_task_runner_no_verbose)
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
    runtime_mock_task_runner_no_verbose: Annotated[RuntimeConfigProtocol, pytest.fixture],
    async_wait_for_send_twice_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> MockTask:
    MockTaskTemplate.set_runtime(runtime_mock_task_runner_no_verbose)
    return async_wait_for_send_twice_task_template.apply()
