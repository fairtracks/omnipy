from __future__ import annotations

from datetime import datetime
from logging import INFO, Logger
from typing import Optional, Protocol, Tuple

from omnipy.api.enums import RunState
from omnipy.api.protocols.private.compute.mixins import IsUniquelyNamedJob


class CanLog(Protocol):
    """"""
    @property
    def logger(self) -> Logger:
        ...

    def log(self, log_msg: str, level: int = INFO, datetime_obj: Optional[datetime] = None):
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
