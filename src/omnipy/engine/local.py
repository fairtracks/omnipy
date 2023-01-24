from typing import Any, Callable, Type

from omnipy.api.protocols import IsDagFlow, IsFuncFlow, IsLinearFlow, IsLocalRunnerConfig, IsTask
from omnipy.config.engine import LocalRunnerConfig
from omnipy.engine.job_runner import (DagFlowRunnerEngine,
                                      FuncFlowRunnerEngine,
                                      LinearFlowRunnerEngine,
                                      TaskRunnerEngine)


class LocalRunner(TaskRunnerEngine,
                  LinearFlowRunnerEngine,
                  DagFlowRunnerEngine,
                  FuncFlowRunnerEngine):
    def _init_engine(self) -> None:
        ...

    def _update_from_config(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsLocalRunnerConfig]:
        return LocalRunnerConfig

    def _init_task(self, task: IsTask, call_func: Callable) -> Any:
        ...

    def _run_task(self, state: Any, task: IsTask, call_func: Callable, *args, **kwargs) -> Any:
        return call_func(*args, **kwargs)

    def _init_linear_flow(self, flow: IsLinearFlow) -> Any:
        ...

    def _run_linear_flow(self, state: Any, flow: IsLinearFlow, *args, **kwargs) -> Any:
        return self.default_linear_flow_run_decorator(flow)(*args, **kwargs)

    def _init_dag_flow(self, flow: IsDagFlow) -> Any:
        ...

    def _run_dag_flow(self, state: Any, flow: IsDagFlow, *args, **kwargs) -> Any:
        return self.default_dag_flow_run_decorator(flow)(*args, **kwargs)

    def _init_func_flow(self, func_flow: IsFuncFlow, call_func: Callable) -> object:
        pass

    def _run_func_flow(self,
                       state: Any,
                       func_flow: IsFuncFlow,
                       call_func: Callable,
                       *args,
                       **kwargs) -> Any:
        with func_flow.flow_context:
            return call_func(*args, **kwargs)
