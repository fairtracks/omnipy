from contextlib import AbstractContextManager
from datetime import datetime
from typing import cast

from omnipy.compute._job import JobBase
from omnipy.shared.protocols.compute._job import IsJob
from omnipy.shared.protocols.compute.mixins import IsNestedContext


class FlowContextJobMixin:
    """"""
    def __init__(self) -> None:
        self._time_of_last_run: datetime | None = None

    @property
    def flow_context(self) -> IsNestedContext:
        class FlowContext(AbstractContextManager):
            @classmethod
            def __enter__(cls) -> None:  # pyright: ignore [reportIncompatibleMethodOverride]
                self_as_job_base = cast(JobBase, self)
                self_as_job_base.__class__.job_creator.__enter__()
                self_as_job = cast(IsJob, self)
                self._time_of_last_run = self_as_job.time_of_cur_toplevel_flow_run

            @classmethod
            def __exit__(  # pyright: ignore [reportIncompatibleMethodOverride]
                    cls,
                    exc_type,
                    exc_value,
                    traceback) -> None:
                self_as_job_base = cast(JobBase, self)
                self_as_job_base.__class__.job_creator.__exit__(exc_type, exc_value, traceback)

        return FlowContext()

    @property
    def time_of_last_run(self) -> datetime | None:
        return self._time_of_last_run
