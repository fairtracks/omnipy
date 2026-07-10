from abc import ABC
from typing import Any, Callable, ClassVar, Literal, NamedTuple

from omnipy.engine._base import Engine
from omnipy.engine.run_spec import (DagFlowRunSpec,
                                    FlowRunSpec,
                                    FuncFlowRunSpec,
                                    JobRunSpec,
                                    LinearFlowRunSpec,
                                    TaskRunSpec)
from omnipy.shared.enums.job import JobType, RunState
from omnipy.shared.protocols.compute.job import IsFuncArgJob
from omnipy.util.callable_types import decorate_result_by_type

InitRunHookName = Literal['_init_task', '_init_flow']
ExecRunHookName = Literal['_run_task', '_run_flow']
JobRunHookNames = tuple[InitRunHookName, ExecRunHookName]


class JobRunDef(NamedTuple):
    run_spec: type[JobRunSpec]
    init_hook_name: InitRunHookName
    run_hook_name: ExecRunHookName


TASK_RUN_HOOKS: JobRunHookNames = ('_init_task', '_run_task')
FLOW_RUN_HOOKS: JobRunHookNames = ('_init_flow', '_run_flow')

JOB_TYPE_TO_RUN_DEF: dict[JobType.Literals, JobRunDef] = {
    JobType.TASK: JobRunDef(TaskRunSpec, TASK_RUN_HOOKS[0], TASK_RUN_HOOKS[1]),
    JobType.LINEAR_FLOW: JobRunDef(LinearFlowRunSpec, FLOW_RUN_HOOKS[0], FLOW_RUN_HOOKS[1]),
    JobType.DAG_FLOW: JobRunDef(DagFlowRunSpec, FLOW_RUN_HOOKS[0], FLOW_RUN_HOOKS[1]),
    JobType.FUNC_FLOW: JobRunDef(FuncFlowRunSpec, FLOW_RUN_HOOKS[0], FLOW_RUN_HOOKS[1]),
}


class JobRunnerEngine(Engine, ABC):
    """Base class for job runner engine implementations"""
    supported_job_types: ClassVar[frozenset[JobType.Literals]] = frozenset()

    @classmethod
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        assert cls.supported_job_types, ('`supported_job_types` must be set '
                                         'on JobRunnerEngine subclasses')

        def _require_hook_override(hook_name: str, support_desc: str) -> None:
            if getattr(cls, hook_name) is getattr(JobRunnerEngine, hook_name):
                raise TypeError(f'JobRunnerEngine subclass {cls.__name__} supports '
                                f'{support_desc} but does not override {hook_name}')

        unknown_job_types = set(cls.supported_job_types) - set(JOB_TYPE_TO_RUN_DEF)
        if unknown_job_types:
            raise TypeError(f'JobRunnerEngine subclass {cls.__name__} has unknown supported job '
                            f'types: {sorted(unknown_job_types)}')

        required_run_hooks = {
            hook_name for job_type in cls.supported_job_types for hook_name in (
                JOB_TYPE_TO_RUN_DEF[job_type].init_hook_name,
                JOB_TYPE_TO_RUN_DEF[job_type].run_hook_name,)
        }
        for hook_name in required_run_hooks:
            _require_hook_override(hook_name, 'supported jobs')

    def supports(self, job_type: JobType.Literals) -> bool:
        return job_type in self.supported_job_types

    def _require_support(self, job_type: JobType.Literals) -> None:
        if not self.supports(job_type):
            raise RuntimeError(f'JobRunnerEngine "{self.__class__.__name__}" does not '
                               f'support job type: {job_type}')

    def apply_job_decorator(
        self,
        job_type: JobType.Literals,
        job: IsFuncArgJob,
        job_callback_accept_decorator: Callable,
    ) -> None:
        self._require_support(job_type)
        job_run_spec_cls, init_state, run_job = self._job_type_to_run_spec_and_funcs(job_type)

        self._apply_job_decorator(
            job,
            job_callback_accept_decorator,
            job_run_spec_cls,
            init_state,
            run_job,
        )

    def _job_type_to_run_spec_and_funcs(
            self, job_type: JobType.Literals) -> tuple[type[JobRunSpec], Callable, Callable]:
        if job_type not in JOB_TYPE_TO_RUN_DEF:
            raise ValueError(f'Unknown job type: {job_type}')

        job_run_def = JOB_TYPE_TO_RUN_DEF[job_type]
        job_run_spec, init_hook_name, run_hook_name = job_run_def
        return job_run_spec, getattr(self, init_hook_name), getattr(self, run_hook_name)

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

    def _init_task(self, task: TaskRunSpec) -> object:
        raise NotImplementedError

    def _run_task(self, state: Any, task: TaskRunSpec, *args, **kwargs) -> object:
        raise NotImplementedError

    def _init_flow(self, flow: FlowRunSpec) -> object:
        raise NotImplementedError

    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> object:
        raise NotImplementedError
