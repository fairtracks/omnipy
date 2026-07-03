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

    @staticmethod
    def _wrap_as_prefect_compatible_callable(  # noqa: C901
        call_func: Callable,
        *,
        has_async_func: bool,
        has_generator_func: bool,
        resolve_async_result: bool = False,
    ) -> Callable:
        """Expose the effective function type to Prefect.

        Omnipy's wrappers can hide whether the underlying callable is sync/async and
        plain/generator. Prefect inspects the decorated callable's function type, so we
        rebuild a minimal wrapper with the same effective shape before applying Prefect's
        decorators.
        """
        if has_async_func:
            if has_generator_func:

                async def _async_generator_wrapper(*inner_args, **inner_kwargs):
                    job_result = call_func(*inner_args, **inner_kwargs)
                    sent = None
                    try:
                        while True:
                            sent = yield await job_result.asend(sent)
                    except StopAsyncIteration:
                        return

                return _async_generator_wrapper
            else:

                async def _async_wrapper(*inner_args, **inner_kwargs):
                    result = call_func(*inner_args, **inner_kwargs)
                    if resolve_async_result:
                        return await resolve(result)
                    return await result

                return _async_wrapper
        else:
            if has_generator_func:

                def _sync_generator_wrapper(*inner_args, **inner_kwargs):
                    yield from call_func(*inner_args, **inner_kwargs)

                return _sync_generator_wrapper
            else:

                def _sync_wrapper(*inner_args, **inner_kwargs):
                    return call_func(*inner_args, **inner_kwargs)

                return _sync_wrapper

    # TaskRunnerEngine

    def _init_task(self, task: IsTask, call_func: Callable) -> PrefectTask:  # noqa: C901
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

        wrapped_callable = self._wrap_as_prefect_compatible_callable(
            call_func,
            has_async_func=task.has_async_func(),
            has_generator_func=task.has_generator_func(),
        )

        return prefect_task(**task_kwargs)(wrapped_callable)

    def _run_task(  # noqa: C901
        self,
        state: PrefectTask,
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
            wrapped_callable = self._wrap_as_prefect_compatible_callable(
                _prefect_task,
                has_async_func=_prefect_task.isasync,
                has_generator_func=_prefect_task.isgenerator,
            )

            return prefect_flow(**flow_kwargs)(wrapped_callable)(*args, **kwargs)

    def _init_flow(self, flow: IsAnyFlow, call_func: Callable) -> Callable:  # noqa: C901
        from ..lazy_import import prefect_flow

        assert isinstance(self._config, PrefectEngineConfig)
        flow_kwargs = FlowKwargs(name=flow.name)

        if flow.has_async_func():
            wrapped_callable = self._wrap_as_prefect_compatible_callable(
                call_func,
                has_async_func=True,
                has_generator_func=flow.has_generator_func(),
                resolve_async_result=not flow.has_generator_func(),
            )
            return prefect_flow(**flow_kwargs)(wrapped_callable)
        else:

            # Since it is impossible to find out whether a synchronous
            # FuncFlow might return a generator without running it or
            # inspecting the code, we defensively wrap the call_func into an
            # generator to ensure that Prefect can handle it correctly. The
            # Prefect flow is itself contained in a wrapper funvtion that
            # re-exposes the flow results as-is.
            def _call_func_as_sync_generator_prefect_flow(*inner_args, **inner_kwargs):
                @prefect_flow(**flow_kwargs)
                def _sync_generator_flow(*inner_args, **inner_kwargs):
                    yield call_func(*inner_args, **inner_kwargs)

                for result in _sync_generator_flow(*inner_args, **inner_kwargs):
                    return result

            return _call_func_as_sync_generator_prefect_flow

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
