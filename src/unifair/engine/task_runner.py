from abc import abstractmethod
from typing import Any

from unifair.engine.base import Engine
from unifair.engine.protocols import TaskProtocol


class TaskRunnerEngine(Engine):
    def task_decorator(self, task: TaskProtocol) -> TaskProtocol:
        self._init_task(task)

        prev_call_func = task._call_func  # noqa

        def _call_func(*args: Any, **kwargs: Any) -> Any:
            setattr(task, '_call_func', prev_call_func)
            return self._run_task(*args, **kwargs)

        setattr(task, '_call_func', _call_func)

        return task

    @abstractmethod
    def _init_task(self, task: TaskProtocol) -> None:
        ...

    @abstractmethod
    def _run_task(self, *args, **kwargs) -> Any:
        ...
