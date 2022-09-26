import asyncio
from typing import Any, Callable, Type

from prefect import flow as prefect_flow
from prefect import Flow as PrefectFlow
from prefect import task as prefect_task
from prefect import Task as PrefectTask

from unifair.config.engine import PrefectEngineConfig
from unifair.engine.protocols import IsPrefectEngineConfig, IsTask
from unifair.engine.task_runner import TaskRunnerEngine


class PrefectEngine(TaskRunnerEngine):
    def _init_engine(self) -> None:
        ...

    def _update_from_config(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsPrefectEngineConfig]:
        return PrefectEngineConfig

    def _init_task(self, task: IsTask, call_func: Callable) -> PrefectTask:
        if task.has_coroutine_task_func():

            @prefect_task(name=task.name)
            async def run_task(*inner_args, **inner_kwargs):
                return await call_func(*inner_args, **inner_kwargs)
        else:

            @prefect_task(name=task.name)
            def run_task(*inner_args, **inner_kwargs):
                return call_func(*inner_args, **inner_kwargs)

        return run_task

    def _run_task(
        self,
        state: PrefectTask,
        task: IsTask,
        call_func: Callable,
        *args,
        **kwargs,
    ) -> Any:

        _prefect_task = state

        if asyncio.iscoroutinefunction(_prefect_task):

            @prefect_flow(name=task.name)
            async def task_flow(*inner_args, **inner_kwargs):
                return await _prefect_task(*inner_args, **inner_kwargs)
        else:

            @prefect_flow(name=task.name)
            def task_flow(*inner_args, **inner_kwargs):
                return _prefect_task(*inner_args, **inner_kwargs)

        return task_flow(*args, **kwargs)
