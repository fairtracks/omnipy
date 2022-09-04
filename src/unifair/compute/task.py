from __future__ import annotations

import inspect
from types import MappingProxyType
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Tuple, Type, Union

from unifair.util.helpers import create_merged_dict
from unifair.util.param_key_mapper import ParamKeyMapper


class TaskConfig:
    def __init__(self,
                 task_func: Callable,
                 *,
                 name: Optional[str] = None,
                 fixed_params: Optional[Mapping[str, Any]] = None,
                 param_key_map: Optional[Mapping[str, str]] = None,
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

    def get_init_args(self) -> Tuple[Callable]:
        return self._task_func,

    def get_init_kwargs(self) -> Dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in ('name', 'fixed_params', 'param_key_map', 'result_key')
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
        return Task.from_task_template(self)

    def refine(self, update: bool = True, **kwargs: Any) -> TaskTemplate:
        if update:
            for key, cur_val in self.get_init_kwargs().items():
                if key in kwargs:
                    new_val = create_merged_dict(cur_val, kwargs[key]) \
                        if isinstance(cur_val, Mapping) else kwargs[key]
                else:
                    new_val = cur_val
                kwargs[key] = new_val

        return TaskTemplate(self._task_func, **kwargs)


class Task(TaskConfig):
    def __init__(self, *args: Any, **kwargs: Any):  # noqa
        raise RuntimeError('Tasks should only be instantiated using TaskTemplate.apply()')

    @classmethod
    def from_task_template(cls, task_template: TaskTemplate):
        init_args = task_template.get_init_args()
        init_kwargs = task_template.get_init_kwargs()
        task_obj = object.__new__(Task)
        super(Task, task_obj).__init__(*init_args, **init_kwargs)
        return task_obj

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
        return TaskTemplate(*self.get_init_args(), **self.get_init_kwargs())


# TODO: Would we need the possibility to refine task templates by adding new task parameters?
