from __future__ import annotations

from enum import Enum, IntEnum


class PersistOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    FOLLOW_CONFIG = 'config'
    ENABLED = 'enabled'


class RestoreOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    FOLLOW_CONFIG = 'config'
    AUTO_ENABLE_IGNORE_PARAMS = 'auto_ignore_params'
    FORCE_ENABLE_IGNORE_PARAMS = 'force_ignore_params'


class ConfigPersistOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    ENABLE_FLOW_OUTPUTS = 'flow'
    ENABLE_FLOW_AND_TASK_OUTPUTS = 'all'


class ConfigRestoreOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    AUTO_ENABLE_IGNORE_PARAMS = 'auto_ignore_params'


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
