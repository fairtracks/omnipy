from enum import Enum, IntEnum


class EngineChoice(str, Enum):
    LOCAL = 'local'
    PREFECT = 'prefect'


class RunState(IntEnum):
    INITIALIZED = 1
    RUNNING = 2
    FINISHED = 3


class RunStateLogMessages(str, Enum):
    INITIALIZED = 'Initialized task "{}"'
    RUNNING = 'Started running task "{}"...'
    FINISHED = 'Task "{}" finished!'


UNIFAIR_LOG_FORMAT_STR: str = '%(levelname)s (%(name)s) - %(message)s'
