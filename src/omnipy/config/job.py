from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class ConfigPersistOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    ENABLE_FLOW_OUTPUTS = 'flow'
    ENABLE_FLOW_AND_TASK_OUTPUTS = 'all'


class ConfigRestoreOutputsOptions(str, Enum):
    DISABLED = 'disabled'
    AUTO_ENABLE_IGNORE_PARAMS = 'auto_ignore_params'


def _get_persist_data_dir_path():
    return str(Path.cwd().joinpath(Path('data')))


@dataclass
class JobConfig:
    persist_outputs: ConfigPersistOutputsOptions = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    restore_outputs: ConfigRestoreOutputsOptions = \
        ConfigRestoreOutputsOptions.DISABLED
    persist_data_dir_path: Path = field(default_factory=_get_persist_data_dir_path)
    datetime_of_nested_context: Optional[datetime] = None
