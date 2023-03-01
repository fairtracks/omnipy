from collections import defaultdict
from datetime import datetime
from typing import DefaultDict, Dict, List, Optional, Tuple

from omnipy.api.enums import RunState, RunStateLogMessages
from omnipy.api.protocols import IsJob
from omnipy.log.mixin import LogMixin


class RunStateRegistry(LogMixin):
    def __init__(self) -> None:

        self._jobs: Dict[str, IsJob] = {}
        self._job_states: Dict[str, RunState] = {}
        self._state_jobs: DefaultDict[RunState, List[str]] = defaultdict(list)
        self._job_state_datetime: Dict[Tuple[str, RunState], datetime] = {}

        super().__init__()

    def get_job_state(self, job: IsJob) -> RunState:
        return self._job_states[job.unique_name]

    def get_job_state_datetime(self, job: IsJob, state: RunState) -> datetime:
        return self._job_state_datetime[(job.unique_name, state)]

    def all_jobs(self, state: Optional[RunState] = None) -> Tuple[IsJob, ...]:
        if state is not None:
            job_unique_names = self._state_jobs[state]
            return tuple(self._jobs[unique_name] for unique_name in job_unique_names)
        else:
            return tuple(self._jobs.values())

    def set_job_state(self, job: IsJob, state: RunState) -> None:
        cur_datetime = datetime.now()

        if job.unique_name in self._jobs:
            self._update_job_registration(job, state)
        else:
            self._register_new_job(job, state)

        self._update_job_stats(job, state, cur_datetime)
        self._log_state_change(job, state)

    def _other_job_registered_with_same_unique_name(self, job: IsJob) -> bool:
        other_job_same_unique_name = self._jobs.get(job.unique_name)
        return bool(other_job_same_unique_name) and id(other_job_same_unique_name) != id(job)

    def _update_job_registration(self, job: IsJob, state: RunState) -> None:
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
                    f'Transitioning from state {prev_state.name} '
                    f'to state {state.name} is not allowed',
                )

    def _register_new_job(self, job, state) -> None:
        if state != RunState.INITIALIZED:
            self._raise_job_error(
                job,
                f'Initial state of must be "INITIALIZED", not "{state.name}"',
            )
        self._jobs[job.unique_name] = job

    def _update_job_stats(self, job, state, cur_datetime) -> None:
        self._job_states[job.unique_name] = state
        self._state_jobs[state].append(job.unique_name)
        self._job_state_datetime[(job.unique_name, state)] = cur_datetime

    def _log_state_change(self, job: IsJob, state: RunState) -> None:
        log_msg = RunStateLogMessages[state.name].value.format(job.unique_name)
        datetime_obj = self.get_job_state_datetime(job, state)
        self.log(log_msg, datetime_obj=datetime_obj)

    def _raise_job_error(self, job: IsJob, msg: str) -> None:
        raise ValueError(f'Error in job "{job.unique_name}": {msg}')
