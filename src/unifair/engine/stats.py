from collections import defaultdict
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

    def set_task_state(self, task: TaskProtocol, state: State) -> None:
        if task.name in self._tasks:
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
        else:
            if state != State.INITIALIZED:
                self._raise_task_error(
                    task,
                    f'Initial state of must be "INITIALIZED", not "{state.name}"',
                )
            self._tasks[task.name] = task
        self._task_states[task.name] = state
        self._state_tasks[state].append(task.name)

    def _raise_task_error(self, task: TaskProtocol, msg: str):
        raise ValueError(f'Error in task "{task.name}": {msg}')

    def get_task_state(self, task: TaskProtocol) -> State:
        return self._task_states[task.name]

    def all_tasks(self, state: Optional[State] = None) -> Tuple[TaskProtocol, ...]:
        if state is not None:
            task_names = self._state_tasks[state]
            return tuple(self._tasks[name] for name in task_names)
        else:
            return tuple(self._tasks.values())
