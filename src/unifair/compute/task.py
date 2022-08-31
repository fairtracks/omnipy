from __future__ import annotations

import inspect
from types import MappingProxyType
from typing import Any, Callable, Dict, Iterable, Optional, Type, Union

from unifair.util.helpers import create_merged_dict
from unifair.util.param_key_mapper import ParamKeyMapper


class TaskConfig:
    def __init__(self,
                 task_func: Callable,
                 name: Optional[str] = None,
                 fixed_params: Optional[Dict[str, Any]] = None,
                 param_key_map: Optional[Dict[str, str]] = None,
                 result_key: Optional[str] = None) -> None:
        self._task_func = task_func
        self._task_func_signature = inspect.signature(self._task_func)
        self._name = name if name is not None else task_func.__name__
        self._fixed_params = dict(fixed_params) if fixed_params is not None else {}
        self._param_key_mapper = ParamKeyMapper(param_key_map if param_key_map is not None else {})
        self._result_key = result_key

        self._check_not_empty_string('name', self.name)
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

    @staticmethod
    def _check_not_empty_string(param_name: str, param: str) -> None:
        if len(param) == 0:
            raise ValueError('Empty strings not allowed for parameter "{}"'.format(param_name))

    def _get_init_params(self) -> Dict[str, Any]:
        return {
            'task_func': self._task_func,
            'name': self.name,
            'param_key_map': self.param_key_map,
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
    def name(self) -> str:
        return self._name

    @property
    def fixed_params(self) -> MappingProxyType[str, Any]:
        return MappingProxyType(self._fixed_params)

    @property
    def param_key_map(self) -> MappingProxyType[str, str]:
        return MappingProxyType(self._param_key_mapper.key_map)

    @property
    def result_key(self) -> Optional[str]:
        return self._result_key


class TaskTemplate(TaskConfig):
    def apply(self, **engine_kwargs: Any) -> Task:
        return Task(**self._get_init_params())

    def refine(self,
               name: Optional[str] = None,
               fixed_params: Optional[Union[Dict[str, Any], MappingProxyType[str, Any]]] = None,
               param_key_map: Optional[Union[Dict[str, str], MappingProxyType[str, str]]] = None,
               result_key: Optional[str] = None,
               update: bool = True) -> TaskTemplate:
        param_key_map = {} if param_key_map is None else param_key_map
        fixed_params = {} if fixed_params is None else fixed_params
        if update:
            name = self.name if name is None else name
            fixed_params = create_merged_dict(self.fixed_params, fixed_params)
            param_key_map = create_merged_dict(self.param_key_map, param_key_map)
            result_key = self.result_key if result_key is None else result_key

        return TaskTemplate(
            self._task_func,
            name=name,
            fixed_params=fixed_params,
            param_key_map=param_key_map,
            result_key=result_key)


class Task(TaskConfig):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        mapped_fixed_params = self._param_key_mapper.delete_matching_keys(
            self._fixed_params, inverse=True)
        mapped_kwargs = self._param_key_mapper.map_matching_keys_delete_inverse_matches_keep_rest(
            kwargs, inverse=True)

        try:
            result = self._task_func(*args, **mapped_fixed_params, **mapped_kwargs)
        except TypeError as e:
            raise TypeError(
                'Incorrect task function arguments. Current parameter key map contents: {}'.format(
                    self.param_key_map)) from e
        if self._result_key:
            return {self._result_key: result}
        else:
            return result

    @staticmethod
    def _map_params(params: Dict[str, Any], key_map: Dict[str, str]) -> Dict[str, Any]:
        return {key_map[key] if key in key_map else key: params[key] for key in params}

    def revise(self) -> TaskTemplate:
        return TaskTemplate(**self._get_init_params())
