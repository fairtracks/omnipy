from datetime import datetime
from typing import Any, Optional, Protocol, Tuple

from unifair.engine.constants import RunState


class RuntimeConfigProtocol(Protocol):
    engine: 'EngineProtocol'
    registry: Optional['RunStateRegistryProtocol'] = None
    verbose: bool = False

    def __init__(
            self,
            engine: 'EngineProtocol',  # noqa
            registry: Optional['RunStateRegistryProtocol'] = None,  # noqa
            verbose: bool = False,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class RuntimeDependentClsProtocol(Protocol):
    def set_runtime(self, runtime: RuntimeConfigProtocol) -> None:
        ...


class EngineConfigProtocol(Protocol):
    ...


class EngineProtocol(RuntimeDependentClsProtocol):
    def __init__(self, config: Optional[EngineConfigProtocol] = None):  # noqa
        ...


class TaskProtocol(RuntimeDependentClsProtocol):
    name: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...

    # Will currently fail in mypy, until this PR has been released:
    # https://github.com/python/mypy/pull/13501
    # TODO: add mypy exception if not supported yet, or remove comment if supported
    @classmethod
    def set_runtime(cls, runtime: RuntimeConfigProtocol) -> None:
        ...


class TaskTemplateProtocol(TaskProtocol):
    def apply(self) -> TaskProtocol:
        ...


class RunStateRegistryProtocol(RuntimeDependentClsProtocol):
    def __init__(self) -> None:
        ...

    def get_task_state(self, task: TaskProtocol) -> RunState:
        ...

    def get_task_state_datetime(self, task: TaskProtocol, state: RunState) -> datetime:
        ...

    def all_tasks(self, state: Optional[RunState] = None) -> Tuple[TaskProtocol, ...]:  # noqa
        ...

    def set_task_state(self, task: TaskProtocol, state: RunState) -> None:
        ...
