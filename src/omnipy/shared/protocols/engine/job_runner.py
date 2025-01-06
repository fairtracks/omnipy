from typing import Callable, Protocol, runtime_checkable

from omnipy.shared.protocols.compute.job import IsDagFlow, IsFuncFlow, IsLinearFlow, IsTask
from omnipy.shared.protocols.engine.base import IsEngine


@runtime_checkable
class IsTaskRunnerEngine(IsEngine, Protocol):
    """"""
    def apply_task_decorator(self, task: IsTask, job_callback_accept_decorator: Callable) -> None:
        ...


@runtime_checkable
class IsLinearFlowRunnerEngine(IsEngine, Protocol):
    """"""
    def apply_linear_flow_decorator(self,
                                    linear_flow: IsLinearFlow,
                                    job_callback_accept_decorator: Callable) -> None:
        ...


@runtime_checkable
class IsDagFlowRunnerEngine(IsEngine, Protocol):
    """"""
    def apply_dag_flow_decorator(self, dag_flow: IsDagFlow,
                                 job_callback_accept_decorator: Callable) -> None:
        ...


@runtime_checkable
class IsFuncFlowRunnerEngine(IsEngine, Protocol):
    """"""
    def apply_func_flow_decorator(self,
                                  func_flow: IsFuncFlow,
                                  job_callback_accept_decorator: Callable) -> None:
        ...
