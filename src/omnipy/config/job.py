from dataclasses import dataclass
from enum import Enum


class ConfigPersistOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    ENABLE_FLOW_OUTPUTS = 'flow'
    ENABLE_FLOW_AND_TASK_OUTPUTS = 'all'


class ConfigRestoreOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    AUTO_ENABLE_IGNORE_PARAMS = 'auto_ignore_params'


@dataclass
class JobConfig:
    persist_outputs: ConfigPersistOutputsOptions = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    restore_outputs: ConfigRestoreOutputsOptions = \
        ConfigRestoreOutputsOptions.DISABLED
