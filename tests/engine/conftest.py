import pytest

from unifair.engine.protocols import RuntimeConfigProtocol

from .helpers.mocks import (MockEngineConfig,
                            MockRuntimeConfig,
                            MockTaskRunnerEngine,
                            MockTaskTemplate)


@pytest.fixture(scope='module')
def runtime_mock_task_runner() -> RuntimeConfigProtocol:
    config = MockEngineConfig(verbose=False)
    return MockRuntimeConfig(engine=MockTaskRunnerEngine(config))  # noqa


@pytest.fixture(scope='module')
def power_task_template() -> MockTaskTemplate:
    def power(number: int, exponent: int):
        return number**exponent

    return MockTaskTemplate('power', power)
