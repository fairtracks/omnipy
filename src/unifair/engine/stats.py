from collections import defaultdict
from datetime import datetime
from enum import Enum, IntEnum
import logging
from typing import DefaultDict, Dict, List, Optional, Tuple, Union

from unifair.engine.protocols import TaskProtocol
from unifair.util.helpers import get_datetime_format


class State(IntEnum):
    INITIALIZED = 1
    RUNNING = 2
    FINISHED = 3


class StateLogMessages(Enum):
    INITIALIZED: str = 'Initialized task "{}"'
    RUNNING: str = 'Started running task "{}"...'
    FINISHED: str = 'Task "{}" finished!'


UNIFAIR_LOG_FORMAT_STR: str = '%(levelname)s (%(name)s) - %(message)s'


class RunStats:
    def __init__(self) -> None:
        self._datetime_format: Optional[str] = None
        self._logger: Optional[logging.Logger] = None

        self._tasks: Dict[str, TaskProtocol] = {}
        self._task_states: Dict[str, State] = {}
        self._state_tasks: DefaultDict[State, List[str]] = defaultdict(list)
        self._task_state_datetime: Dict[Tuple[str, State], datetime] = {}

    def get_task_state(self, task: TaskProtocol) -> State:
        return self._task_states[task.name]

    def get_task_state_datetime(self, task: TaskProtocol, state: State) -> datetime:
        return self._task_state_datetime[(task.name, state)]

    def all_tasks(self, state: Optional[State] = None) -> Tuple[TaskProtocol, ...]:
        if state is not None:
            task_names = self._state_tasks[state]
            return tuple(self._tasks[name] for name in task_names)
        else:
            return tuple(self._tasks.values())

    def set_logger(self,
                   logger: logging.Logger,
                   set_unifair_formatter_on_handlers=True,
                   locale: Union[str, Tuple[str, str]] = '') -> None:

        self._logger = logger
        self._datetime_format = get_datetime_format(locale)

        if set_unifair_formatter_on_handlers:
            formatter = logging.Formatter(UNIFAIR_LOG_FORMAT_STR)

            for handler in self._logger.handlers:
                if set_unifair_formatter_on_handlers:
                    handler.setFormatter(formatter)

    def set_task_state(self, task: TaskProtocol, state: State) -> None:
        cur_datetime = datetime.now()

        if task.name in self._tasks:
            self._update_task_registration(task, state)
        else:
            self._register_new_task(task, state)

        self._update_task_stats(task, state, cur_datetime)
        self._log_state_change(task, state)

    def _update_task_registration(self, task: TaskProtocol, state: State) -> None:
        if id(self._tasks[task.name]) != id(task):
            self._raise_task_error(
                task,
                f'Another task with the same name has already been registered',
            )
        prev_state = self._task_states[task.name]
        if state == prev_state + 1:
            self._state_tasks[prev_state].remove(task.name)
        else:
            self._raise_task_error(
                task,
                f'Transitioning from state {prev_state.name} '
                f'to state {state.name} is not allowed',
            )

    def _register_new_task(self, task, state) -> None:
        if state != State.INITIALIZED:
            self._raise_task_error(
                task,
                f'Initial state of must be "INITIALIZED", not "{state.name}"',
            )
        self._tasks[task.name] = task

    def _update_task_stats(self, task, state, cur_datetime) -> None:
        self._task_states[task.name] = state
        self._state_tasks[state].append(task.name)
        self._task_state_datetime[(task.name, state)] = cur_datetime

    def _log_state_change(self, task: TaskProtocol, state: State) -> None:
        if self._logger is not None:
            datetime_str = self.get_task_state_datetime(task, state).strftime(self._datetime_format)
            log_msg = StateLogMessages[state.name].value.format(task.name)
            self._logger.info(f'{datetime_str}: {log_msg}')

    def _raise_task_error(self, task: TaskProtocol, msg: str) -> None:
        raise ValueError(f'Error in task "{task.name}": {msg}')
