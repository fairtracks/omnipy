from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Generic, Type, TypeVar

from omnipy.shared.enums import RunState
from omnipy.shared.protocols.compute._job import IsJob
from omnipy.shared.protocols.compute.job import IsDagFlow, IsFuncFlow, IsLinearFlow, IsTask
from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.engine.job_runner import (IsDagFlowRunnerEngine,
                                                       IsFuncFlowRunnerEngine,
                                                       IsTaskRunnerEngine)
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry


class JobType(Enum):
    task = 1
    linear_flow = 2
    dag_flow = 3
    func_flow = 4


ArgT = TypeVar('ArgT')
ReturnT = TypeVar('ReturnT')


@dataclass
class JobCase(Generic[ArgT, ReturnT]):
    name: str
    job_func: Callable[[ArgT], ReturnT]
    run_and_assert_results_func: Callable[..., None] | Awaitable[Callable[..., None]]
    job_type: JobType | None = None
    job: IsJob | None = None


class JobRunnerStateChecker(IsTaskRunnerEngine, IsDagFlowRunnerEngine, IsFuncFlowRunnerEngine):
    def __init__(self, engine):
        self._engine = engine
        self._engine.__init__()

    def set_config(self, config: IsJobRunnerConfig) -> None:
        self._engine.set_config(config)

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        self._engine.set_registry(registry)

    def get_config_cls(self) -> Type[IsJobRunnerConfig]:
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

    def _init_task(self, task: IsTask, call_func: Callable) -> Any:
        from .functions import assert_job_state
        assert_job_state(task, [RunState.INITIALIZED])
        return self._engine._init_task(task, call_func)  # noqa

    def _run_task(self, state: Any, task: IsTask, call_func: Callable, *args, **kwargs) -> Any:
        from .functions import assert_job_state
        assert_job_state(task, [RunState.RUNNING])
        return self._engine._run_task(state, task, call_func, *args, **kwargs)  # noqa

    def _init_linear_flow(self, linear_flow: IsLinearFlow) -> Any:
        from .functions import assert_job_state
        assert_job_state(linear_flow, [RunState.INITIALIZED])
        return self._engine._init_linear_flow(linear_flow)  # noqa

    def _run_linear_flow(self, state: Any, linear_flow: IsLinearFlow, *args, **kwargs) -> Any:
        from .functions import assert_job_state
        assert_job_state(linear_flow, [RunState.RUNNING])
        return self._engine._run_linear_flow(state, linear_flow, *args, **kwargs)  # noqa

    def _init_dag_flow(self, dag_flow: IsDagFlow) -> Any:
        from .functions import assert_job_state
        assert_job_state(dag_flow, [RunState.INITIALIZED])
        return self._engine._init_dag_flow(dag_flow)  # noqa

    def _run_dag_flow(self, state: Any, dag_flow: IsDagFlow, *args, **kwargs) -> Any:
        from .functions import assert_job_state
        assert_job_state(dag_flow, [RunState.RUNNING])
        return self._engine._run_dag_flow(state, dag_flow, *args, **kwargs)  # noqa

    def _init_func_flow(self, func_flow: IsFuncFlow) -> Any:
        from .functions import assert_job_state
        assert_job_state(func_flow, [RunState.INITIALIZED])
        return self._engine._init_func_flow(dag_flow)  # noqa

    def _run_func_flow(self, state: Any, func_flow: IsFuncFlow, *args, **kwargs) -> Any:
        from .functions import assert_job_state
        assert_job_state(func_flow, [RunState.RUNNING])
        return self._engine._run_func_flow(state, func_flow, *args, **kwargs)  # noqa
