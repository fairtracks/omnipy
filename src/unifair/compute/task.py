from __future__ import annotations

import inspect
from types import MappingProxyType
from typing import Any, Callable, Dict, Optional, Type, Union


class TaskConfig:
    def __init__(self,
                 task_func: Callable,
                 name: str = None,
                 param_map_keys: Optional[Dict[str, str]] = None,
                 result_key: Optional[str] = None,
                 fixed_params: Optional[Dict[str, Any]] = None) -> None:
        self._task_func = task_func
        self._task_func_signature = inspect.signature(self._task_func)

        self._name = name if name is not None else task_func.__name__
        self._param_map_keys = param_map_keys if param_map_keys is not None else {}
        self._result_key = result_key
        self._fixed_params = fixed_params if fixed_params is not None else {}

        self._check_param_keys_in_func_signature()

    def _check_param_keys_in_func_signature(self):
        for param_key in self._fixed_params.keys():
            if param_key not in self.param_signatures:
                raise KeyError('Parameter "{}" was not found in the '.format(param_key)
                               + 'signature of the task function. Only parameters in the '
                               'signature of the task function are '
                               'allowed as keyword arguments to a Task object.')

    def _get_init_params(self) -> Dict[str, Any]:
        return {
            'task_func': self._task_func,
            'name': self.name,
            'param_map_keys': self.param_map_keys,
            'result_key': self.result_key,
            'fixed_params': self.fixed_params,
        }

    @property
    def param_signatures(self) -> MappingProxyType:
        return self._task_func_signature.parameters

    @property
    def return_type(self) -> Union[Type[Any]]:
        return self._task_func_signature.return_annotation

    @property
    def name(self):
        return self._name

    @property
    def param_map_keys(self):
        return MappingProxyType(self._param_map_keys)

    @property
    def result_key(self):
        return self._result_key

    @property
    def fixed_params(self):
        return MappingProxyType(self._fixed_params)


class TaskTemplate(TaskConfig):
    def apply(self, **engine_kwargs: Any) -> Task:
        return Task(**self._get_init_params())


class Task(TaskConfig):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._task_func(*args, **self._fixed_params, **kwargs)

    def revise(self) -> TaskTemplate:
        return TaskTemplate(**self._get_init_params())
