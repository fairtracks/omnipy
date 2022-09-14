from dataclasses import dataclass
from typing import Any, Callable, ClassVar, Optional, Type

from unifair.engine.base import Engine, EngineConfig
from unifair.engine.protocols import RuntimeConfigProtocol, TaskProtocol
from unifair.engine.task_runner import TaskRunnerEngine


@dataclass
class MockRuntimeConfig:
    engine: Engine


@dataclass
class MockEngineConfig(EngineConfig):
    verbose: bool = True


class MockTask:
    runtime: ClassVar[Optional[MockRuntimeConfig]] = None

    def __init__(self, name: str, func: Callable) -> None:
        self.name = name
        self._func = func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        return self._func(*args, **kwargs)

    @classmethod
    def set_runtime(cls, runtime: RuntimeConfigProtocol) -> None:
        assert isinstance(runtime, MockRuntimeConfig)
        cls.runtime = runtime


class MockTaskTemplate(MockTask):
    def apply(self) -> TaskProtocol:
        task = MockTask(self.name, self._func)
        assert self.runtime is not None
        task.set_runtime(self.runtime)
        assert isinstance(self.runtime.engine, TaskRunnerEngine)
        return self.runtime.engine.task_decorator(task)


class MockBackendTask:
    def __init__(self, task: Type[TaskProtocol], engine_config: MockEngineConfig):
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


class MockTaskRunnerEngine(TaskRunnerEngine):
    def _init_engine(self) -> None:
        self.backend_task: Optional[MockBackendTask] = None
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.verbose: bool = self._config.verbose

    def _init_task(self, task) -> None:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.backend_task = MockBackendTask(task, self._config)

    def _run_task(self, *args, **kwargs) -> Any:
        assert self.backend_task is not None
        return self.backend_task.run(*args, **kwargs)
