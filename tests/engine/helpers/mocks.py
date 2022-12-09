import asyncio
from dataclasses import dataclass
from datetime import datetime
from functools import update_wrapper
import inspect
import logging
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple, Type

from inflection import underscore
from prefect.utilities.names import generate_slug
from slugify import slugify

from unifair.engine.base import Engine
from unifair.engine.constants import RunState
from unifair.engine.job_runner import (DagFlowRunnerEngine,
                                       FuncFlowRunnerEngine,
                                       LinearFlowRunnerEngine,
                                       TaskRunnerEngine)
from unifair.engine.protocols import (IsDagFlow,
                                      IsEngine,
                                      IsEngineConfig,
                                      IsFlow,
                                      IsFuncFlow,
                                      IsJob,
                                      IsLinearFlow,
                                      IsRunStateRegistry,
                                      IsRunStateRegistryConfig,
                                      IsTask)
from unifair.util.callable_decorator_cls import callable_decorator_cls


class MockJobCreator:
    def __init__(self):
        self.engine: Optional[IsEngine] = None
        self.nested_context_level = 0

    def set_engine(self, engine: IsEngine) -> None:
        self.engine = engine

    def __enter__(self):
        self.nested_context_level += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self.nested_context_level -= 1


class MockTask:
    job_creator = MockJobCreator()

    def __init__(self, func: Callable, *, name: Optional[str] = None) -> None:
        self._func = func
        self.name = name if name is not None else func.__name__
        self.regenerate_unique_name()

    def regenerate_unique_name(self) -> None:
        class_name_snake = underscore(self.__class__.__name__)
        self.unique_name = slugify(  # noqa
            f'{class_name_snake}-{underscore(self.name)}-{generate_slug(2)}')

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        return self._func(*args, **kwargs)

    def has_coroutine_func(self) -> bool:
        return asyncio.iscoroutinefunction(self._func)

    @property
    def flow_context(self):
        return self.job_creator

    @property
    def in_flow_context(self):
        return self.job_creator.nested_context_level > 0


@callable_decorator_cls
class MockTaskTemplate(MockTask):
    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        if self.in_flow_context:
            return self.run(*args, **kwargs)
        raise TypeError("'{}' object is not callable".format(self.__class__.__name__))

    def run(self, *args: object, **kwargs: object) -> object:
        return self.apply()(*args, **kwargs)

    def apply(self) -> IsTask:
        task = MockTask(self._func, name=self.name)
        update_wrapper(task, self._func)
        print(self.job_creator.engine)
        return self.job_creator.engine.task_decorator(task)


class MockLinearFlow(MockTask):
    def __init__(self,
                 func: Callable,
                 *task_templates: MockTaskTemplate,
                 name: Optional[str] = None,
                 **kwargs: object) -> None:
        self._task_templates = task_templates
        super().__init__(func, name=name, **kwargs)

    @property
    def task_templates(self) -> Tuple[MockTaskTemplate]:
        return self._task_templates

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._func).bind(*args, **kwargs).arguments


@callable_decorator_cls
class MockLinearFlowTemplate(MockLinearFlow):
    def apply(self) -> IsTask:
        linear_flow = MockLinearFlow(self._func, *self._task_templates, name=self.name)
        linear_flow = self.job_creator.engine.linear_flow_decorator(linear_flow)
        update_wrapper(linear_flow, self._func)
        return linear_flow


class MockDagFlow(MockTask):
    def __init__(self,
                 func: Callable,
                 *task_templates: MockTaskTemplate,
                 name: Optional[str] = None,
                 **kwargs: object) -> None:
        self._task_templates = task_templates
        super().__init__(func, name=name, **kwargs)

    @property
    def task_templates(self) -> Tuple[MockTaskTemplate]:
        return self._task_templates

    def get_call_args(self, *args: object, **kwargs: object) -> Dict[str, object]:
        return inspect.signature(self._func).bind(*args, **kwargs).arguments


@callable_decorator_cls
class MockDagFlowTemplate(MockDagFlow):
    def apply(self) -> IsTask:
        dag_flow = MockDagFlow(self._func, *self._task_templates, name=self.name)
        dag_flow = self.job_creator.engine.dag_flow_decorator(dag_flow)
        update_wrapper(dag_flow, self._func)
        return dag_flow


class MockFuncFlow(MockTask):
    def __init__(self, flow_func: Callable, name: Optional[str] = None, **kwargs: object) -> None:
        super().__init__(flow_func, name=name)


@callable_decorator_cls
class MockFuncFlowTemplate(MockFuncFlow, MockTaskTemplate):
    def apply(self) -> IsTask:
        func_flow = MockFuncFlow(self._func, name=self.name)
        func_flow = self.job_creator.engine.func_flow_decorator(func_flow)
        update_wrapper(func_flow, self._func)
        return func_flow


@dataclass
class MockEngineConfig:
    backend_verbose: bool = True


class MockBackendTask:
    def __init__(self, engine_config: MockEngineConfig):
        self.backend_verbose = engine_config.backend_verbose

    def run(self, task: IsTask, call_func: Callable, *args: Any, **kwargs: Any):
        if self.backend_verbose:
            print('Running task "{}": ...'.format(task.name))
        result = call_func(*args, **kwargs)
        if self.backend_verbose:
            print('Result of task "{}": {}'.format(task.name, result))
        return result


class MockBackendFlow:
    def __init__(self, engine_config: MockEngineConfig):
        self.backend_verbose = engine_config.backend_verbose

    def run(self, flow: IsFlow, call_func: Callable, *args: Any, **kwargs: Any):
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
        self.finished_backend_tasks: List[MockBackendTask] = []
        self.finished_backend_flows: List[MockBackendFlow] = []

    def _update_from_config(self) -> None:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        self.backend_verbose: bool = self._config.backend_verbose

    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
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
        return MockBackendFlow(self._config)

    def _run_func_flow(self,
                       state: MockBackendFlow,
                       func_flow: IsFuncFlow,
                       call_func: Callable,
                       *args,
                       **kwargs) -> Any:
        result = state.run(func_flow, call_func, *args, **kwargs)
        self.finished_backend_flows.append(state)
        return result


@dataclass
class MockRunStateRegistryConfig:
    verbose: bool = True


class MockRunStateRegistry:
    def __init__(self) -> None:
        self.logger: Optional[logging.Logger] = None
        self.config: IsRunStateRegistryConfig = MockRunStateRegistryConfig()

        self._jobs: Dict[str, IsJob] = {}
        self._job_state: Dict[str, RunState] = {}
        self._job_state_datetime: Dict[Tuple[str, RunState], datetime] = {}

    def get_job_state(self, job: IsJob) -> RunState:
        return self._job_state[job.unique_name]

    def get_job_state_datetime(self, job: IsJob, state: RunState) -> datetime:
        return self._job_state_datetime[(job.unique_name, state)]

    def all_jobs(self, state: Optional[RunState] = None) -> Tuple[IsJob, ...]:  # noqa
        return tuple(self._jobs.values())

    def set_job_state(self, job: IsJob, state: RunState) -> None:
        self._jobs[job.unique_name] = job
        self._job_state[job.unique_name] = state
        self._job_state_datetime[(job.unique_name, state)] = datetime.now()
        if self.logger:
            self.logger.info(f'{job.unique_name} - {state.name}')

    def set_logger(self, logger: Optional[logging.Logger]) -> None:
        self.logger = logger

    def set_config(self, config: IsRunStateRegistryConfig) -> None:
        self.config = config
