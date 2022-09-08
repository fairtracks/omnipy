from dataclasses import dataclass
from typing import Any, Type

import pytest

from unifair.engine.base import Engine, EngineConfig, TaskRunnerEngine


@pytest.fixture
def MockRuntimeConfig() -> Type['MockRuntimeConfig']:  # noqa
    @dataclass
    class MockRuntimeConfig:
        engine: Engine

    return MockRuntimeConfig


@pytest.fixture
def MockEngineConfig() -> Type['MockEngineConfig']:  # noqa
    @dataclass
    class MockEngineConfig(EngineConfig):
        verbose: bool = True

    return MockEngineConfig


@pytest.fixture
def MockTask(MockRuntimeConfig) -> Type['MockTask']:  # noqa
    class MockTask:
        runtime = None

        def __init__(self, name, func):
            self.name = name
            self._func = func

        def __call__(self, *args: Any, **kwargs: Any):
            return self._call_func(*args, **kwargs)

        def _call_func(self, *args: Any, **kwargs: Any):
            return self._func(*args, **kwargs)

        @classmethod
        def set_runtime(cls, runtime: MockRuntimeConfig):
            cls.runtime = runtime

    return MockTask


@pytest.fixture
def MockTaskTemplate(MockRuntimeConfig, MockTask) -> Type['MockTaskTemplate']:  # noqa
    class MockTaskTemplate(MockTask):
        def apply(self) -> MockTask:
            task = MockTask(self.name, self._func)  # noqa
            task.set_runtime(self.runtime)
            return self.runtime.engine.task_decorator(task)

    return MockTaskTemplate


@pytest.fixture
def MockBackendTask(MockEngineConfig, MockTaskTemplate) -> Type['MockBackendTask']:  # noqa
    class MockBackendTask:
        def __init__(self, task: MockTaskTemplate, engine_config: MockEngineConfig):
            self.task = task
            self.engine_config = engine_config
            self.verbose = engine_config.verbose
            self.finished = False

        def run(self, *args: Any, **kwargs: Any):
            if self.engine_config.verbose:
                print('Running task "{}": ...'.format(self.task.name))
            result = self.task(*args, **kwargs)
            if self.engine_config.verbose:
                print('Result of task "{}": {}'.format(self.task.name, result))
            self.finished = True
            return result

    return MockBackendTask


@pytest.fixture
def MockTaskRunnerEngine(MockEngineConfig, MockBackendTask) -> Type['MockTaskRunnerEngine']:  # noqa
    class MockTaskRunnerEngine(TaskRunnerEngine):
        def _config_cls(self) -> Type[EngineConfig]:
            return MockEngineConfig

        def _init_engine(self) -> None:
            self.backend_task = None
            self.verbose = self._config.verbose  # noqa

        def _init_task(self, task) -> None:
            self.backend_task = MockBackendTask(task, self._config)

        def _run_task(self, *args, **kwargs) -> Any:
            return self.backend_task.run(*args, **kwargs)

    return MockTaskRunnerEngine


@pytest.fixture
def runtime(MockRuntimeConfig, MockEngineConfig, MockTaskRunnerEngine) -> MockRuntimeConfig:  # noqa
    return MockRuntimeConfig(engine=MockTaskRunnerEngine(config=MockEngineConfig(verbose=False)))


def test_engine_init(MockTaskRunnerEngine, MockEngineConfig) -> None:  # noqa
    engine = MockTaskRunnerEngine(config=MockEngineConfig(verbose=True))
    assert engine.verbose is True
    engine = MockTaskRunnerEngine(config=MockEngineConfig(verbose=False))
    assert engine.verbose is False


@pytest.fixture
def power_task_template(MockTaskTemplate) -> MockTaskTemplate:  # noqa
    def power(number: int, exponent: int):
        return number**exponent

    return MockTaskTemplate('power', power)


def test_run_mock_task_run(runtime, MockTaskTemplate, power_task_template) -> None:  # noqa
    MockTaskTemplate.set_runtime(runtime)

    power = power_task_template.apply()

    assert power(4, 2) == 16
    assert power.name == 'power'
    assert power.runtime.engine.backend_task.verbose is False
    assert power.runtime.engine.backend_task.finished
