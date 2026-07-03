from datetime import timedelta
from logging import WARNING
from typing import Any, Callable, Type, TypedDict

from omnipy.config.engine import PrefectEngineConfig
from omnipy.engine.job_runner import (DagFlowRunnerEngine,
                                      FuncFlowRunnerEngine,
                                      LinearFlowRunnerEngine,
                                      TaskRunnerEngine)
from omnipy.shared.protocols.compute.job import (IsAnyFlow,
                                                 IsDagFlow,
                                                 IsFlow,
                                                 IsFuncFlow,
                                                 IsLinearFlow,
                                                 IsTask)
from omnipy.shared.protocols.config import IsPrefectEngineConfig
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.helpers import resolve

if TYPE_CHECKING:
    from ..lazy_import import PrefectTask


class FlowKwargs(TypedDict):
    name: str


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

    def _init_task(self, task: IsTask, call_func: Callable) -> 'PrefectTask':  # noqa: C901
        from ..lazy_import import cache_policies, prefect_task

        assert isinstance(self._config, PrefectEngineConfig)
        task_kwargs: dict[str, Any] = dict(name=task.name)

        if self._config.use_cached_results and task.has_generator_func():
            task.log(
                'NOTE: Cache-key computation for Prefect tasks traverses task parameters '
                'and will consume generator inputs. To disable caching of task parameters, set '
                '`runtime.config.engine.prefect.use_cached_results` to `False`.',
                level=WARNING)

        if self._config.use_cached_results:
            task_kwargs['cache_policy'] = cache_policies.DEFAULT
            task_kwargs['cache_expiration'] = timedelta(days=1)
        else:
            task_kwargs['cache_policy'] = cache_policies.NO_CACHE

        if task.has_async_func():

            if task.has_generator_func():

                @prefect_task(**task_kwargs)
                async def _async_generator_task(*inner_args, **inner_kwargs):
                    try:
                        job_result = call_func(*inner_args, **inner_kwargs)
                        value = yield await anext(job_result)
                        while True:
                            value = yield await job_result.asend(value)
                    except StopAsyncIteration:
                        pass

                return _async_generator_task
            else:

                @prefect_task(**task_kwargs)
                async def _async_task(*inner_args, **inner_kwargs):
                    return await call_func(*inner_args, **inner_kwargs)

                return _async_task

        else:
            if task.has_generator_func():

                @prefect_task(**task_kwargs)
                def _sync_generator_task(*inner_args, **inner_kwargs):
                    try:
                        job_result = call_func(*inner_args, **inner_kwargs)
                        value = yield next(job_result)
                        while True:
                            value = yield job_result.send(value)
                    except StopIteration:
                        pass

                return _sync_generator_task
            else:

                @prefect_task(**task_kwargs)
                def _sync_task(*inner_args, **inner_kwargs):
                    return call_func(*inner_args, **inner_kwargs)

                return _sync_task

    def _run_task(  # noqa: C901
        self,
        state: 'PrefectTask',
        task: IsTask,
        call_func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        from ..lazy_import import prefect_flow

        _prefect_task = state

        if task.in_flow_context:
            return _prefect_task(*args, **kwargs)
        else:
            flow_kwargs = FlowKwargs(name=task.name)

            if _prefect_task.isasync:
                if _prefect_task.isgenerator:

                    @prefect_flow(**flow_kwargs)
                    async def _async_generator_task_flow(*inner_args, **inner_kwargs):
                        try:
                            job_result = _prefect_task(*inner_args, **inner_kwargs)
                            value = yield await anext(job_result)
                            while True:
                                value = yield await job_result.asend(value)
                        except StopAsyncIteration:
                            pass

                    return _async_generator_task_flow(*args, **kwargs)
                else:

                    @prefect_flow(**flow_kwargs)
                    async def _async_task_flow(*inner_args, **inner_kwargs):
                        return await resolve(_prefect_task(*inner_args, **inner_kwargs))

                    return _async_task_flow(*args, **kwargs)

            else:
                if _prefect_task.isgenerator:

                    @prefect_flow(**flow_kwargs)
                    def _sync_generator_task_flow(*inner_args, **inner_kwargs):
                        try:
                            job_result = _prefect_task(*inner_args, **inner_kwargs)
                            value = yield next(job_result)
                            while True:
                                value = yield job_result.send(value)
                        except StopIteration:
                            pass

                    return _sync_generator_task_flow(*args, **kwargs)
                else:

                    @prefect_flow(**flow_kwargs)
                    def _sync_task_flow(*inner_args, **inner_kwargs):
                        return _prefect_task(*inner_args, **inner_kwargs)

                    return _sync_task_flow(*args, **kwargs)

    def _init_flow(self, flow: IsAnyFlow, call_func: Callable) -> Any:  # noqa: C901
        from ..lazy_import import prefect_flow

        assert isinstance(self._config, PrefectEngineConfig)
        flow_kwargs = FlowKwargs(name=flow.name)

        if flow.has_async_func():
            if flow.has_generator_func():

                @prefect_flow(**flow_kwargs)
                async def _async_generator_flow(*inner_args, **inner_kwargs):
                    try:
                        job_result = call_func(*inner_args, **inner_kwargs)
                        value = yield await anext(job_result)
                        while True:
                            value = yield await job_result.asend(value)
                    except StopAsyncIteration:
                        pass

                return _async_generator_flow
            else:

                @prefect_flow(**flow_kwargs)
                async def _async_flow(*inner_args, **inner_kwargs):
                    return await resolve(call_func(*inner_args, **inner_kwargs))

                return _async_flow
        else:

            def _sync_auto_flow(*inner_args, **inner_kwargs):
                @prefect_flow(**flow_kwargs)
                def _sync_generator_flow(*inner_args, **inner_kwargs):
                    yield call_func(*inner_args, **inner_kwargs)

                for result in _sync_generator_flow(*inner_args, **inner_kwargs):
                    return result

            return _sync_auto_flow

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
        call_func = self.default_func_flow_run_decorator(func_flow, call_func)
        return self._init_flow(func_flow, call_func)

    def _run_func_flow(
        self,
        state: Any,
        func_flow: IsFuncFlow,
        call_func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        return self._run_flow(state, func_flow, *args, **kwargs)
