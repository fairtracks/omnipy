"""Context and configuration objects shared across job classes.

`JobCreator` tracks the engine, job configuration, and nested execution context used
by a concrete job family. `JobBaseMeta` exposes a shared creator instance on each job
class so templates, applied jobs, and flow-context mixins all observe the same runtime
state.
"""

from abc import ABCMeta
from contextlib import AbstractContextManager
from datetime import datetime

from omnipy.config.job import JobConfig
from omnipy.shared.protocols.compute.job_creator import IsJobCreator
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.engine.base import IsEngine


class JobCreator(AbstractContextManager):
    """Manage shared runtime state for a concrete job class hierarchy."""

    def __init__(self) -> None:
        self._engine: IsEngine | None = None
        self._config: IsJobConfig = JobConfig()
        self._nested_context_level: int = 0
        self._time_of_cur_toplevel_nested_context_run: datetime | None = None

    def set_engine(self, engine: IsEngine) -> None:
        """Set the engine used when newly applied jobs are decorated."""
        self._engine = engine

    def set_config(self, config: IsJobConfig) -> None:
        """Replace the shared job configuration object."""
        self._config = config

    def __enter__(self):
        """Enter a nested job-execution context and record top-level start time."""
        if self._nested_context_level == 0:
            self._time_of_cur_toplevel_nested_context_run = datetime.now()

        self._nested_context_level += 1

    def __exit__(self, exc_type, exc_value, traceback):
        """Leave a nested job-execution context and clear top-level state when done."""
        self._nested_context_level -= 1

        if self._nested_context_level == 0:
            self._time_of_cur_toplevel_nested_context_run = None

    @property
    def engine(self) -> IsEngine | None:
        """Return the engine currently configured for this job family."""
        return self._engine

    @property
    def config(self) -> IsJobConfig:
        """Return the configuration currently configured for this job family."""
        return self._config

    @property
    def nested_context_level(self) -> int:
        """Return the current depth of nested job-execution contexts."""
        return self._nested_context_level

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> datetime | None:
        """Return the start time for the active top-level execution context, if any."""
        return self._time_of_cur_toplevel_nested_context_run


class JobBaseMeta(ABCMeta):
    """Expose the shared `JobCreator` for each concrete `JobBase` subclass."""

    _job_creator_obj = JobCreator()

    @property
    def job_creator(self) -> IsJobCreator:
        """Return the shared creator object used by the job class hierarchy."""
        return self._job_creator_obj

    @property
    def nested_context_level(self) -> int:
        """Return the nested execution depth tracked by the shared creator."""
        return self.job_creator.nested_context_level
