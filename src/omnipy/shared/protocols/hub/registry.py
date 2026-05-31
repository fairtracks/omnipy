"""Protocols for tracking job run-state transitions."""

from datetime import datetime
import os
from textwrap import dedent
from typing import Protocol, runtime_checkable

from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute.mixins import IsUniquelyNamedJob
from omnipy.util.helpers import is_package_editable


if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISRUNSTATEREGISTRY_GET_JOB_STATE_SUMMARY'] = (
        'Return the current run state registered for a job.')
    os.environ['OMNIPY_MACRO_ISRUNSTATEREGISTRY_GET_JOB_STATE_DETAILS'] = dedent("""\
        Args:
            job: Job whose current run state should be looked up.

        Returns:
            RunState.Literals: Current run-state literal for the job.
    """)

    os.environ['OMNIPY_MACRO_ISRUNSTATEREGISTRY_GET_JOB_STATE_DATETIME_SUMMARY'] = (
        'Return when the job was recorded in a specific run state.')
    os.environ['OMNIPY_MACRO_ISRUNSTATEREGISTRY_GET_JOB_STATE_DATETIME_DETAILS'] = dedent("""\
        Args:
            job: Job whose transition time should be looked up.
            state: Run-state literal to query.

        Returns:
            datetime: Timestamp recorded for the requested transition.
    """)

    os.environ['OMNIPY_MACRO_ISRUNSTATEREGISTRY_ALL_JOBS_SUMMARY'] = (
        'Return all registered jobs, optionally filtered by their current state.')
    os.environ['OMNIPY_MACRO_ISRUNSTATEREGISTRY_ALL_JOBS_DETAILS'] = dedent("""\
        Args:
            state: Optional run-state filter limiting the returned jobs.

        Returns:
            tuple[IsUniquelyNamedJob, ...]: Registered jobs matching the requested filter.
    """)

    os.environ['OMNIPY_MACRO_ISRUNSTATEREGISTRY_SET_JOB_STATE_SUMMARY'] = (
        'Register a job transition, update indexes, and emit the matching log event.')
    os.environ['OMNIPY_MACRO_ISRUNSTATEREGISTRY_SET_JOB_STATE_DETAILS'] = dedent("""\
        Args:
            job: Job whose state transition should be recorded.
            state: New run-state literal to register.
    """)


@runtime_checkable
class IsRunStateRegistry(Protocol):
    """Protocol for registries that track job run states."""

    def __init__(self) -> None:
        ...

    def get_job_state(self, job: IsUniquelyNamedJob) -> RunState.Literals:
        """{{ISRUNSTATEREGISTRY_GET_JOB_STATE_SUMMARY}}

        {{ISRUNSTATEREGISTRY_GET_JOB_STATE_DETAILS}}"""
        ...

    def get_job_state_datetime(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> datetime:
        """{{ISRUNSTATEREGISTRY_GET_JOB_STATE_DATETIME_SUMMARY}}

        {{ISRUNSTATEREGISTRY_GET_JOB_STATE_DATETIME_DETAILS}}"""
        ...

    def all_jobs(self,
                 state: RunState.Literals | None = None) -> tuple[IsUniquelyNamedJob, ...]:  # noqa
        """{{ISRUNSTATEREGISTRY_ALL_JOBS_SUMMARY}}

        {{ISRUNSTATEREGISTRY_ALL_JOBS_DETAILS}}"""
        ...

    def set_job_state(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> None:
        """{{ISRUNSTATEREGISTRY_SET_JOB_STATE_SUMMARY}}

        {{ISRUNSTATEREGISTRY_SET_JOB_STATE_DETAILS}}"""
        ...
