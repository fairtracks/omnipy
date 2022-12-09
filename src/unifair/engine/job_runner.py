from abc import ABC, abstractmethod
import inspect
import sys
from types import AsyncGeneratorType, GeneratorType
from typing import Any, Awaitable, Callable, cast, Iterable

from unifair.engine.base import Engine
from unifair.engine.constants import RunState
from unifair.engine.protocols import IsDagFlow, IsFuncFlow, IsJob, IsLinearFlow, IsTask


class JobRunnerEngine(Engine, ABC):
    def _register_job_state(self, job: IsJob, state: RunState) -> None:
        if self._registry:
            self._registry.set_job_state(job, state)

    def _decorate_result_with_job_finalization_detector(self, job: IsJob, job_result: object):
        if isinstance(job_result, GeneratorType):
            job_result = cast(GeneratorType, job_result)

            def detect_finished_generator_decorator():
                try:
                    value = yield next(job_result)
                    while True:
                        value = yield job_result.send(value)
                except StopIteration:
                    self._register_job_state(job, RunState.FINISHED)

            return detect_finished_generator_decorator()
        elif isinstance(job_result, AsyncGeneratorType):
            job_result = cast(AsyncGeneratorType, job_result)

            async def detect_finished_async_generator_decorator():
                try:
                    if sys.version_info >= (3, 10):
                        value = yield await anext(job_result)
                    else:
                        value = yield await job_result.__anext__()
                    while True:
                        print(value)
                        value = yield await job_result.asend(value)
                except StopAsyncIteration:
                    self._register_job_state(job, RunState.FINISHED)

            return detect_finished_async_generator_decorator()

        elif inspect.isawaitable(job_result):
            job_result = cast(Awaitable, job_result)

            async def detect_finished_coroutine():
                result = await job_result
                self._register_job_state(job, RunState.FINISHED)
                return result

            return detect_finished_coroutine()
        else:
            self._register_job_state(job, RunState.FINISHED)
            return job_result


class TaskRunnerEngine(JobRunnerEngine):
    def task_decorator(self, task: IsTask) -> IsTask:
        prev_call_func = task._call_func  # noqa
        self._register_job_state(task, RunState.INITIALIZED)
        state = self._init_task(task, prev_call_func)

        def _call_func(*args: Any, **kwargs: Any) -> Any:
            self._register_job_state(task, RunState.RUNNING)
            task_result = self._run_task(state, task, prev_call_func, *args, **kwargs)
            return self._decorate_result_with_job_finalization_detector(task, task_result)

        setattr(task, '_call_func', _call_func)
        return task

    @abstractmethod
    def _init_task(self, task: IsTask, call_func: Callable) -> Any:
        ...

    @abstractmethod
    def _run_task(self, state: Any, task: IsTask, call_func: Callable, *args, **kwargs) -> Any:
        ...


class LinearFlowRunnerEngine(JobRunnerEngine):
    def linear_flow_decorator(self, linear_flow: IsLinearFlow) -> IsLinearFlow:
        # prev_call_func = flow._call_func  # Only raises error anyway

        self._register_job_state(linear_flow, RunState.INITIALIZED)
        state = self._init_linear_flow(linear_flow)

        def _call_func(*args: object, **kwargs: object) -> Any:
            self._register_job_state(linear_flow, RunState.RUNNING)
            flow_result = self._run_linear_flow(state, linear_flow, *args, **kwargs)
            return self._decorate_result_with_job_finalization_detector(linear_flow, flow_result)

        setattr(linear_flow, '_call_func', _call_func)
        return linear_flow

    @staticmethod
    def default_linear_flow_run_decorator(linear_flow: IsLinearFlow) -> Any:
        def _inner_run_linear_flow(*args: object, **kwargs: object):

            result = None
            for i, job in enumerate(linear_flow.task_templates):
                with linear_flow.flow_context:
                    # TODO: Better handling or kwargs
                    if i == 0:
                        result = job(*args, **kwargs)
                    else:
                        result = job(*args)

                args = result if isinstance(result, Iterable) else [result]
            return result

        return _inner_run_linear_flow

    @abstractmethod
    def _init_linear_flow(self, linear_flow: IsLinearFlow) -> Any:
        ...

    @abstractmethod
    def _run_linear_flow(self, state: Any, linear_flow: IsLinearFlow, *args, **kwargs) -> Any:
        ...


class DagFlowRunnerEngine(JobRunnerEngine):
    def dag_flow_decorator(self, dag_flow: IsDagFlow) -> IsDagFlow:
        # prev_call_func = flow._call_func  # Only raises error anyway

        self._register_job_state(dag_flow, RunState.INITIALIZED)
        state = self._init_dag_flow(dag_flow)

        def _call_func(*args: object, **kwargs: object) -> Any:
            self._register_job_state(dag_flow, RunState.RUNNING)
            flow_result = self._run_dag_flow(state, dag_flow, *args, **kwargs)
            return self._decorate_result_with_job_finalization_detector(dag_flow, flow_result)

        setattr(dag_flow, '_call_func', _call_func)
        return dag_flow

    @staticmethod
    def default_dag_flow_run_decorator(dag_flow: IsDagFlow) -> Any:
        def _inner_run_dag_flow(*args: object, **kwargs: object):
            results = {}
            result = None
            for i, job in enumerate(dag_flow.task_templates):
                if i == 0:
                    results = dag_flow.get_call_args(*args, **kwargs)

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
                with dag_flow.flow_context:
                    result = job(**params)

                if isinstance(result, dict) and len(result) > 0:
                    results.update(result)
                else:
                    results[job.name] = result
            return result

        return _inner_run_dag_flow

    @abstractmethod
    def _init_dag_flow(self, dag_flow: IsDagFlow) -> Any:
        ...

    @abstractmethod
    def _run_dag_flow(self, state: Any, dag_flow: IsDagFlow, *args, **kwargs) -> Any:
        ...


class FuncFlowRunnerEngine(JobRunnerEngine):
    def func_flow_decorator(self, func_flow: IsFuncFlow) -> IsFuncFlow:
        prev_call_func = func_flow._call_func  # noqa

        self._register_job_state(func_flow, RunState.INITIALIZED)
        state = self._init_func_flow(func_flow, prev_call_func)

        def _call_func(*args: object, **kwargs: object) -> Any:
            self._register_job_state(func_flow, RunState.RUNNING)
            with func_flow.flow_context:
                flow_result = self._run_func_flow(state, func_flow, prev_call_func, *args, **kwargs)
                return self._decorate_result_with_job_finalization_detector(func_flow, flow_result)

        setattr(func_flow, '_call_func', _call_func)
        return func_flow

    @abstractmethod
    def _init_func_flow(self, func_flow: IsFuncFlow, call_func: Callable) -> object:
        ...

    @abstractmethod
    def _run_func_flow(self,
                       state: Any,
                       func_flow: IsFuncFlow,
                       call_func: Callable,
                       *args,
                       **kwargs) -> Any:
        ...
