from abc import ABC, abstractmethod
from functools import wraps
import inspect
from itertools import filterfalse, tee
from typing import Any, Callable, Dict, Iterable, Optional, Type

from unifair.compute.task import TaskTemplate


class TaskWrapper(ABC, TaskTemplate):
    def __init__(self, task: TaskTemplate, **extra_kwargs: Any):
        self._task = task

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...

    def __getattr__(self, item):
        return getattr(self.__dict__['_task'], item)


class DagFlowWrapper(ABC):
    @abstractmethod
    def __init__(self,
                 name: str,
                 tasks: Iterable[Callable],
                 flow_signature: inspect.Signature,
                 flow_kwargs: Dict[str, Any],
                 **_mock_backend_flow_kwargs: Any):
        ...

    @abstractmethod
    def __call__(self, **runtime_kwargs: Any):
        ...


def split_kwargs_by_func_parameters(kwargs: Dict[str, Any], func: Callable):
    func_parameters = set(inspect.signature(func).parameters.keys())

    def is_task_param(item: str):
        key, value = item
        return key in func_parameters

    kwargs_copy_1, kwargs_copy_2 = tee(kwargs.items())
    return dict(filter(is_task_param, kwargs_copy_1)), dict(filterfalse(is_task_param, kwargs_copy_2))


class Engine(ABC):
    def __init__(self,
                 task_wrapper: Type[TaskWrapper],
                 dag_flow_wrapper: Optional[Type[DagFlowWrapper]] = None,
                 cfg_engine: Dict[str, Any] = {}):
        self._task_wrapper = task_wrapper
        self._dag_flow_wrapper = dag_flow_wrapper

    def task_decorator(self, name: str = None, **kwargs: Any) -> Callable:
        def _inner_task_decorator(func: Callable):
            task = TaskTemplate(func, name)
            extra_kwargs = {}
            for key, value in kwargs.items():
                try:
                    task[key] = value
                except KeyError:
                    extra_kwargs[key] = value

            return wraps(func)(self._task_wrapper(task, **extra_kwargs))

        return _inner_task_decorator

    def dag_flow_decorator(self,
                           tasks: Iterable[Callable],
                           name: str = None,
                           **kwargs: Any) -> Callable:
        if self._dag_flow_wrapper is None:
            raise NotImplementedError('DAG flow wrapper is not implemented by engine '
                                      + self.__class__.__name__)

        def _inner_dag_flow_decorator(flow_def: Callable):

            flow_name = name if name is not None else flow_def.__name__
            flow_kwargs, backend_flow_kwargs = split_kwargs_by_func_parameters(kwargs, flow_def)
            flow_signature = inspect.signature(flow_def)

            new_tasks = []
            for i, task in enumerate(tasks):
                last_task = (i == len(tuple(tasks)) - 1)

                def _default_task_decorator(*args, **kwargs):
                    if kwargs:
                        if len(args) > 0:
                            raise TypeError('Tasks may not contain both positional and keyword '
                                            'parameters at runtime. Keyword arguments are reserved '
                                            'for fixed task arguments or internally when running '
                                            'certain flows (defined through task iterators). '
                                            'Positional arguments: {}. '.format(args)
                                            + 'Keyword arguments: {}. '.format(kwargs))
                        else:
                            args = []
                            func_params = inspect.signature(flow_def).parameters
                            for key, param in func_params.items():
                                if param.kind == param.POSITIONAL_OR_KEYWORD:
                                    if key in kwargs:
                                        args.append(kwargs[key])
                                    else:
                                        raise TypeError('Missing parameter "{}" in '
                                                        'kwargs'.format(param.name))
                    ret = task(*args)
                    if not last_task and not isinstance(ret, dict):
                        ret = {'{}_result'.format(task.name): ret}
                    return ret

                new_tasks.append(wraps(task)(_default_task_decorator))

            engine_wrapped_flow = wraps(flow_def)(
                self._dag_flow_wrapper(flow_name,
                                       new_tasks,
                                       flow_signature,
                                       flow_kwargs,
                                       **backend_flow_kwargs))

            def _default_flow_decorator(*args):
                kwargs = {}
                for i, arg in enumerate(args):
                    param = tuple(flow_signature.parameters.values())[i]
                    if param.kind == param.POSITIONAL_OR_KEYWORD:
                        kwargs[param.name] = arg
                    else:
                        raise TypeError('Flow signature for flow named "{}" '.format(flow_name)
                                        + 'has no positional parameters with '
                                        'index {} (for arg with value: {})'.format(i, arg))

                ret = engine_wrapped_flow(**kwargs)
                return ret

            return wraps(engine_wrapped_flow)(_default_flow_decorator)

        return _inner_dag_flow_decorator

    # @staticmethod
    # @abstractmethod
    # def result_persisting_task_decorator(result_dir: str) -> Callable:
    #     pass
    #
    # @staticmethod
    # @abstractmethod
    # def flow_decorator() -> Callable:
    #     pass
    #
    # @staticmethod
    # @abstractmethod
    # def executable_task_decorator() -> Callable:
    #     pass


class Runtime:
    def __init__(self):
        self._engine = None
        self.execution_mode = 'flow'
        self.flow_mode = 'list'
        self._result_dir = None

    def set_engine(self, engine: Engine):
        self._engine = engine

    def set_result_persistence(self, result_dir: str):
        assert result_dir
        self._result_dir = result_dir

    def get_task_decorators(self):
        task_decorators = []

        if self._result_dir:
            task_decorators.append(self._engine.result_persisting_task_decorator(self._result_dir))
        else:
            task_decorators.append(self._engine.task_decorator())

        if self._execution_mode == 'task':
            task_decorators.append(self._engine.executable_task_decorator())

        return task_decorators

    def set_execution_mode(self, mode='flow'):
        assert mode in ['task', 'flow']
        self._execution_mode = mode

    def get_flow_decorators(self):
        return [self._engine.flow_decorator()]

    def set_flow_mode(self, flow_mode):
        assert flow_mode in ['list', 'function']
        self._flow_mode = flow_mode


def runtime_task_decorator(runtime: Runtime):
    class RuntimeTaskDecorator:
        def __init__(self, _task_func: Callable, _runtime: Runtime = runtime):
            self._task_func = _task_func
            self._runtime = _runtime

        def __call__(self, input=None):
            decorated_func = self._task_func
            for decorator in self._runtime.get_task_decorators():
                decorated_func = decorator(decorated_func)

            if input:
                return decorated_func(input)
            else:
                return decorated_func()

    return RuntimeTaskDecorator


def runtime_flow_decorator(runtime: Runtime):
    class RuntimeFlowDecorator:
        def __init__(self, _flow_func: Callable, _runtime: Runtime = runtime):
            self._flow_func = _flow_func
            self._runtime = _runtime

        def __call__(self):
            decorated_func = self._flow_func
            for decorator in self._runtime.get_flow_decorators():
                decorated_func = decorator(decorated_func)
            return decorated_func()

    return RuntimeFlowDecorator
