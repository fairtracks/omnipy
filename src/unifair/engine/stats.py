from collections import defaultdict
from datetime import datetime
from enum import IntEnum
from typing import DefaultDict, Dict, List, Optional, Tuple

from unifair.engine.protocols import TaskProtocol


class State(IntEnum):
    INITIALIZED = 1
    RUNNING = 2
    FINISHED = 3


class RunStats:
    def __init__(self) -> None:
        self._tasks: Dict[str, TaskProtocol] = {}
        self._task_states: Dict[str, State] = {}
        self._state_tasks: DefaultDict[State, List[str]] = defaultdict(list)
        self._task_state_datetime: Dict[Tuple[str, State], datetime] = {}

    def set_task_state(self, task: TaskProtocol, state: State) -> None:
        cur_datetime = datetime.now()

        if task.name in self._tasks:
            self._update_task_registration(task, state)
        else:
            self._register_new_task(task, state)

        self._update_task_stats(task, state, cur_datetime)

    def _update_task_registration(self, task: TaskProtocol, state: State):
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

    def _register_new_task(self, task, state):
        if state != State.INITIALIZED:
            self._raise_task_error(
                task,
                f'Initial state of must be "INITIALIZED", not "{state.name}"',
            )
        self._tasks[task.name] = task

    def _update_task_stats(self, task, state, cur_datetime):
        self._task_states[task.name] = state
        self._state_tasks[state].append(task.name)
        self._task_state_datetime[(task.name, state)] = cur_datetime

    def _raise_task_error(self, task: TaskProtocol, msg: str):
        raise ValueError(f'Error in task "{task.name}": {msg}')

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
