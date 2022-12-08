from __future__ import annotations

import asyncio
import inspect
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Optional, Tuple, Type, Union

from unifair.compute.job import CallableDecoratingJobTemplateMixin, Job, JobConfig, JobTemplate
from unifair.util.callable_decorator_cls import callable_decorator_cls
from unifair.util.param_key_mapper import ParamKeyMapper


class TaskConfig(JobConfig):
    def __init__(self,
                 task_func: Callable,
                 *,
                 name: Optional[str] = None,
                 fixed_params: Optional[Mapping[str, Any]] = None,
                 param_key_map: Optional[Mapping[str, str]] = None,
                 result_key: Optional[str] = None) -> None:

        name = name if name is not None else task_func.__name__
        super().__init__(name=name)

        self._task_func = task_func
        self._task_func_signature = inspect.signature(self._task_func)
        self._fixed_params = dict(fixed_params) if fixed_params is not None else {}
        self._param_key_mapper = ParamKeyMapper(param_key_map if param_key_map is not None else {})
        self._result_key = result_key

        self._check_param_keys_in_func_signature(self.fixed_params.keys())
        self._check_param_keys_in_func_signature(self.param_key_map.keys())
        if self.result_key is not None:
            self._check_not_empty_string('result_key', self.result_key)

    def _check_param_keys_in_func_signature(self, param_keys: Iterable[str]) -> None:
        for param_key in param_keys:
            if param_key not in self.param_signatures:
                raise KeyError('Parameter "{}" was not found in the '.format(param_key)
                               + 'signature of the task function. Only parameters in the '
                               'signature of the task function are '
                               'allowed as keyword arguments to a Task object.')

    def _get_init_arg_values(self) -> Union[Tuple[()], Tuple[Any, ...]]:
        return self._task_func,

    def _get_init_kwarg_public_property_keys(self) -> Tuple[str, ...]:
        return 'fixed_params', 'param_key_map', 'result_key'

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._task_func)

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._task_func_signature.parameters

    @property
    def return_type(self) -> Type[Any]:
        return self._task_func_signature.return_annotation

    @property
    def fixed_params(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._fixed_params)

    @property
    def param_key_map(self) -> MappingProxyType[str, str]:
        return MappingProxyType(self._param_key_mapper.key_map)

    @property
    def result_key(self) -> Optional[str]:
        return self._result_key


@callable_decorator_cls
class TaskTemplate(CallableDecoratingJobTemplateMixin['TaskTemplate'], JobTemplate, TaskConfig):
    @classmethod
    def _get_job_subcls_for_apply(cls) -> Type[Job]:
        return Task

    @classmethod
    def _apply_engine_decorator(cls, task: Task) -> Task:
        if cls.engine is not None:
            return cls.engine.task_decorator(task)
        else:
            return task


class Task(Job, TaskConfig):
    @classmethod
    def _get_job_config_subcls_for_init(cls) -> Type[JobConfig]:
        return TaskConfig

    @classmethod
    def _get_job_template_subcls_for_revise(cls) -> Type[JobTemplate]:
        return TaskTemplate

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        mapped_fixed_params = self._param_key_mapper.delete_matching_keys(
            self._fixed_params, inverse=True)
        mapped_kwargs = self._param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
            kwargs, inverse=True)
        try:
            if len(mapped_kwargs) < len(kwargs):
                raise TypeError('Keyword arguments {} matches parameter key map inversely.'.format(
                    tuple(set(kwargs.keys()) - set(mapped_kwargs.keys()))))

            result = self._call_func(*args, **mapped_fixed_params, **mapped_kwargs)

        except TypeError as e:
            raise TypeError(
                'Incorrect task function arguments. Current parameter key map contents: {}'.format(
                    self.param_key_map)) from e
        if self._result_key:
            return {self._result_key: result}
        else:
            return result

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        return self._task_func(*args, **kwargs)


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
