from typing import Any, Type

from unifair.engine.constants import RunState
from unifair.engine.protocols import IsEngineConfig, IsTask
from unifair.engine.task_runner import TaskRunnerEngine


class TaskRunnerStateChecker(TaskRunnerEngine):
    def __init__(self, engine):
        self._engine = engine
        super().__init__()

    def _init_engine(self) -> None:
        self._engine._init_engine()  # noqa

    def get_config_cls(self) -> Type[IsEngineConfig]:
        return self._engine.get_config_cls()  # noqa

    def _update_from_config(self) -> None:
        return self._engine._update_from_config()  # noqa

    def _init_task(self, task: IsTask) -> None:
        from .functions import assert_task_state
        assert_task_state(task, [RunState.INITIALIZED])
        self._engine._init_task(task)  # noqa

    def _run_task(self, task: IsTask, *args: Any, **kwargs: Any) -> Any:
        from .functions import assert_task_state
        assert_task_state(task, [RunState.RUNNING])
        return self._engine._run_task(task, *args, **kwargs)  # noqa
