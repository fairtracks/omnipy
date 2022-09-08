from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Type

from unifair.compute.task import Task


@dataclass
class EngineConfig:
    ...


class Engine(ABC):
    def __init__(self, config: EngineConfig = None):
        if config is None:
            config = self._config_cls()
        self._config = config
        self._init_engine()

    @abstractmethod
    def _config_cls(self) -> Type[EngineConfig]:
        ...

    @abstractmethod
    def _init_engine(self) -> None:
        ...


class TaskRunnerEngine(Engine):
    def task_decorator(self, task: Task) -> Task:
        self._init_task(task)

        prev_call_func = task._call_func

        def _call_func(*args: Any, **kwargs: Any) -> Any:
            task._call_func = prev_call_func
            return self._run_task(*args, **kwargs)

        task._call_func = _call_func

        return task

    @abstractmethod
    def _init_task(self, task) -> None:
        ...

    @abstractmethod
    def _run_task(self, *args, **kwargs) -> Any:
        ...
