from datetime import datetime
from typing import Any, Optional, Protocol, Tuple

from unifair.engine.constants import RunState


class EngineConfigProtocol(Protocol):
    ...


class EngineProtocol(Protocol):
    def __init__(
            self,
            config: Optional[EngineConfigProtocol] = None,  # noqa
            registry: Optional['RunStateRegistryProtocol'] = None):  # noqa
        ...


class RuntimeConfigProtocol(Protocol):
    engine: EngineProtocol
    registry: Optional['RunStateRegistryProtocol'] = None

    def __init__(
            self,
            engine: EngineProtocol,  # noqa
            registry: Optional['RunStateRegistryProtocol'],  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class TaskProtocol(Protocol):
    name: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...

    @classmethod
    def set_runtime(cls, runtime: RuntimeConfigProtocol) -> None:
        ...


class TaskTemplateProtocol(TaskProtocol):
    def apply(self) -> TaskProtocol:
        ...


class RunStateRegistryProtocol:
    def get_task_state(self, task: TaskProtocol) -> RunState:
        ...

    def get_task_state_datetime(self, task: TaskProtocol, state: RunState) -> datetime:
        ...

    def all_tasks(self, state: Optional[RunState] = None) -> Tuple[TaskProtocol, ...]:  # noqa
        ...

    def set_task_state(self, task: TaskProtocol, state: RunState) -> None:
        ...
