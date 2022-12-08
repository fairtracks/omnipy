import asyncio
from datetime import timedelta
from typing import Any, Callable, Type

from prefect import flow as prefect_flow
from prefect import Flow as PrefectFlow
from prefect import task as prefect_task
from prefect import Task as PrefectTask
from prefect.tasks import task_input_hash

from unifair.config.engine import PrefectEngineConfig
from unifair.engine.job_runner import DagFlowRunnerEngine, TaskRunnerEngine
from unifair.engine.protocols import IsDagFlow, IsPrefectEngineConfig, IsTask
from unifair.util.helpers import resolve


class PrefectEngine(TaskRunnerEngine, DagFlowRunnerEngine):
    def _init_engine(self) -> None:
        ...

    def _update_from_config(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsPrefectEngineConfig]:
        return PrefectEngineConfig

    def _init_task(self, task: IsTask, call_func: Callable) -> PrefectTask:

        assert isinstance(self._config, PrefectEngineConfig)
        task_kwargs = dict(
            name=task.name,
            cache_key_fn=task_input_hash if self._config.use_cached_results else None,
            cache_expiration=timedelta(days=1))

        if task.has_coroutine_func():

            @prefect_task(**task_kwargs)
            async def run_task(*inner_args, **inner_kwargs):
                return await call_func(*inner_args, **inner_kwargs)
        else:

            @prefect_task(**task_kwargs)
            def run_task(*inner_args, **inner_kwargs):
                return call_func(*inner_args, **inner_kwargs)

        return run_task

    def _run_task(self, state: PrefectTask, task: IsTask, call_func: Callable, *args,
                  **kwargs) -> Any:

        _prefect_task = state

        if task.in_flow_context:
            return _prefect_task(*args, return_state=False, **kwargs)
        else:
            flow_kwargs = dict(name=task.name)

            if asyncio.iscoroutinefunction(_prefect_task):

                @prefect_flow(**flow_kwargs)
                async def task_flow(*inner_args, **inner_kwargs):
                    return await resolve(
                        _prefect_task(*inner_args, return_state=False, **inner_kwargs))
            else:

                @prefect_flow(**flow_kwargs)
                def task_flow(*inner_args, **inner_kwargs):
                    return _prefect_task(*inner_args, return_state=False, **inner_kwargs)

            return task_flow(*args, **kwargs)

    def _init_dag_flow(self, flow: IsDagFlow) -> Any:

        assert isinstance(self._config, PrefectEngineConfig)
        flow_kwargs = dict(name=flow.name,)
        call_func = self.default_dag_flow_run_decorator(flow)

        if flow.has_coroutine_func():

            @prefect_flow(**flow_kwargs)
            async def run_dag_flow(*inner_args, **inner_kwargs):
                with flow.flow_context:
                    return await resolve(call_func(*inner_args, **inner_kwargs))
        else:

            @prefect_flow(**flow_kwargs)
            def run_dag_flow(*inner_args, **inner_kwargs):
                with flow.flow_context:
                    return call_func(*inner_args, **inner_kwargs)

        return run_dag_flow

    def _run_dag_flow(self, state: PrefectFlow, flow: IsDagFlow, *args, **kwargs) -> Any:

        _prefect_flow = state

        return _prefect_flow(*args, **kwargs)
