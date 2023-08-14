from dataclasses import dataclass, field
# from datetime import datetime
from pathlib import Path

from omnipy.api.enums import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions

# from typing import Optional


def _get_persist_data_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('data')))


@dataclass
class JobConfig:
    persist_outputs: ConfigPersistOutputsOptions = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    restore_outputs: ConfigRestoreOutputsOptions = \
        ConfigRestoreOutputsOptions.DISABLED
    persist_data_dir_path: str = field(default_factory=_get_persist_data_dir_path)
