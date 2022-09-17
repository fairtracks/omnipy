from enum import Enum, IntEnum


class RunState(IntEnum):
    INITIALIZED = 1
    RUNNING = 2
    FINISHED = 3


class RunStateLogMessages(Enum):
    INITIALIZED: str = 'Initialized task "{}"'
    RUNNING: str = 'Started running task "{}"...'
    FINISHED: str = 'Task "{}" finished!'


UNIFAIR_LOG_FORMAT_STR: str = '%(levelname)s (%(name)s) - %(message)s'
