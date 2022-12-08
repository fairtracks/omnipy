from dataclasses import dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Generic, Optional, Type, TypeVar, Union

from unifair.engine.constants import RunState
from unifair.engine.protocols import (IsDagFlow,
                                      IsDagFlowRunnerEngine,
                                      IsEngineConfig,
                                      IsJob,
                                      IsRunStateRegistry,
                                      IsTask,
                                      IsTaskRunnerEngine)


class JobType(Enum):
    task = 1
    dag_flow = 2
    func_flow = 3


ArgT = TypeVar('ArgT')
ReturnT = TypeVar('ReturnT')


@dataclass
class JobCase(Generic[ArgT, ReturnT]):
    name: str
    job_func: Callable[[ArgT], ReturnT]
    run_and_assert_results_func: Union[Callable[[Any], None], Awaitable[Callable[[Any], None]]]
    job_type: Optional[JobType] = None
    job: Optional[IsJob] = None


class JobRunnerStateChecker(IsTaskRunnerEngine, IsDagFlowRunnerEngine):
    def __init__(self, engine):
        self._engine = engine
        self._engine.__init__()

    def set_config(self, config: IsEngineConfig) -> None:
        self._engine.set_config(config)

    def set_registry(self, registry: Optional[IsRunStateRegistry]) -> None:
        self._engine.set_registry(registry)

    def get_config_cls(self) -> Type[IsEngineConfig]:
        return self._engine.get_config_cls()  # noqa

    def task_decorator(self, task: IsTask) -> IsTask:
        return self._engine.task_decorator(task)

    def dag_flow_decorator(self, dag_flow: IsDagFlow) -> IsDagFlow:
        return self._engine.dag_flow_decorator(dag_flow)

    def _init_task(self, task: IsTask, call_func: Callable) -> Any:
        from .functions import assert_job_state
        assert_job_state(task, [RunState.INITIALIZED])
        return self._engine._init_task(task, call_func)  # noqa

    def _run_task(self, state: Any, task: IsTask, call_func: Callable, *args, **kwargs) -> Any:
        from .functions import assert_job_state
        assert_job_state(task, [RunState.RUNNING])
        return self._engine._run_task(state, task, call_func, *args, **kwargs)  # noqa

    def _init_dag_flow(self, dag_flow: IsDagFlow, call_func: Callable) -> Any:
        from .functions import assert_job_state
        assert_job_state(dag_flow, [RunState.INITIALIZED])
        return self._engine._init_dag_flow(dag_flow, call_func)  # noqa

    def _run_dag_flow(self, state: Any, dag_flow: IsDagFlow, call_func: Callable, *args,
                      **kwargs) -> Any:
        from .functions import assert_job_state
        assert_job_state(dag_flow, [RunState.RUNNING])
        return self._engine._run_dag_flow(state, dag_flow, call_func, *args, **kwargs)  # noqa
