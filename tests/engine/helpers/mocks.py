from contextlib import AbstractContextManager
from datetime import datetime
from functools import update_wrapper
import inspect
from inspect import BoundArguments
from types import MappingProxyType
from typing import Any, Callable, cast, Type

from omnipy.config import ConfigBase
from omnipy.engine.job_runner import (DagFlowRunnerEngine,
                                      FuncFlowRunnerEngine,
                                      LinearFlowRunnerEngine,
                                      TaskRunnerEngine)
from omnipy.engine.run_spec import FlowRunSpec, TaskRunSpec
from omnipy.hub.log.mixin import LogMixin
from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute._job import IsJob
from omnipy.shared.protocols.compute.job import IsTaskTemplate
from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.engine.job_runner import (IsDagFlowRunnerEngine,
                                                       IsEngine,
                                                       IsFuncFlowRunnerEngine,
                                                       IsLinearFlowRunnerEngine,
                                                       IsTaskRunnerEngine)
from omnipy.shared.typedefs import GeneralDecorator
from omnipy.util.callable_decorator import callable_decorator_cls
from omnipy.util.helpers import generate_job_slug, is_async_func, is_generator_func


class MockJobCreator(AbstractContextManager):
    def __init__(self) -> None:
        self.engine: IsEngine | None = None
        self.nested_context_level = 0

    def set_engine(self, engine: IsEngine) -> None:
        self.engine = engine

    def __enter__(self):
        self.nested_context_level += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self.nested_context_level -= 1


class MockTask(LogMixin):
    job_creator = MockJobCreator()

    def __init__(self, func: Callable, *, name: str | None = None) -> None:
        super().__init__()
        self._func = func
        self._job_func = func
        self._func_signature = inspect.signature(self._func)
        self.name = name if name is not None else func.__name__
        self.regenerate_unique_name()

    def regenerate_unique_name(self) -> None:
        self.unique_name = generate_job_slug(self.__class__.__name__, self.name)

    def __call__(self, *args: object, **kwargs: object) -> Any:
        return self._call_func(*args, **kwargs)

    def _call_func(self, *args: object, **kwargs: object) -> Any:
        return self._func(*args, **kwargs)

    @property
    def param_signatures(self) -> MappingProxyType[str, inspect.Parameter]:
        return self._func_signature.parameters

    @property
    def return_type(self) -> type:
        return self._func_signature.return_annotation

    def has_async_func(self) -> bool:
        return is_async_func(self._job_func)

    def has_generator_func(self) -> bool:
        return is_generator_func(self._job_func)

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

    def apply(self) -> MockTask:
        task = MockTask(self._func, name=self.name)
        engine = cast(IsTaskRunnerEngine, self.job_creator.engine)
        assert engine is not None
        engine.apply_task_decorator(
            task,  # type: ignore[arg-type]
            task._accept_call_func_decorator,
        )
        update_wrapper(task, self._func)
        return task


class MockLinearFlow(MockTask):
    def __init__(self,
                 func: Callable,
                 *task_templates: IsTaskTemplate,
                 name: str | None = None,
                 **kwargs: object) -> None:
        self._task_templates = task_templates
        super().__init__(func, name=name, **kwargs)

    @property
    def task_templates(self) -> tuple[IsTaskTemplate, ...]:
        return self._task_templates


@callable_decorator_cls
class MockLinearFlowTemplate(MockLinearFlow):
    def apply(self) -> MockLinearFlow:
        linear_flow = MockLinearFlow(self._func, *self._task_templates, name=self.name)
        engine = cast(IsLinearFlowRunnerEngine, self.job_creator.engine)
        assert engine is not None
        engine.apply_linear_flow_decorator(
            linear_flow,  # type: ignore[arg-type]
            linear_flow._accept_call_func_decorator,
        )
        update_wrapper(linear_flow, self._func)
        return linear_flow


class MockDagFlow(MockTask):
    def __init__(self,
                 func: Callable,
                 *task_templates: IsTaskTemplate,
                 name: str | None = None,
                 **kwargs: object) -> None:
        self._task_templates = task_templates
        super().__init__(func, name=name, **kwargs)

    @property
    def task_templates(self) -> tuple[IsTaskTemplate, ...]:
        return self._task_templates


@callable_decorator_cls
class MockDagFlowTemplate(MockDagFlow):
    def apply(self) -> MockDagFlow:
        dag_flow = MockDagFlow(self._func, *self._task_templates, name=self.name)
        engine = cast(IsDagFlowRunnerEngine, self.job_creator.engine)
        engine.apply_dag_flow_decorator(
            dag_flow,  # type: ignore[arg-type]
            dag_flow._accept_call_func_decorator,
        )
        update_wrapper(dag_flow, self._func)
        return dag_flow


class MockFuncFlow(MockTask):
    def __init__(self, flow_func: Callable, name: str | None = None, **kwargs: object) -> None:
        super().__init__(flow_func, name=name)


@callable_decorator_cls
class MockFuncFlowTemplate(MockFuncFlow, MockTaskTemplate):  # pyright: ignore
    def apply(self) -> MockFuncFlow:
        func_flow = MockFuncFlow(self._func, name=self.name)
        engine = cast(IsFuncFlowRunnerEngine, self.job_creator.engine)
        engine.apply_func_flow_decorator(
            func_flow,  # type: ignore[arg-type]
            func_flow._accept_call_func_decorator,
        )
        update_wrapper(func_flow, self._func)
        return func_flow


class MockEngineConfig(ConfigBase):
    backend_verbose: bool = True


class MockBackendTask:
    def __init__(self, engine_config: MockEngineConfig):
        self.backend_verbose = engine_config.backend_verbose

    def run(self, task: TaskRunSpec, call_func: Callable, *args: object, **kwargs: object):
        if self.backend_verbose:
            print('Running task "{}": ...'.format(task.name))
        result = call_func(*args, **kwargs)
        if self.backend_verbose:
            print('Result of task "{}": {}'.format(task.name, result))
        return result


class MockBackendFlow:
    def __init__(self, engine_config: MockEngineConfig):
        self.backend_verbose = engine_config.backend_verbose

    def run(self, flow: FlowRunSpec, call_func: Callable, *args: object, **kwargs: object):
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

    def _init_task(self, task: TaskRunSpec) -> MockBackendTask:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        return MockBackendTask(self._config)

    def _run_task(self, state: MockBackendTask, task: TaskRunSpec, *args, **kwargs) -> object:
        result = state.run(task, task.create_default_run_callable(), *args, **kwargs)
        self.finished_backend_tasks.append(state)
        return result

    def _init_flow(self, flow: FlowRunSpec) -> MockBackendFlow:
        assert isinstance(self._config, MockEngineConfig)  # to help type checkers
        return MockBackendFlow(self._config)

    def _run_flow(self, state: MockBackendFlow, flow: FlowRunSpec, *args, **kwargs) -> object:
        result = state.run(flow, flow.create_default_run_callable(), *args, **kwargs)
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
