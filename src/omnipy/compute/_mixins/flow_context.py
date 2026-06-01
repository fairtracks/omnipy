"""Flow-context mixin for applied flow jobs.

Concrete flow jobs compose this mixin to expose a context manager that proxies the
shared `JobCreator` nesting state. The mixin also records the timestamp of the last
top-level flow run observed by the job instance.
"""

from contextlib import AbstractContextManager
from datetime import datetime
from typing import cast

from omnipy.compute._job import JobBase
from omnipy.shared.protocols.compute.job import IsJob
from omnipy.shared.protocols.compute.mixins import IsNestedContext


class FlowContextJobMixin:
    """Add flow-context tracking to executable flow jobs."""
    def __init__(self) -> None:
        self._time_of_last_run: datetime | None = None

    @property
    def flow_context(self) -> IsNestedContext:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFLOW_FLOW_CONTEXT_SUMMARY}}
        #
        # {{ISFLOW_FLOW_CONTEXT_DETAILS}}
        """Return a context manager that enters and exits the shared flow context.

        Returns:
            IsNestedContext: Context manager that tracks top-level flow execution state.
"""
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
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISFLOW_TIME_OF_LAST_RUN_SUMMARY}}
        #
        # {{ISFLOW_TIME_OF_LAST_RUN_DETAILS}}
        """Return the timestamp captured for the most recent top-level flow run.

        Returns:
            datetime | None: Timestamp from the latest top-level flow run, or ``None`` if the
                flow has not completed one yet.
"""
        return self._time_of_last_run
