from typing import Any, Type

from unifair.config.engine import LocalRunnerConfig
from unifair.engine.protocols import IsLocalRunnerConfig, IsTask
from unifair.engine.task_runner import TaskRunnerEngine


class LocalRunner(TaskRunnerEngine):
    def _init_engine(self) -> None:
        ...

    def _update_from_config(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsLocalRunnerConfig]:
        return LocalRunnerConfig

    def _init_task(self, task: IsTask) -> None:
        ...

    def _run_task(self, task: IsTask, *args, **kwargs) -> Any:
        return task(*args, **kwargs)
