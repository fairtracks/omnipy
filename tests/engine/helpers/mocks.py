from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, ClassVar, Dict, Optional, Tuple, Type

from unifair.engine.base import Engine
from unifair.engine.constants import RunState
from unifair.engine.protocols import (EngineConfigProtocol,
                                      EngineProtocol,
                                      RunStateRegistryProtocol,
                                      RuntimeConfigProtocol,
                                      TaskProtocol)
from unifair.engine.task_runner import TaskRunnerEngine


@dataclass
class MockRuntimeConfig:
    engine: EngineProtocol
    registry: Optional[RunStateRegistryProtocol] = None
    verbose: bool = False

    def __post_init__(self):
        self.engine.set_runtime(self)
        if self.registry is not None:
            self.registry.set_runtime(self)


@dataclass
class MockEngineConfig:
    backend_verbose: bool = True


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


class MockEngine(Engine):
    def _init_engine(self) -> None:
        ...

    def _get_default_config(self) -> EngineConfigProtocol:
        return MockEngineConfig()

    @property
    def runtime(self) -> Optional[RuntimeConfigProtocol]:
        return self._runtime


class MockTaskRunnerEngine(TaskRunnerEngine):
    def _init_engine(self) -> None:
        self.backend_task: Optional[MockBackendTask] = None
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.backend_verbose: bool = self._config.backend_verbose

    def _init_task(self, task) -> None:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.backend_task = MockBackendTask(task, self._config)

    def _run_task(self, *args, **kwargs) -> Any:
        assert self.backend_task is not None
        return self.backend_task.run(*args, **kwargs)

    def _get_default_config(self) -> EngineConfigProtocol:
        return MockEngineConfig()


class MockBackendTask:
    def __init__(self, task: Type[TaskProtocol], engine_config: MockEngineConfig):
        self.task = task
        self.engine_config = engine_config
        self.backend_verbose = engine_config.backend_verbose
        self.finished = False

    def run(self, *args: Any, **kwargs: Any):
        if self.engine_config.backend_verbose:
            print('Running task "{}": ...'.format(self.task.name))
        result = self.task(*args, **kwargs)
        if self.engine_config.backend_verbose:
            print('Result of task "{}": {}'.format(self.task.name, result))
        self.finished = True
        return result


class MockRunStateRegistry:
    def __init__(self):
        self._runtime: Optional[RuntimeConfigProtocol] = None
        self._tasks: Dict[str, TaskProtocol] = {}
        self._task_state: Dict[str, RunState] = {}
        self._task_state_datetime: Dict[Tuple[str, RunState], datetime] = {}

    def get_task_state(self, task: TaskProtocol) -> RunState:
        return self._task_state[task.name]

    def get_task_state_datetime(self, task: TaskProtocol, state: RunState) -> datetime:
        return self._task_state_datetime[(task.name, state)]

    def all_tasks(self, state: Optional[RunState] = None) -> Tuple[TaskProtocol, ...]:  # noqa
        return tuple(self._tasks.values())

    def set_task_state(self, task: TaskProtocol, state: RunState) -> None:
        self._tasks[task.name] = task
        self._task_state[task.name] = state
        self._task_state_datetime[(task.name, state)] = datetime.now()

    def set_runtime(self, runtime: RuntimeConfigProtocol) -> None:
        self._runtime = runtime

    @property
    def runtime(self) -> Optional[RuntimeConfigProtocol]:
        return self._runtime
