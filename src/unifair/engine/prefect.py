import asyncio
from typing import Any, Type

from prefect import flow as prefect_flow
from prefect import task as prefect_task

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

    def _init_task(self, task: IsTask) -> None:
        if task.has_coroutine_task_func():

            @prefect_task(name=task.name)
            async def run_task(*inner_args, **inner_kwargs):
                return await task(*inner_args, **inner_kwargs)
        else:

            @prefect_task(name=task.name)
            def run_task(*inner_args, **inner_kwargs):
                return task(*inner_args, **inner_kwargs)

        self._prefect_task = run_task

    def _run_task(self, task: IsTask, *args: Any, **kwargs: Any) -> Any:
        if asyncio.iscoroutinefunction(self._prefect_task):

            @prefect_flow(name=task.name)
            async def task_flow(*inner_args, **inner_kwargs):
                return await self._prefect_task(*inner_args, **inner_kwargs)
        else:

            @prefect_flow(name=task.name)
            def task_flow(*inner_args, **inner_kwargs):
                return self._prefect_task(*inner_args, **inner_kwargs)

        return task_flow(*args, **kwargs)
