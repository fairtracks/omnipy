"""Engine-facing run-spec adapters for tasks and flows.

Run-spec objects expose a uniform view of Omnipy jobs so execution engines can
initialize them, wrap their callables, and execute them without depending on the
full job implementation details.
"""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from datetime import datetime
import inspect
from inspect import BoundArguments
from logging import INFO
from types import MappingProxyType
from typing import Any, Callable, cast, Generator

from omnipy.shared.protocols.compute.job import (IsAnyFlow,
                                                 IsChildJobListArgJob,
                                                 IsFuncArgJob,
                                                 IsFuncArgJobTemplate,
                                                 IsTask)
from omnipy.util.callable_types import CallableType, decorate_callable_by_type
from omnipy.util.helpers import resolve


def _has_any_async_coroutine_jobs(flow_run_spec: 'ChildJobListArgFlowRunSpec') -> bool:
    return any(job.callable_type is CallableType.ASYNC_COROUTINE
               for job in flow_run_spec.child_job_templates)


def _keyword_param_keys_for_job(job: IsFuncArgJobTemplate,
                                positional_arg_count: int = 0) -> set[str]:
    signature_params = list(inspect.signature(job).parameters.values())

    keyword_param_keys = {
        param.name
        for param in signature_params
        if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    }

    positional_params = [
        param for param in signature_params
        if param.kind in (inspect.Parameter.POSITIONAL_ONLY,
                          inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    consumed_positional_kw_keys = {
        param.name
        for param in positional_params[:positional_arg_count]
        if param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    }
    keyword_param_keys.difference_update(consumed_positional_kw_keys)

    param_key_map = job.param_key_map if hasattr(job, 'param_key_map') else {}
    mapped_keyword_param_keys = {
        param_key_map.get(param_key, param_key) for param_key in keyword_param_keys
    }

    if hasattr(job, 'fixed_params'):
        fixed_keys = {
            param_key_map.get(param_key, param_key) for param_key in job.fixed_params.keys()
        }
        mapped_keyword_param_keys.difference_update(fixed_keys)

    return mapped_keyword_param_keys


def _collect_matching_kwargs_for_job(job: IsFuncArgJobTemplate,
                                     kwargs: Mapping[str, object],
                                     positional_arg_count: int = 0) -> dict[str, object]:
    param_keys = _keyword_param_keys_for_job(job, positional_arg_count)
    return {key: val for key, val in kwargs.items() if key in param_keys}


def _drain_sync_results(run_tasks_gen: Generator[object, object, object]) -> object:
    try:
        result = next(run_tasks_gen)
        while True:
            result = run_tasks_gen.send(result)
    except StopIteration as exc:
        return exc.value


async def _drain_async_results(
    run_tasks_gen: Generator[object, object, object],
    resolve_result_func: Callable[[object], Any] = resolve,
) -> object:
    try:
        result = next(run_tasks_gen)
        while True:
            result = await resolve_result_func(result)
            result = run_tasks_gen.send(result)
    except StopIteration as exc:
        return exc.value


class JobRunSpec(ABC):
    """Base adapter exposing engine-facing metadata and callables for a job."""

    def __init__(self, job: IsFuncArgJob, run_callable: Callable) -> None:
        self._job = job
        self._run_callable = run_callable

    @property
    def name(self) -> str:
        """Proxies to the wrapped job's display name.

        See :attr:`~omnipy.shared.protocols.compute.mixins.IsUniquelyNamedJob.name`.
        """
        return self._job.name

    @property
    def unique_name(self) -> str:
        """Proxies to the wrapped job's unique registry name.

        See :attr:`~omnipy.shared.protocols.compute.mixins.IsUniquelyNamedJob.unique_name`.
        """
        return self._job.unique_name

    @property
    def unique_run_slug(self) -> str:
        """Proxies to the wrapped job's run-specific slug.

        See :attr:`~omnipy.shared.protocols.compute.mixins.IsUniquelyNamedJob.unique_run_slug`.
        """
        return self._job.unique_run_slug

    @property
    def param_signatures(self) -> MappingProxyType[str, inspect.Parameter]:
        """Proxies to the wrapped job's callable parameter metadata.

        See :attr:`~omnipy.shared.protocols.compute.job.IsFuncArgJobBase.param_signatures`.
        """
        return self._job.param_signatures

    @property
    def return_type(self) -> type:
        """Proxies to the wrapped job's annotated return type.

        See :attr:`~omnipy.shared.protocols.compute.job.IsFuncArgJobBase.return_type`.
        """
        return self._job.return_type

    @property
    def callable_type(self) -> CallableType.Literals:
        """Proxies to the wrapped job's callable-shape classification.

        See :attr:`~omnipy.shared.protocols.compute.job.IsFuncArgJobBase.callable_type`.
        """
        return self._job.callable_type

    def log(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None) -> None:
        """Proxies log messages to the wrapped job.

        See :meth:`~omnipy.shared.protocols.hub.log.CanLog.log`.
        """
        self._job.log(log_msg, level=level, datetime_obj=datetime_obj)

    @abstractmethod
    def create_default_run_callable(self) -> Callable:
        """Build the default callable that engines should initialize and execute.

        Returns:
            Callable: Engine-facing callable for running the wrapped job.
        """
        ...


class TaskRunSpec(JobRunSpec):
    """Run-spec adapter for applied tasks."""

    @property
    def in_flow_context(self) -> bool:
        """Proxies whether the wrapped task is running inside a flow.

        See :attr:`~omnipy.shared.protocols.compute.job.IsJobBase.in_flow_context`.
        """
        task = cast(IsTask, self._job)
        return task.in_flow_context

    def create_default_run_callable(self) -> Callable:
        """Return the task callable exactly as supplied to the run spec.

        Returns:
            Callable: Underlying task callable to hand to the engine.
        """
        return self._run_callable


class FlowRunSpec(JobRunSpec, ABC):
    """Base run-spec adapter for flow jobs."""

    @property
    def flow_context(self):
        """Proxies the wrapped flow's nested execution context.

        See :attr:`~omnipy.shared.protocols.compute.job.IsFlow.flow_context`.
        """
        flow = cast(IsAnyFlow, self._job)
        return flow.flow_context

    def get_bound_args(self, *args: object, **kwargs: object) -> BoundArguments:
        """Proxies argument binding to the wrapped flow callable.

        See :meth:`~omnipy.shared.protocols.compute.job.IsFuncArgJobBase.get_bound_args`.
        """
        flow = cast(IsAnyFlow, self._job)
        return flow.get_bound_args(*args, **kwargs)

    def create_default_run_callable(self) -> Callable:
        """Wrap the flow callable with its declared callable shape and flow context.

        Returns:
            Callable: Engine-facing flow callable that enters :attr:`flow_context`.
        """
        return decorate_callable_by_type(
            self._create_default_run_callable(),
            self.param_signatures,
            self.return_type,
            self.callable_type,
            context_factory=lambda: self.flow_context,
        )

    @abstractmethod
    def _create_default_run_callable(self) -> Callable:
        ...


class ChildJobListArgFlowRunSpec(FlowRunSpec, ABC):
    """Base run spec for flows defined by ordered child-job templates."""

    @property
    def child_job_templates(self) -> tuple[IsFuncArgJobTemplate, ...]:
        """Proxies the wrapped flow's ordered child templates.

        See :attr:`~omnipy.shared.protocols.compute.job.IsChildJobListArgJobBase.child_job_templates`.
        """
        flow = cast(IsChildJobListArgJob, self._job)
        return flow.child_job_templates


class LinearFlowRunSpec(ChildJobListArgFlowRunSpec):
    """Run spec for linear flows that pipe each child result into the next."""

    def _create_default_run_callable(self) -> Callable:
        def _run_all_linear_tasks(
            *args: object,
            **kwargs: object,
        ) -> Generator[object, object, object]:
            flow_kwargs = self.get_bound_args(*args, **kwargs).arguments
            result = None
            for i, job in enumerate(self.child_job_templates):
                call_args = args if i == 0 else (result,)
                task_kwargs = _collect_matching_kwargs_for_job(job, flow_kwargs, len(call_args))
                result = job(*call_args, **task_kwargs)

                result = yield result

                args = (result,)

            return result

        if _has_any_async_coroutine_jobs(self):

            async def _async_inner_run_linear_flow(*args: object, **kwargs: object):
                return await _drain_async_results(_run_all_linear_tasks(*args, **kwargs))

            return _async_inner_run_linear_flow
        else:

            def _sync_inner_run_linear_flow(*args: object, **kwargs: object):
                return _drain_sync_results(_run_all_linear_tasks(*args, **kwargs))

            return _sync_inner_run_linear_flow


class DagFlowRunSpec(ChildJobListArgFlowRunSpec):
    """Run spec for DAG flows that route named results into downstream inputs."""

    def _create_default_run_callable(self) -> Callable:  # noqa: C901
        def _run_all_dag_tasks(
            *args: object,
            **kwargs: object,
        ) -> Generator[object, object, object]:
            results = {}
            result = None

            for i, job in enumerate(self.child_job_templates):
                if i == 0:
                    results = self.get_bound_args(*args, **kwargs).arguments

                params = _collect_matching_kwargs_for_job(job, results)
                result = job(**params)

                result = yield result

                if isinstance(result, dict) and len(result) > 0:
                    results.update(result)
                else:
                    results[job.name] = result

            return result

        if _has_any_async_coroutine_jobs(self):

            async def _async_inner_run_dag_flow(*args: object, **kwargs: object):
                async def _resolve_awaitable_dag_task_result(result: object) -> object:
                    result = await resolve(result)

                    if isinstance(result, dict) and len(result) > 0:
                        result = {key: await resolve(val) for key, val in result.items()}

                    return result

                return await _drain_async_results(
                    _run_all_dag_tasks(*args, **kwargs),
                    _resolve_awaitable_dag_task_result,
                )

            return _async_inner_run_dag_flow
        else:

            def _sync_inner_run_dag_flow(*args: object, **kwargs: object):
                return _drain_sync_results(_run_all_dag_tasks(*args, **kwargs))

            return _sync_inner_run_dag_flow


class FuncFlowRunSpec(FlowRunSpec):
    """Run spec for callable-backed flows that execute a single wrapped callable."""

    def _create_default_run_callable(self) -> Callable:
        return self._run_callable
