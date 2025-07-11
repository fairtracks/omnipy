from datetime import datetime
from typing import Protocol, runtime_checkable

from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.mixins import IsUniquelyNamedJob


@runtime_checkable
class IsRunStateRegistry(Protocol):
    """"""
    def __init__(self) -> None:
        ...

    def get_job_state(self, job: IsUniquelyNamedJob) -> RunState.Literals:
        ...

    def get_job_state_datetime(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> datetime:
        ...

    def all_jobs(self,
                 state: RunState.Literals | None = None) -> tuple[IsUniquelyNamedJob, ...]:  # noqa
        ...

    def set_job_state(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> None:
        ...
