from typing import Any, Callable, Type

from unifair.config.engine import LocalRunnerConfig
from unifair.engine.job_runner import DagFlowRunnerEngine, TaskRunnerEngine
from unifair.engine.protocols import IsDagFlow, IsLocalRunnerConfig, IsTask


class LocalRunner(TaskRunnerEngine, DagFlowRunnerEngine):
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

    def _init_dag_flow(self, flow: IsDagFlow) -> Any:
        ...

    def _run_dag_flow(self, state: Any, flow: IsDagFlow, *args, **kwargs) -> Any:
        return self.default_dag_flow_run_decorator(flow)(*args, **kwargs)
