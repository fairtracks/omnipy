from dataclasses import dataclass, field
import os
from pathlib import Path

from omnipy.api.enums import (ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions)
from omnipy.api.protocols.public.config import (IsLocalOutputStorageConfig,
                                                IsOutputStorageConfig,
                                                IsS3OutputStorageConfig)


def _get_persist_data_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('outputs')))


@dataclass
class LocalOutputStorageConfig:
    persist_data_dir_path: str = field(default_factory=_get_persist_data_dir_path)


@dataclass
class S3OutputStorageConfig:
    persist_data_dir_path: str = os.path.join('omnipy', 'outputs')
    endpoint_url: str = ''
    bucket_name: str = ''
    access_key: str = ''
    secret_key: str = ''


@dataclass
class OutputStorageConfig:
    persist_outputs: ConfigPersistOutputsOptions = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    restore_outputs: ConfigRestoreOutputsOptions = \
        ConfigRestoreOutputsOptions.DISABLED
    protocol: ConfigOutputStorageProtocolOptions = ConfigOutputStorageProtocolOptions.LOCAL
    local: IsLocalOutputStorageConfig = field(default_factory=LocalOutputStorageConfig)
    s3: IsS3OutputStorageConfig = field(default_factory=S3OutputStorageConfig)


@dataclass
class JobConfig:
    output_storage: IsOutputStorageConfig = field(default_factory=OutputStorageConfig)
