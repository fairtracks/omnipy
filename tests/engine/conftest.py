from io import StringIO
import logging

import pytest

from unifair.engine.protocols import RuntimeConfigProtocol

from .helpers.mocks import (MockEngineConfig,
                            MockRuntimeConfig,
                            MockTask,
                            MockTaskRunnerEngine,
                            MockTaskTemplate)


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


@pytest.fixture(scope='module')
def runtime_mock_task_runner() -> RuntimeConfigProtocol:
    config = MockEngineConfig(verbose=False)
    return MockRuntimeConfig(engine=MockTaskRunnerEngine(config))  # noqa


@pytest.fixture(scope='module')
def power_task_template() -> MockTaskTemplate:
    def power(number: int, exponent: int):
        return number**exponent

    return MockTaskTemplate('power', power)


@pytest.fixture(scope='class')
def str_stream() -> StringIO:
    return StringIO()


@pytest.fixture(scope='class')
def simple_logger() -> logging.Logger:
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    return logger
