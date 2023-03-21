from __future__ import annotations

from typing import Protocol

from omnipy.api.enums import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions


class IsJobConfigBase(Protocol):
    """"""
    persist_outputs: ConfigPersistOutputsOptions
    restore_outputs: ConfigRestoreOutputsOptions
    persist_data_dir_path: str
