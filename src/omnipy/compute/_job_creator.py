"""Context and configuration objects shared across job classes.

`JobCreator` tracks the engine, job configuration, and nested execution context used
by a concrete job family. `JobBaseMeta` exposes a shared creator instance on each job
class so templates, applied jobs, and flow-context mixins all observe the same runtime
state.
"""

from abc import ABCMeta
from contextlib import AbstractContextManager
from datetime import datetime
from typing import cast

from omnipy.config.job import JobConfig
from omnipy.shared.protocols.compute.job_creator import IsJobCreator
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.engine.base import IsEngine


class JobCreator(AbstractContextManager):
    """Manage shared runtime state for a concrete job class hierarchy."""

    def __init__(self) -> None:
        self._engine: IsEngine | None = None
        self._config: IsJobConfig = cast(IsJobConfig, JobConfig())
        self._nested_context_level: int = 0
        self._time_of_cur_toplevel_nested_context_run: datetime | None = None

    def set_engine(self, engine: IsEngine) -> None:
        """{{ISJOBCONFIGHOLDER_SET_ENGINE_SUMMARY}}

        {{ISJOBCONFIGHOLDER_SET_ENGINE_DETAILS}}"""
        self._engine = engine

    def set_config(self, config: IsJobConfig) -> None:
        """{{ISJOBCONFIGHOLDER_SET_CONFIG_SUMMARY}}

        {{ISJOBCONFIGHOLDER_SET_CONFIG_DETAILS}}"""
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
        """{{ISJOBCONFIGHOLDER_ENGINE_SUMMARY}}

        {{ISJOBCONFIGHOLDER_ENGINE_DETAILS}}"""
        return self._engine

    @property
    def config(self) -> IsJobConfig:
        """{{ISJOBCONFIGHOLDER_CONFIG_SUMMARY}}

        {{ISJOBCONFIGHOLDER_CONFIG_DETAILS}}"""
        return self._config

    @property
    def nested_context_level(self) -> int:
        """{{ISJOBCREATOR_NESTED_CONTEXT_LEVEL_SUMMARY}}

        {{ISJOBCREATOR_NESTED_CONTEXT_LEVEL_DETAILS}}"""
        return self._nested_context_level

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> datetime | None:
        """{{ISJOBCREATOR_TIME_OF_CUR_TOPLEVEL_NESTED_CONTEXT_RUN_SUMMARY}}

        {{ISJOBCREATOR_TIME_OF_CUR_TOPLEVEL_NESTED_CONTEXT_RUN_DETAILS}}"""
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
        """{{ISJOBCREATOR_NESTED_CONTEXT_LEVEL_SUMMARY}}

        {{ISJOBCREATOR_NESTED_CONTEXT_LEVEL_DETAILS}}"""
        return self.job_creator.nested_context_level
