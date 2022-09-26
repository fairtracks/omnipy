import asyncio
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple, Type

from unifair.engine.base import Engine
from unifair.engine.constants import RunState
from unifair.engine.protocols import (IsEngine,
                                      IsEngineConfig,
                                      IsRunStateRegistry,
                                      IsRunStateRegistryConfig,
                                      IsTask,
                                      IsTaskRunnerEngine)
from unifair.engine.task_runner import TaskRunnerEngine


class MockJobCreator:
    def __init__(self):
        self.engine: Optional[IsTaskRunnerEngine] = None

    def set_engine(self, engine: IsTaskRunnerEngine) -> None:
        self.engine = engine


class MockTask:
    job_creator = MockJobCreator()

    def __init__(self, name: str, func: Callable) -> None:
        self.name = name
        self._func = func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        return self._func(*args, **kwargs)

    def has_coroutine_task_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._func)

    @classmethod
    def extrack_registry(cls) -> IsRunStateRegistry:
        assert isinstance(cls.engine, Engine)
        return cls.engine._registry  # noqa


class MockTaskTemplate(MockTask):
    def apply(self) -> IsTask:
        task = MockTask(self.name, self._func)
        return self.job_creator.engine.task_decorator(task)


@dataclass
class MockEngineConfig:
    backend_verbose: bool = True


class MockBackendTask:
    def __init__(self, engine_config: MockEngineConfig):
        self.backend_verbose = engine_config.backend_verbose

    def run(self, task: IsTask, call_func: Callable, *args: Any, **kwargs: Any):
        if self.backend_verbose:
            print('Running task "{}": ...'.format(task.name))
        result = call_func(*args, **kwargs)
        if self.backend_verbose:
            print('Result of task "{}": {}'.format(task.name, result))
        return result


class MockEngineSubclass(Engine):
    def _init_engine(self) -> None:
        self._update_from_config()

    def _update_from_config(self) -> None:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.backend_verbose: bool = self._config.backend_verbose

    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        return MockEngineConfig


class MockTaskRunnerSubclass(MockEngineSubclass, TaskRunnerEngine):
    def _init_engine(self) -> None:
        super()._init_engine()
        self.finished_backend_tasks: List[MockBackendTask] = []

    def _init_task(self, task: IsTask, call_func: Callable) -> MockBackendTask:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        return MockBackendTask(self._config)

    def _run_task(self, state: MockBackendTask, task: IsTask, call_func: Callable, *args,
                  **kwargs) -> Any:
        result = state.run(task, call_func, *args, **kwargs)
        self.finished_backend_tasks.append(state)
        return result


@dataclass
class MockRunStateRegistryConfig:
    verbose: bool = True


class MockRunStateRegistry:
    def __init__(self) -> None:
        self.logger: Optional[logging.Logger] = None
        self.config: IsRunStateRegistryConfig = MockRunStateRegistryConfig()

        self._tasks: Dict[str, IsTask] = {}
        self._task_state: Dict[str, RunState] = {}
        self._task_state_datetime: Dict[Tuple[str, RunState], datetime] = {}

    def get_task_state(self, task: IsTask) -> RunState:
        return self._task_state[task.name]

    def get_task_state_datetime(self, task: IsTask, state: RunState) -> datetime:
        return self._task_state_datetime[(task.name, state)]

    def all_tasks(self, state: Optional[RunState] = None) -> Tuple[IsTask, ...]:  # noqa
        return tuple(self._tasks.values())

    def set_task_state(self, task: IsTask, state: RunState) -> None:
        self._tasks[task.name] = task
        self._task_state[task.name] = state
        self._task_state_datetime[(task.name, state)] = datetime.now()
        if self.logger:
            self.logger.info(f'{task.name} - {state.name}')

    def set_logger(self, logger: Optional[logging.Logger]) -> None:
        self.logger = logger

    def set_config(self, config: IsRunStateRegistryConfig) -> None:
        self.config = config
