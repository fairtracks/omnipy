from datetime import timedelta
from typing import Any, Callable, Type, TYPE_CHECKING

from omnipy.config.engine import PrefectEngineConfig
from omnipy.engine.job_runner import (DagFlowRunnerEngine,
                                      FuncFlowRunnerEngine,
                                      LinearFlowRunnerEngine,
                                      TaskRunnerEngine)
from omnipy.shared.protocols.compute.job import IsDagFlow, IsFlow, IsFuncFlow, IsLinearFlow, IsTask
from omnipy.shared.protocols.config import IsPrefectEngineConfig
from omnipy.util.helpers import resolve

if TYPE_CHECKING:
    from ..lazy_import import PrefectTask


class PrefectEngine(TaskRunnerEngine,
                    LinearFlowRunnerEngine,
                    DagFlowRunnerEngine,
                    FuncFlowRunnerEngine):
    """Job runner engine for Prefect"""
    def _init_engine(self) -> None:
        ...

    def _update_from_config(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsPrefectEngineConfig]:
        return PrefectEngineConfig

    # TaskRunnerEngine

    def _init_task(self, task: IsTask, call_func: Callable) -> 'PrefectTask':
        from ..lazy_import import prefect_task, task_input_hash

        assert isinstance(self._config, PrefectEngineConfig)
        task_kwargs = dict(
            name=task.name,
            cache_key_fn=task_input_hash if self._config.use_cached_results else None,
            cache_expiration=timedelta(days=1))

        if task.has_coroutine_func():

            @prefect_task(**task_kwargs)
            async def _task(*inner_args, **inner_kwargs):
                return await call_func(*inner_args, **inner_kwargs)
        else:

            @prefect_task(**task_kwargs)
            def _task(*inner_args, **inner_kwargs):
                return call_func(*inner_args, **inner_kwargs)

        return _task

    def _run_task(self, state: 'PrefectTask', task: IsTask, call_func: Callable, *args,
                  **kwargs) -> Any:
        from ..lazy_import import prefect_flow

        _prefect_task = state

        if task.in_flow_context:
            return _prefect_task(*args, **kwargs)
        else:
            flow_kwargs = dict(name=task.name)

            if task.has_coroutine_func():

                @prefect_flow(**flow_kwargs)
                async def _task_flow(*inner_args, **inner_kwargs):
                    return await resolve(_prefect_task(*inner_args, **inner_kwargs))
            else:

                @prefect_flow(**flow_kwargs)
                def _task_flow(*inner_args, **inner_kwargs):
                    return _prefect_task(*inner_args, **inner_kwargs)

            return _task_flow(*args, **kwargs)

    def _init_flow(self, flow: IsFlow, call_func: Callable) -> Any:
        from ..lazy_import import prefect_flow

        assert isinstance(self._config, PrefectEngineConfig)
        flow_kwargs = dict(name=flow.name,)
        if flow.has_coroutine_func():

            @prefect_flow(**flow_kwargs)
            async def _flow(*inner_args, **inner_kwargs):
                with flow.flow_context:
                    return await resolve(call_func(*inner_args, **inner_kwargs))
        else:

            @prefect_flow(**flow_kwargs)
            def _flow(*inner_args, **inner_kwargs):
                with flow.flow_context:
                    return call_func(*inner_args, **inner_kwargs)

        return _flow

    def _run_flow(self, state: Any, flow: IsFlow, *args, **kwargs) -> Any:
        _prefect_flow = state
        return _prefect_flow(*args, **kwargs)

    # LinearFlowRunnerEngine
    def _init_linear_flow(self, linear_flow: IsLinearFlow) -> Any:
        call_func = self.default_linear_flow_run_decorator(linear_flow)
        return self._init_flow(linear_flow, call_func)

    def _run_linear_flow(self, state: Any, linear_flow: IsLinearFlow, *args, **kwargs) -> Any:
        return self._run_flow(state, linear_flow, *args, **kwargs)

    # DagFlowRunnerEngine

    def _init_dag_flow(self, dag_flow: IsDagFlow) -> Any:
        call_func = self.default_dag_flow_run_decorator(dag_flow)
        return self._init_flow(dag_flow, call_func)

    def _run_dag_flow(self, state: Any, dag_flow: IsDagFlow, *args, **kwargs) -> Any:
        return self._run_flow(state, dag_flow, *args, **kwargs)

    # FuncFlowRunnerEngine

    def _init_func_flow(self, func_flow: IsFuncFlow, call_func: Callable) -> object:
        return self._init_flow(func_flow, call_func)

    def _run_func_flow(self, state: Any, func_flow: IsFuncFlow, *args, **kwargs) -> Any:
        return self._run_flow(state, func_flow, *args, **kwargs)
