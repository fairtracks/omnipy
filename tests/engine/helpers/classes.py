from typing import Any, Callable, Optional, Type

from unifair.engine.constants import RunState
from unifair.engine.protocols import IsEngineConfig, IsRunStateRegistry, IsTask, IsTaskRunnerEngine


class TaskRunnerStateChecker(IsTaskRunnerEngine):
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

    def _init_task(self, task: IsTask, call_func: Callable) -> Any:
        from .functions import assert_task_state
        assert_task_state(task, [RunState.INITIALIZED])
        return self._engine._init_task(task, call_func)  # noqa

    def _run_task(self, state: Any, task: IsTask, call_func: Callable, *args, **kwargs) -> Any:
        from .functions import assert_task_state
        assert_task_state(task, [RunState.RUNNING])
        return self._engine._run_task(state, task, call_func, *args, **kwargs)  # noqa
