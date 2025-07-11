import asyncio
from contextlib import AbstractContextManager
from datetime import datetime
from functools import update_wrapper
import inspect
from inspect import BoundArguments
from typing import Any, Callable, Type

from inflection import underscore
from slugify import slugify

from omnipy.config import ConfigBase
from omnipy.engine.job_runner import (DagFlowRunnerEngine,
                                      FuncFlowRunnerEngine,
                                      LinearFlowRunnerEngine,
                                      TaskRunnerEngine)
from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute._job import IsJob
from omnipy.shared.protocols.compute.job import IsDagFlow, IsFlow, IsFuncFlow, IsLinearFlow, IsTask
from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.typedefs import GeneralDecorator
from omnipy.util.callable_decorator import callable_decorator_cls


class MockJobCreator(AbstractContextManager):
    def __init__(self):
        self.engine: IsEngine | None = None
        self.nested_context_level = 0

    def set_engine(self, engine: IsEngine) -> None:
        self.engine = engine

    def __enter__(self):
        self.nested_context_level += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self.nested_context_level -= 1


class MockTask:
    job_creator = MockJobCreator()

    def __init__(self, func: Callable, *, name: str | None = None) -> None:
        self._func = func
        self._func_signature = inspect.signature(self._func)
        self.name = name if name is not None else func.__name__
        self.regenerate_unique_name()

    def regenerate_unique_name(self) -> None:
        from omnipy.components.prefect.lazy_import import generate_slug

        class_name_snake = underscore(self.__class__.__name__)
        self.unique_name = slugify(  # noqa
            f'{class_name_snake}-{underscore(self.name)}-{generate_slug(2)}')

    def __call__(self, *args: object, **kwargs: object) -> Any:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: object, **kwargs: object) -> Any:
        return self._func(*args, **kwargs)

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._func)

    @property
    def flow_context(self):
        return self.job_creator

    @property
    def in_flow_context(self):
        return self.job_creator.nested_context_level > 0

    def _accept_call_func_decorator(self, call_func_decorator: GeneralDecorator) -> None:
        self._func = call_func_decorator(self._func)

    def get_bound_args(self, *args: object, **kwargs: object) -> BoundArguments:
        return self._func_signature.bind(*args, **kwargs)


@callable_decorator_cls
class MockTaskTemplate(MockTask):
    def _call_func(self, *args: object, **kwargs: object) -> Any:
        if self.in_flow_context:
            return self.run(*args, **kwargs)
        raise TypeError("'{}' object is not callable".format(self.__class__.__name__))

    def run(self, *args: object, **kwargs: object) -> object:
        return self.apply()(*args, **kwargs)

    def apply(self) -> IsTask:
        task = MockTask(self._func, name=self.name)
        self.job_creator.engine.apply_task_decorator(task, task._accept_call_func_decorator)
        update_wrapper(task, self._func)
        return task


class MockLinearFlow(MockTask):
    def __init__(self,
                 func: Callable,
                 *task_templates: MockTaskTemplate,
                 name: str | None = None,
                 **kwargs: object) -> None:
        self._task_templates = task_templates
        super().__init__(func, name=name, **kwargs)

    @property
    def task_templates(self) -> tuple[MockTaskTemplate, ...]:
        return self._task_templates


@callable_decorator_cls
class MockLinearFlowTemplate(MockLinearFlow):
    def apply(self) -> MockLinearFlow:
        linear_flow = MockLinearFlow(self._func, *self._task_templates, name=self.name)
        self.job_creator.engine.apply_linear_flow_decorator(linear_flow,
                                                            linear_flow._accept_call_func_decorator)
        update_wrapper(linear_flow, self._func)
        return linear_flow


class MockDagFlow(MockTask):
    def __init__(self,
                 func: Callable,
                 *task_templates: MockTaskTemplate,
                 name: str | None = None,
                 **kwargs: object) -> None:
        self._task_templates = task_templates
        super().__init__(func, name=name, **kwargs)

    @property
    def task_templates(self) -> tuple[MockTaskTemplate, ...]:
        return self._task_templates


@callable_decorator_cls
class MockDagFlowTemplate(MockDagFlow):
    def apply(self) -> MockDagFlow:
        dag_flow = MockDagFlow(self._func, *self._task_templates, name=self.name)
        self.job_creator.engine.apply_dag_flow_decorator(dag_flow,
                                                         dag_flow._accept_call_func_decorator)
        update_wrapper(dag_flow, self._func)
        return dag_flow


class MockFuncFlow(MockTask):
    def __init__(self, flow_func: Callable, name: str | None = None, **kwargs: object) -> None:
        super().__init__(flow_func, name=name)


@callable_decorator_cls
class MockFuncFlowTemplate(MockFuncFlow, MockTaskTemplate):
    def apply(self) -> MockFuncFlow:
        func_flow = MockFuncFlow(self._func, name=self.name)
        self.job_creator.engine.apply_func_flow_decorator(func_flow,
                                                          func_flow._accept_call_func_decorator)
        update_wrapper(func_flow, self._func)
        return func_flow


class MockEngineConfig(ConfigBase):
    backend_verbose: bool = True


class MockBackendTask:
    def __init__(self, engine_config: MockEngineConfig):
        self.backend_verbose = engine_config.backend_verbose

    def run(self, task: IsTask, call_func: Callable, *args: object, **kwargs: object):
        if self.backend_verbose:
            print('Running task "{}": ...'.format(task.name))
        result = call_func(*args, **kwargs)
        if self.backend_verbose:
            print('Result of task "{}": {}'.format(task.name, result))
        return result


class MockBackendFlow:
    def __init__(self, engine_config: MockEngineConfig, call_func: Callable | None = None):
        self.backend_verbose = engine_config.backend_verbose
        self.call_func = call_func

    def run(self, flow: IsFlow, call_func: Callable, *args: object, **kwargs: object):
        if self.backend_verbose:
            print('Running flow "{}": ...'.format(flow.name))
        result = call_func(*args, **kwargs)
        if self.backend_verbose:
            print('Result of flow "{}": {}'.format(flow.name, result))
        return result


class MockJobRunnerSubclass(TaskRunnerEngine,
                            LinearFlowRunnerEngine,
                            DagFlowRunnerEngine,
                            FuncFlowRunnerEngine):
    def _init_engine(self) -> None:
        self._update_from_config()
        self.finished_backend_tasks: list[MockBackendTask] = []
        self.finished_backend_flows: list[MockBackendFlow] = []

    def _update_from_config(self) -> None:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.backend_verbose: bool = self._config.backend_verbose

    @classmethod
    def get_config_cls(cls) -> Type[IsJobRunnerConfig]:
        return MockEngineConfig

    # TaskRunnerEngine

    def _init_task(self, task: IsTask, call_func: Callable) -> MockBackendTask:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        return MockBackendTask(self._config)

    def _run_task(self, state: MockBackendTask, task: IsTask, call_func: Callable, *args,
                  **kwargs) -> Any:
        result = state.run(task, call_func, *args, **kwargs)
        self.finished_backend_tasks.append(state)
        return result

    # LinearFlowRunnerEngine

    def _init_linear_flow(self, linear_flow: IsLinearFlow) -> MockBackendFlow:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        return MockBackendFlow(self._config)

    def _run_linear_flow(self, state: MockBackendFlow, linear_flow: IsLinearFlow, *args,
                         **kwargs) -> Any:
        call_func = self.default_linear_flow_run_decorator(linear_flow)
        result = state.run(linear_flow, call_func, *args, **kwargs)
        self.finished_backend_flows.append(state)
        return result

    # DagFlowRunnerEngine

    def _init_dag_flow(self, dag_flow: IsDagFlow) -> MockBackendFlow:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        return MockBackendFlow(self._config)

    def _run_dag_flow(self, state: MockBackendFlow, dag_flow: IsDagFlow, *args, **kwargs) -> Any:
        call_func = self.default_dag_flow_run_decorator(dag_flow)
        result = state.run(dag_flow, call_func, *args, **kwargs)
        self.finished_backend_flows.append(state)
        return result

    # FuncFlowRunnerEngine

    def _init_func_flow(self, func_flow: IsFuncFlow, call_func: Callable) -> object:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        return MockBackendFlow(self._config, call_func)

    def _run_func_flow(self, state: MockBackendFlow, func_flow: IsFuncFlow, *args, **kwargs) -> Any:
        assert state.call_func is not None
        result = state.run(func_flow, state.call_func, *args, **kwargs)
        self.finished_backend_flows.append(state)
        return result


class MockRunStateRegistryConfig(ConfigBase):
    verbose: bool = True


class MockRunStateRegistry:
    def __init__(self) -> None:
        self._jobs: dict[str, IsJob] = {}
        self._job_state: dict[str, RunState.Literals] = {}
        self._job_state_datetime: dict[tuple[str, RunState.Literals], datetime] = {}

    def get_job_state(self, job: IsJob) -> RunState.Literals:
        return self._job_state[job.unique_name]

    def get_job_state_datetime(self, job: IsJob, state: RunState.Literals) -> datetime:
        return self._job_state_datetime[(job.unique_name, state)]

    def all_jobs(self, state: RunState.Literals | None = None) -> tuple[IsJob, ...]:  # noqa
        return tuple(self._jobs.values())

    def set_job_state(self, job: IsJob, state: RunState.Literals) -> None:
        self._jobs[job.unique_name] = job
        self._job_state[job.unique_name] = state
        self._job_state_datetime[(job.unique_name, state)] = datetime.now()
