from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Optional, Protocol, runtime_checkable, Tuple, Type

from omnipy.api.enums import RunState


class IsUniquelyNamedJob(Protocol):
    """"""
    unique_name: str

    def regenerate_unique_name(self) -> None:
        ...


class IsRunStateRegistry(Protocol):
    """"""
    def __init__(self) -> None:
        ...

    def get_job_state(self, job: IsUniquelyNamedJob) -> RunState:
        ...

    def get_job_state_datetime(self, job: IsUniquelyNamedJob, state: RunState) -> datetime:
        ...

    def all_jobs(self, state: Optional[RunState] = None) -> Tuple[IsUniquelyNamedJob, ...]:  # noqa
        ...

    def set_job_state(self, job: IsUniquelyNamedJob, state: RunState) -> None:
        ...


class IsDataPublisher(Protocol):
    """"""
    def subscribe(self, config_item: str, callback_fun: Callable[[Any], None]):
        ...

    def unsubscribe_all(self) -> None:
        ...


@runtime_checkable
class IsEngine(Protocol):
    """"""
    def __init__(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        ...

    def set_config(self, config: IsEngineConfig) -> None:
        ...

    def set_registry(self, registry: Optional[IsRunStateRegistry]) -> None:
        ...


class IsEngineConfig(Protocol):
    """"""
    ...
