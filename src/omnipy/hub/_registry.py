from collections import defaultdict
from datetime import datetime
from typing import DefaultDict

from omnipy.hub.log.mixin import LogMixin
from omnipy.shared.enums.job import RunState, RunStateLogMessages
from omnipy.shared.protocols.compute._job import IsUniquelyNamedJob


class RunStateRegistry(LogMixin):
    def __init__(self) -> None:

        self._jobs: dict[str, IsUniquelyNamedJob] = {}
        self._job_states: dict[str, RunState.Literals] = {}
        self._state_jobs: DefaultDict[RunState.Literals, list[str]] = defaultdict(list)
        self._job_state_datetime: dict[tuple[str, RunState.Literals], datetime] = {}

        super().__init__()

    def get_job_state(self, job: IsUniquelyNamedJob) -> RunState.Literals:
        return self._job_states[job.unique_name]

    def get_job_state_datetime(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> datetime:
        return self._job_state_datetime[(job.unique_name, state)]

    def all_jobs(self, state: RunState.Literals | None = None) -> tuple[IsUniquelyNamedJob, ...]:
        if state is not None:
            job_unique_names = self._state_jobs[state]
            return tuple(self._jobs[unique_name] for unique_name in job_unique_names)
        else:
            return tuple(self._jobs.values())

    def set_job_state(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> None:
        cur_datetime = datetime.now()

        if job.unique_name in self._jobs:
            self._update_job_registration(job, state)
        else:
            self._register_new_job(job, state)

        self._update_job_stats(job, state, cur_datetime)
        self._log_state_change(job, state)

    def _other_job_registered_with_same_unique_name(self, job: IsUniquelyNamedJob) -> bool:
        other_job_same_unique_name = self._jobs.get(job.unique_name)
        return bool(other_job_same_unique_name) and id(other_job_same_unique_name) != id(job)

    def _update_job_registration(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> None:
        # TODO: Reimplement logic using a state machine, e.g. "transitions" package
        if self._other_job_registered_with_same_unique_name(job):
            while self._other_job_registered_with_same_unique_name(job):
                job.regenerate_unique_name()
            self._register_new_job(job, state)
        else:
            prev_state = self._job_states[job.unique_name]
            if state == prev_state + 1:
                self._state_jobs[prev_state].remove(job.unique_name)
            else:
                self._raise_job_error(
                    job,
                    f'Transitioning from state {RunState.name_for_value(prev_state)} '
                    f'to state {RunState.name_for_value(state)} is not allowed',
                )

    def _register_new_job(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> None:
        if state != RunState.INITIALIZED:
            self._raise_job_error(
                job,
                f'Initial state of must be "INITIALIZED", not "{RunState.name_for_value(state)}"',
            )
        self._jobs[job.unique_name] = job

    def _update_job_stats(
        self,
        job: IsUniquelyNamedJob,
        state: RunState.Literals,
        cur_datetime: datetime,
    ) -> None:
        self._job_states[job.unique_name] = state
        self._state_jobs[state].append(job.unique_name)
        self._job_state_datetime[(job.unique_name, state)] = cur_datetime

    def _log_state_change(self, job: IsUniquelyNamedJob, state: RunState.Literals) -> None:
        log_template = getattr(RunStateLogMessages, RunState.name_for_value(state))
        log_msg = log_template.format(job.unique_name)
        datetime_obj = self.get_job_state_datetime(job, state)
        self.log(log_msg, datetime_obj=datetime_obj)

    def _raise_job_error(self, job: IsUniquelyNamedJob, msg: str) -> None:
        raise ValueError(f'Error in job "{job.unique_name}": {msg}')
