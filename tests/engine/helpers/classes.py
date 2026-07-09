from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Generic, ParamSpec, Type, TypeVar

from typing_extensions import override

from omnipy.engine.run_spec import FlowRunSpec, TaskRunSpec
from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.job import IsDagFlow, IsFuncFlow, IsJob, IsLinearFlow, IsTask
from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.engine.job_runner import (IsDagFlowRunnerEngine,
                                                       IsFuncFlowRunnerEngine,
                                                       IsLinearFlowRunnerEngine,
                                                       IsTaskRunnerEngine)
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry


class JobType(Enum):
    task = 1
    linear_flow = 2
    dag_flow = 3
    func_flow = 4


CallP = ParamSpec('CallP')
ReturnT = TypeVar('ReturnT')


@dataclass
class JobCase(Generic[CallP, ReturnT]):
    name: str
    job_func: Callable[CallP, ReturnT]
    run_and_assert_results_func: Callable[..., None | Awaitable[None]]
    job_type: JobType | None = None
    job: IsJob | None = None


class JobRunnerStateChecker(IsTaskRunnerEngine,
                            IsLinearFlowRunnerEngine,
                            IsDagFlowRunnerEngine,
                            IsFuncFlowRunnerEngine):
    def __init__(self, engine):
        object.__init__(self)
        self._engine = engine
        self._engine.__init__()

    def set_config(self, config: IsJobRunnerConfig) -> None:
        self._engine.set_config(config)

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        self._engine.set_registry(registry)

    @property
    def config(self) -> IsJobRunnerConfig:
        return self._engine.config

    @property
    def registry(self) -> IsRunStateRegistry | None:
        return self._engine.registry

    @override
    def get_config_cls(self) -> Type[IsJobRunnerConfig]:  # type: ignore[override]
        return self._engine.get_config_cls()  # noqa

    def apply_task_decorator(self, task: IsTask, job_callback_accept_decorator: Callable) -> None:
        return self._engine.apply_task_decorator(task, job_callback_accept_decorator)

    def apply_linear_flow_decorator(self,
                                    linear_flow: IsLinearFlow,
                                    job_callback_accept_decorator: Callable) -> None:
        return self._engine.apply_linear_flow_decorator(linear_flow, job_callback_accept_decorator)

    def apply_dag_flow_decorator(self, dag_flow: IsDagFlow,
                                 job_callback_accept_decorator: Callable) -> None:
        return self._engine.apply_dag_flow_decorator(dag_flow, job_callback_accept_decorator)

    def apply_func_flow_decorator(self,
                                  func_flow: IsFuncFlow,
                                  job_callback_accept_decorator: Callable) -> None:
        return self._engine.apply_func_flow_decorator(func_flow, job_callback_accept_decorator)

    def _init_task(self, task: TaskRunSpec) -> object:
        from .functions import assert_job_state
        assert_job_state(task._job, [RunState.INITIALIZED])
        return self._engine._init_task(task)  # noqa

    def _run_task(self, state: Any, task: TaskRunSpec, *args, **kwargs) -> object:
        from .functions import assert_job_state
        assert_job_state(task._job, [RunState.RUNNING])
        return self._engine._run_task(state, task, *args, **kwargs)  # noqa

    def _init_flow(self, flow: FlowRunSpec) -> object:
        from .functions import assert_job_state
        assert_job_state(flow._job, [RunState.INITIALIZED])
        return self._engine._init_flow(flow)  # noqa

    def _run_flow(self, state: Any, flow: FlowRunSpec, *args, **kwargs) -> object:
        from .functions import assert_job_state
        assert_job_state(flow._job, [RunState.RUNNING])
        return self._engine._run_flow(state, flow, *args, **kwargs)  # noqa
