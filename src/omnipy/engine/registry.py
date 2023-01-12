from collections import defaultdict
from datetime import datetime
import logging
from typing import DefaultDict, Dict, List, Optional, Tuple, Union

from omnipy.config.registry import RunStateRegistryConfig
from omnipy.engine.constants import OMNIPY_LOG_FORMAT_STR, RunState, RunStateLogMessages
from omnipy.engine.protocols import IsJob, IsRunStateRegistryConfig
from omnipy.util.helpers import get_datetime_format


class RunStateRegistry:
    def __init__(self) -> None:
        self._datetime_format: Optional[str] = None
        self._logger: Optional[logging.Logger] = None
        self._config: IsRunStateRegistryConfig = RunStateRegistryConfig()

        self._jobs: Dict[str, IsJob] = {}
        self._job_states: Dict[str, RunState] = {}
        self._state_jobs: DefaultDict[RunState, List[str]] = defaultdict(list)
        self._job_state_datetime: Dict[Tuple[str, RunState], datetime] = {}

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

    def set_logger(self,
                   logger: Optional[logging.Logger],
                   set_omnipy_formatter_on_handlers=True,
                   locale: Union[str, Tuple[str, str]] = '') -> None:

        self._logger = logger
        if self._logger is not None:
            self._datetime_format = get_datetime_format(locale)

            if set_omnipy_formatter_on_handlers:
                formatter = logging.Formatter(OMNIPY_LOG_FORMAT_STR)
                for handler in self._logger.handlers:
                    handler.setFormatter(formatter)

    def set_config(self, config: IsRunStateRegistryConfig) -> None:
        self._config = config

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
        return other_job_same_unique_name and id(other_job_same_unique_name) != id(job)

    def _update_job_registration(self, job: IsJob, state: RunState) -> None:
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
        if self._logger is not None:
            log_msg = RunStateLogMessages[state.name].value.format(job.unique_name)
            datetime_obj = self.get_job_state_datetime(job, state)
            self.log(datetime_obj, log_msg)

    def log(self, datetime_obj: datetime, log_msg: str):
        if self._logger is not None:
            datetime_str = datetime_obj.strftime(self._datetime_format)
            self._logger.info(f'{datetime_str}: {log_msg}')

    def _raise_job_error(self, job: IsJob, msg: str) -> None:
        raise ValueError(f'Error in job "{job.unique_name}": {msg}')
