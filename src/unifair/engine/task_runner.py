from abc import abstractmethod
import inspect
import sys
from types import AsyncGeneratorType, GeneratorType
from typing import Any

from unifair.engine.base import Engine
from unifair.engine.constants import RunState
from unifair.engine.protocols import IsTask


class TaskRunnerEngine(Engine):
    def _register_task_state(self, task: IsTask, state: RunState) -> None:
        if self._registry:
            self._registry.set_task_state(task, state)

    def task_decorator(self, task: IsTask) -> IsTask:
        self._register_task_state(task, RunState.INITIALIZED)
        self._init_task(task)

        prev_call_func = task._call_func  # noqa

        def _call_func(*args: Any, **kwargs: Any) -> Any:
            setattr(task, '_call_func', prev_call_func)
            self._register_task_state(task, RunState.RUNNING)
            task_result = self._run_task(*args, **kwargs)

            if isinstance(task_result, GeneratorType):

                def detect_finished_generator_decorator():
                    try:
                        value = yield next(task_result)
                        while True:
                            value = yield task_result.send(value)
                    except StopIteration:
                        self._register_task_state(task, RunState.FINISHED)

                return detect_finished_generator_decorator()
            elif isinstance(task_result, AsyncGeneratorType):

                async def detect_finished_async_generator_decorator():
                    try:
                        if sys.version_info >= (3, 10):
                            value = yield await anext(task_result)
                        else:
                            value = yield await task_result.__anext__()
                        while True:
                            value = yield await task_result.asend(value)
                    except StopAsyncIteration:
                        self._register_task_state(task, RunState.FINISHED)

                return detect_finished_async_generator_decorator()

            elif inspect.isawaitable(task_result):

                async def detect_finished_coroutine():
                    result = await task_result
                    self._register_task_state(task, RunState.FINISHED)
                    return result

                return detect_finished_coroutine()
            else:
                self._register_task_state(task, RunState.FINISHED)
                return task_result

        setattr(task, '_call_func', _call_func)

        return task

    @abstractmethod
    def _init_task(self, task: IsTask) -> None:
        ...

    @abstractmethod
    def _run_task(self, *args, **kwargs) -> Any:
        ...
