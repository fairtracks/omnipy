"""Protocols for engines that decorate runnable jobs."""

from typing import Callable, Protocol, runtime_checkable

from omnipy.shared.enums.job import JobType
from omnipy.shared.protocols.compute.job import IsFuncArgJob
from omnipy.shared.protocols.engine.base import IsEngine


@runtime_checkable
class IsJobRunnerEngine(IsEngine, Protocol):
    """"""
    supported_job_types: frozenset[JobType.Literals]

    def supports(self, job_type: JobType.Literals) -> bool:
        ...

    def apply_job_decorator(
        self,
        job_type: JobType.Literals,
        job: IsFuncArgJob,
        job_callback_accept_decorator: Callable,
    ) -> None:
        ...
