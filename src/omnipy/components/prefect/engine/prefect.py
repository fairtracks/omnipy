from datetime import timedelta
import inspect
from logging import WARNING
from types import MappingProxyType
from typing import Any, Callable, Type, TypedDict

from omnipy.config.engine import PrefectEngineConfig
from omnipy.engine.job_runner import (DagFlowRunnerEngine,
                                      FuncFlowRunnerEngine,
                                      LinearFlowRunnerEngine,
                                      TaskRunnerEngine)
from omnipy.engine.run_spec import FlowRunSpec, TaskRunSpec
from omnipy.shared.protocols.config import IsPrefectEngineConfig
from omnipy.shared.typing import TYPE_CHECKING
from omnipy.util.callable_types import (callable_type_from_flags,
                                        CallableType,
                                        decorate_callable_by_type,
                                        GeneratorCallableType)

if TYPE_CHECKING:
    from ..lazy_import import CachePolicy, NotSet, PrefectTask


class TaskKwargs(TypedDict, total=False):
    name: str
    cache_policy: CachePolicy | type[NotSet]
    cache_expiration: timedelta | None


class FlowKwargs(TypedDict, total=False):
    name: str
    flow_run_name: str


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
    def _wrap_as_prefect_compatible_callable(
        call_func: Callable,
        param_signatures: MappingProxyType[str, inspect.Parameter],
        return_type: type,
        *,
        callable_type: CallableType.Literals,
        resolve_async_result: bool = False,
    ) -> Callable:
        """Expose the effective function type to Prefect.

        Omnipy's wrappers can hide whether the underlying callable is sync/async and
        plain/generator. Prefect inspects the decorated callable's function type, so we
        rebuild a minimal wrapper with the same effective shape before applying Prefect's
        decorators.
        """
        return decorate_callable_by_type(
            call_func,
            param_signatures,
            return_type,
            callable_type,
            resolve_async_result=resolve_async_result,
        )

    # TaskRunnerEngine

    def _init_task(self, task: TaskRunSpec) -> PrefectTask:
        from ..lazy_import import cache_policies, prefect_task

        assert isinstance(self._config, PrefectEngineConfig)
        task_kwargs = TaskKwargs(name=task.name)

        if self._config.use_cached_results and task.callable_type in GeneratorCallableType:
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
            task.create_default_run_callable(),
            task.param_signatures,
            task.return_type,
            callable_type=task.callable_type,
        )

        return prefect_task(**task_kwargs)(wrapped_callable)

    def _run_task(
        self,
        state: PrefectTask,
        task: TaskRunSpec,
        *args,
        **kwargs,
    ) -> object:
        from ..lazy_import import prefect_flow

        _prefect_task = state

        if task.in_flow_context:
            return _prefect_task(*args, **kwargs)
        else:
            flow_kwargs = FlowKwargs(
                name=task.name,
                flow_run_name=task.unique_run_slug,
            )
            wrapped_callable = self._wrap_as_prefect_compatible_callable(
                _prefect_task,
                task.param_signatures,
                task.return_type,
                callable_type=callable_type_from_flags(
                    is_async=_prefect_task.isasync,
                    is_generator=_prefect_task.isgenerator,
                ),
            )

            return prefect_flow(**flow_kwargs)(wrapped_callable)(*args, **kwargs)

    def _init_flow(self, flow: FlowRunSpec) -> Callable:
        from ..lazy_import import prefect_flow

        assert isinstance(self._config, PrefectEngineConfig)
        flow_kwargs = FlowKwargs(
            name=flow.name,
            flow_run_name=flow.unique_run_slug,
        )
        run_callable = flow.create_default_run_callable()

        wrapped_callable = self._wrap_as_prefect_compatible_callable(
            run_callable,
            flow.param_signatures,
            flow.return_type,
            callable_type=flow.callable_type,
            resolve_async_result=flow.callable_type not in GeneratorCallableType,
        )
        return prefect_flow(**flow_kwargs)(wrapped_callable)

    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> Any:
        _prefect_flow = state
        return _prefect_flow(*args, **kwargs)
