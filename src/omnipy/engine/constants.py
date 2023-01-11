from enum import Enum, IntEnum


class EngineChoice(str, Enum):
    LOCAL = 'local'
    PREFECT = 'prefect'


class RunState(IntEnum):
    INITIALIZED = 1
    RUNNING = 2
    FINISHED = 3


# TODO: Add 'apply' state
# TODO: Add 'failed' state and error management
# TODO: Consider the need for a 'waiting' state


class RunStateLogMessages(str, Enum):
    INITIALIZED = 'Initialized "{}"'
    RUNNING = 'Started running "{}"...'
    FINISHED = 'Finished running "{}"!'


UNIFAIR_LOG_FORMAT_STR: str = '%(levelname)s (%(name)s) - %(message)s'
