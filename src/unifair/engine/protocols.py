from typing import Any, Protocol

from unifair.engine.base import Engine


class RuntimeConfigProtocol(Protocol):
    engine: Engine

    def __init__(self, engine: Engine, *args: Any, **kwargs: Any) -> None:  # noqa
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
