import pytest

from unifair.engine.protocols import RuntimeConfigProtocol

from .helpers.mocks import (MockEngineConfig,
                            MockRuntimeConfig,
                            MockTaskRunnerEngine,
                            MockTaskTemplate,
                            MockTask)


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
