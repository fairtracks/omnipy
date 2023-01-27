import asyncio
from datetime import timedelta
from typing import Any, Callable, Type

from omnipy.api.protocols import IsDagFlow, IsFuncFlow, IsLinearFlow, IsPrefectEngineConfig, IsTask
from omnipy.config.engine import PrefectEngineConfig
from omnipy.engine.job_runner import (DagFlowRunnerEngine,
                                      FuncFlowRunnerEngine,
                                      LinearFlowRunnerEngine,
                                      TaskRunnerEngine)
from omnipy.modules.prefect import flow as prefect_flow
from omnipy.modules.prefect import Flow as PrefectFlow
from omnipy.modules.prefect import task as prefect_task
from omnipy.modules.prefect import Task as PrefectTask
from omnipy.modules.prefect import task_input_hash
from omnipy.util.helpers import resolve


class PrefectEngine(TaskRunnerEngine,
                    LinearFlowRunnerEngine,
                    DagFlowRunnerEngine,
                    FuncFlowRunnerEngine):
    def _init_engine(self) -> None:
        ...

    def _update_from_config(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsPrefectEngineConfig]:
        return PrefectEngineConfig

    # TaskRunnerEngine

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
            return _prefect_task(*args, **kwargs)
        else:
            flow_kwargs = dict(name=task.name)

            if asyncio.iscoroutinefunction(_prefect_task):

                @prefect_flow(**flow_kwargs)
                async def task_flow(*inner_args, **inner_kwargs):
                    return await resolve(_prefect_task(*inner_args, **inner_kwargs))
            else:

                @prefect_flow(**flow_kwargs)
                def task_flow(*inner_args, **inner_kwargs):
                    return _prefect_task(*inner_args, **inner_kwargs)

            return task_flow(*args, **kwargs)

    # LinearFlowRunnerEngine
    def _init_linear_flow(self, linear_flow: IsLinearFlow) -> Any:
        assert isinstance(self._config, PrefectEngineConfig)
        flow_kwargs = dict(name=linear_flow.name,)
        call_func = self.default_linear_flow_run_decorator(linear_flow)

        if linear_flow.has_coroutine_func():

            @prefect_flow(**flow_kwargs)
            async def run_linear_flow(*inner_args, **inner_kwargs):
                with linear_flow.flow_context:
                    return await resolve(call_func(*inner_args, **inner_kwargs))
        else:

            @prefect_flow(**flow_kwargs)
            def run_linear_flow(*inner_args, **inner_kwargs):
                with linear_flow.flow_context:
                    return call_func(*inner_args, **inner_kwargs)

        return run_linear_flow

    def _run_linear_flow(self, state: Any, linear_flow: IsLinearFlow, *args, **kwargs) -> Any:

        _prefect_flow = state

        return _prefect_flow(*args, **kwargs)

    # DagFlowRunnerEngine

    def _init_dag_flow(self, dag_flow: IsDagFlow) -> Any:

        assert isinstance(self._config, PrefectEngineConfig)
        flow_kwargs = dict(name=dag_flow.name,)
        call_func = self.default_dag_flow_run_decorator(dag_flow)

        if dag_flow.has_coroutine_func():

            @prefect_flow(**flow_kwargs)
            async def run_dag_flow(*inner_args, **inner_kwargs):
                with dag_flow.flow_context:
                    return await resolve(call_func(*inner_args, **inner_kwargs))
        else:

            @prefect_flow(**flow_kwargs)
            def run_dag_flow(*inner_args, **inner_kwargs):
                with dag_flow.flow_context:
                    return call_func(*inner_args, **inner_kwargs)

        return run_dag_flow

    def _run_dag_flow(self, state: PrefectFlow, flow: IsDagFlow, *args, **kwargs) -> Any:

        _prefect_flow = state

        return _prefect_flow(*args, **kwargs)

    # FuncFlowRunnerEngine

    def _init_func_flow(self, func_flow: IsFuncFlow, call_func: Callable) -> object:

        assert isinstance(self._config, PrefectEngineConfig)
        flow_kwargs = dict(name=func_flow.name,)

        if func_flow.has_coroutine_func():

            @prefect_flow(**flow_kwargs)
            async def run_func_flow(*inner_args, **inner_kwargs):
                with func_flow.flow_context:
                    return await resolve(call_func(*inner_args, **inner_kwargs))
        else:

            @prefect_flow(**flow_kwargs)
            def run_func_flow(*inner_args, **inner_kwargs):
                with func_flow.flow_context:
                    return call_func(*inner_args, **inner_kwargs)

        return run_func_flow

    def _run_func_flow(self,
                       state: Any,
                       func_flow: IsFuncFlow,
                       call_func: Callable,
                       *args,
                       **kwargs) -> Any:

        _prefect_flow = state

        return _prefect_flow(*args, **kwargs)


# TODO: Refactor redundant code
