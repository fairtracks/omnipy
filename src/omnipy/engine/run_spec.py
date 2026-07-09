from abc import ABC, abstractmethod
from datetime import datetime
import inspect
from inspect import BoundArguments
from logging import INFO
from types import MappingProxyType
from typing import Any, Callable, cast

from omnipy.shared.protocols.compute._job import IsFuncArgJob, IsTaskTemplateArgsJob
from omnipy.shared.protocols.compute.job import IsAnyFlow, IsTask, IsTaskTemplate
from omnipy.util.callable_types import callable_type_from_flags, decorate_callable_by_type


class JobRunSpec(ABC):
    def __init__(self, job: IsFuncArgJob, run_callable: Callable) -> None:
        self._job = job
        self._run_callable = run_callable

    @property
    def name(self) -> str:
        return self._job.name

    @property
    def param_signatures(self) -> MappingProxyType[str, inspect.Parameter]:
        return self._job.param_signatures

    @property
    def return_type(self) -> type:
        return self._job.return_type

    def has_async_func(self) -> bool:
        return self._job.has_async_func()

    def has_generator_func(self) -> bool:
        return self._job.has_generator_func()

    def log(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None) -> None:
        self._job.log(log_msg, level=level, datetime_obj=datetime_obj)

    @abstractmethod
    def create_default_run_callable(self) -> Callable:
        ...


class TaskRunSpec(JobRunSpec):
    @property
    def in_flow_context(self) -> bool:
        task = cast(IsTask, self._job)
        return task.in_flow_context

    def create_default_run_callable(self) -> Callable:
        return self._run_callable


class FlowRunSpec(JobRunSpec, ABC):
    @property
    def flow_context(self):
        flow = cast(IsAnyFlow, self._job)
        return flow.flow_context

    def get_bound_args(self, *args: object, **kwargs: object) -> BoundArguments:
        flow = cast(IsAnyFlow, self._job)
        return flow.get_bound_args(*args, **kwargs)

    def create_default_run_callable(self) -> Callable:
        return decorate_callable_by_type(
            self._create_default_run_callable(),
            self.param_signatures,
            self.return_type,
            callable_type_from_flags(
                has_async=self.has_async_func(),
                has_generator=self.has_generator_func(),
            ),
            context_factory=lambda: self.flow_context,
        )

    @abstractmethod
    def _create_default_run_callable(self) -> Callable:
        ...


class TaskTemplateArgsFlowRunSpec(FlowRunSpec, ABC):
    @property
    def task_templates(self) -> tuple[IsTaskTemplate, ...]:
        flow = cast(IsTaskTemplateArgsJob[IsTaskTemplate, Any, Any, Any, Any], self._job)
        return flow.task_templates


class LinearFlowRunSpec(TaskTemplateArgsFlowRunSpec):
    def _create_default_run_callable(self) -> Callable:
        def _inner_run_linear_flow(*args: object, **kwargs: object):
            result = None
            for i, job in enumerate(self.task_templates):
                # TODO: Better handling of kwargs
                if i == 0:
                    result = job(*args, **kwargs)
                else:
                    result = job(*args)

                args = (result,)
            return result

        return _inner_run_linear_flow


class DagFlowRunSpec(TaskTemplateArgsFlowRunSpec):
    def _create_default_run_callable(self) -> Callable:  # noqa: C901
        def _inner_run_dag_flow(*args: object, **kwargs: object):
            results = {}
            result = None
            for i, job in enumerate(self.task_templates):
                if i == 0:
                    results = self.get_bound_args(*args, **kwargs).arguments

                param_keys = set(inspect.signature(job).parameters.keys())

                # TODO: Refactor to remove dependency
                #       Also, add test for not allowing override of fixed_params
                if hasattr(job, 'param_key_map'):
                    for key, val in job.param_key_map.items():
                        if key in param_keys:
                            param_keys.remove(key)
                            param_keys.add(val)

                if hasattr(job, 'fixed_params'):
                    for key in job.fixed_params.keys():
                        if key in param_keys:
                            param_keys.remove(key)

                params = {key: val for key, val in results.items() if key in param_keys}
                result = job(**params)

                if isinstance(result, dict) and len(result) > 0:
                    results.update(result)
                else:
                    results[job.name] = result
            return result

        return _inner_run_dag_flow


class FuncFlowRunSpec(FlowRunSpec):
    def _create_default_run_callable(self) -> Callable:
        return self._run_callable
