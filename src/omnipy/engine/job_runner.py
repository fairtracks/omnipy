from abc import ABC, abstractmethod
from typing import Any, Callable

from omnipy.engine._base import Engine
from omnipy.engine.run_spec import (DagFlowRunSpec,
                                    FlowRunSpec,
                                    FuncFlowRunSpec,
                                    JobRunSpec,
                                    LinearFlowRunSpec,
                                    TaskRunSpec)
from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.job import (IsDagFlow,
                                                 IsFuncArgJob,
                                                 IsFuncFlow,
                                                 IsLinearFlow,
                                                 IsTask)
from omnipy.util.callable_types import decorate_result_by_type


class JobRunnerEngine(Engine, ABC):
    """Base class for job runner engine implementations"""
    def _register_job_state(self, job: IsFuncArgJob, state: RunState.Literals) -> None:
        if self._registry:
            self._registry.set_job_state(job, state)

    def _apply_job_decorator(
        self,
        job: IsFuncArgJob,
        job_callback_accept_decorator: Callable,
        job_run_spec_cls: type[JobRunSpec],
        init_state: Callable,
        run_job: Callable,
    ) -> None:
        def _job_decorator(call_func: Callable) -> Callable:
            job_run_spec = job_run_spec_cls(job, call_func)
            self._register_job_state(job, RunState.INITIALIZED)
            state = init_state(job_run_spec)

            def _job_runner_call_func(*args: object, **kwargs: object) -> Any:
                self._register_job_state(job, RunState.RUNNING)
                job_result = run_job(state, job_run_spec, *args, **kwargs)
                return self._decorate_result_with_job_finalization_detector(job, job_result)

            return _job_runner_call_func

        job_callback_accept_decorator(_job_decorator)

    def _decorate_result_with_job_finalization_detector(self, job: IsFuncArgJob,
                                                        job_result: object):
        def _register_job_finished() -> None:
            self._register_job_state(job, RunState.FINISHED)

        return decorate_result_by_type(on_finished=_register_job_finished)(lambda: job_result)()


class TaskRunnerEngine(JobRunnerEngine):
    """Base class for task runner engine implementations"""
    def apply_task_decorator(self, task: IsTask, job_callback_accept_decorator: Callable) -> None:
        self._apply_job_decorator(
            task,
            job_callback_accept_decorator,
            TaskRunSpec,
            self._init_task,
            self._run_task,
        )

    @abstractmethod
    def _init_task(self, task: TaskRunSpec) -> object:
        ...

    @abstractmethod
    def _run_task(self, state: Any, task: TaskRunSpec, *args, **kwargs) -> object:
        ...


class LinearFlowRunnerEngine(JobRunnerEngine):
    """Base class for linear flow runner engine implementations"""
    def apply_linear_flow_decorator(
        self,
        linear_flow: IsLinearFlow,
        job_callback_accept_decorator: Callable,
    ) -> None:
        self._apply_job_decorator(
            linear_flow,
            job_callback_accept_decorator,
            LinearFlowRunSpec,
            self._init_flow,
            self._run_flow,
        )

    @abstractmethod
    def _init_flow(self, flow: FlowRunSpec) -> object:
        ...

    @abstractmethod
    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> object:
        ...


class DagFlowRunnerEngine(JobRunnerEngine):
    """Base class for DAG flow runner engine implementations"""
    def apply_dag_flow_decorator(
        self,
        dag_flow: IsDagFlow,
        job_callback_accept_decorator: Callable,
    ) -> None:
        self._apply_job_decorator(
            dag_flow,
            job_callback_accept_decorator,
            DagFlowRunSpec,
            self._init_flow,
            self._run_flow,
        )

    @abstractmethod
    def _init_flow(self, flow: FlowRunSpec) -> object:
        ...

    @abstractmethod
    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> object:
        ...


class FuncFlowRunnerEngine(JobRunnerEngine):
    """Base class for function flow runner engine implementations"""
    def apply_func_flow_decorator(
        self,
        func_flow: IsFuncFlow,
        job_callback_accept_decorator: Callable,
    ) -> None:
        self._apply_job_decorator(
            func_flow,
            job_callback_accept_decorator,
            FuncFlowRunSpec,
            self._init_flow,
            self._run_flow,
        )

    @abstractmethod
    def _init_flow(self, flow: FlowRunSpec) -> object:
        ...

    @abstractmethod
    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> object:
        ...
