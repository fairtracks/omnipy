from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Callable, ClassVar, Dict, Optional, Tuple, Type

from unifair.config.engine import LocalRunnerConfig, PrefectEngineConfig
from unifair.config.registry import RunStateRegistryConfig
from unifair.engine.constants import RunState
from unifair.engine.local import LocalRunner
from unifair.engine.prefect import PrefectEngine
from unifair.engine.protocols import (IsEngine,
                                      IsEngineConfig,
                                      IsLocalRunnerConfig,
                                      IsPrefectEngineConfig,
                                      IsRunStateRegistry,
                                      IsRunStateRegistryConfig,
                                      IsTask)
from unifair.engine.task_runner import TaskRunnerEngine


class MockTask:
    engine: ClassVar[Optional[IsEngine]] = None

    def __init__(self, name: str, func: Callable) -> None:
        self.name = name
        self._func = func

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        return self._func(*args, **kwargs)

    @classmethod
    def set_engine(cls, engine: IsEngine) -> None:
        cls.engine = engine

    @classmethod
    def extrack_registry(cls) -> IsRunStateRegistry:
        from unifair.engine.base import Engine
        assert isinstance(cls.engine, Engine)
        return cls.engine._registry  # noqa


class MockTaskTemplate(MockTask):
    def apply(self) -> IsTask:
        task = MockTask(self.name, self._func)
        assert self.engine is not None
        task.set_engine(self.engine)
        assert isinstance(self.engine, TaskRunnerEngine)
        return self.engine.task_decorator(task)


@dataclass
class MockLocalRunnerConfig(LocalRunnerConfig):
    backend_verbose: bool = True


class MockLocalRunner(LocalRunner):
    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        return MockLocalRunnerConfig

    @property
    def config(self) -> Optional[IsLocalRunnerConfig]:
        return self._config

    @property
    def registry(self) -> Optional[IsRunStateRegistry]:
        return self._registry


@dataclass
class MockPrefectEngineConfig(PrefectEngineConfig):
    server_url: str = ''


class MockPrefectEngine(PrefectEngine):
    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        return MockPrefectEngineConfig

    @property
    def config(self) -> Optional[IsPrefectEngineConfig]:
        return self._config

    @property
    def registry(self) -> Optional[IsRunStateRegistry]:
        return self._registry


@dataclass
class MockEngineConfig:
    backend_verbose: bool = True


class MockTaskRunnerEngine(TaskRunnerEngine):
    def _init_engine(self) -> None:
        self.backend_task: Optional[MockBackendTask] = None
        self._update_from_config()

    def _update_from_config(self) -> None:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.backend_verbose: bool = self._config.backend_verbose

    def _init_task(self, task: IsTask) -> None:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.backend_task = MockBackendTask(task, self._config)

    def _run_task(self, task: IsTask, *args: Any, **kwargs: Any) -> Any:
        assert self.backend_task is not None
        return self.backend_task.run(*args, **kwargs)

    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        return MockEngineConfig


class MockBackendTask:
    def __init__(self, task: Type[IsTask], engine_config: MockEngineConfig):
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
    def __init__(self) -> None:
        self.logger: Optional[logging.Logger] = None
        self.config: IsRunStateRegistryConfig = RunStateRegistryConfig()

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


class TaskRunnerStateChecker(TaskRunnerEngine):
    def __init__(self, engine):
        self._engine = engine
        super().__init__()

    def _init_engine(self) -> None:
        self._engine._init_engine()  # noqa

    def get_config_cls(self) -> Type[IsEngineConfig]:
        return self._engine.get_config_cls()  # noqa

    def _update_from_config(self) -> None:
        return self._engine._update_from_config()  # noqa

    def _init_task(self, task: IsTask) -> None:
        from engine.helpers.functions import assert_task_state
        assert_task_state(task, RunState.INITIALIZED)
        self._engine._init_task(task)  # noqa

    def _run_task(self, task: IsTask, *args: Any, **kwargs: Any) -> Any:
        from engine.helpers.functions import assert_task_state
        assert_task_state(task, RunState.RUNNING)
        return self._engine._run_task(task, *args, **kwargs)  # noqa
