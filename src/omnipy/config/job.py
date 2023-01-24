from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from omnipy.abstract.enums import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions


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
