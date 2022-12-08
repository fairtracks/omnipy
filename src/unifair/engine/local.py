from typing import Any, Callable, Type

from unifair.config.engine import LocalRunnerConfig
from unifair.engine.job_runner import TaskRunnerEngine
from unifair.engine.protocols import IsLocalRunnerConfig, IsTask


class LocalRunner(TaskRunnerEngine):
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
