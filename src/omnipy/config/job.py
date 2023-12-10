from dataclasses import dataclass, field
import os
from pathlib import Path

from omnipy.api.enums import (ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions)
from omnipy.api.protocols.public.config import (IsLocalOutputStorage,
                                                IsOutputStorage,
                                                IsS3OutputStorage)


def _get_persist_data_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('outputs')))


@dataclass
class LocalOutputStorage:
    persist_data_dir_path: str = field(default_factory=_get_persist_data_dir_path)


@dataclass
class S3OutputStorage:
    persist_data_dir_path: str = os.path.join('omnipy', 'outputs')
    endpoint_url: str = ''
    bucket_name: str = ''
    access_key: str = ''
    secret_key: str = ''


@dataclass
class OutputStorage:
    persist_outputs: ConfigPersistOutputsOptions = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    restore_outputs: ConfigRestoreOutputsOptions = \
        ConfigRestoreOutputsOptions.DISABLED
    protocol: ConfigOutputStorageProtocolOptions = ConfigOutputStorageProtocolOptions.LOCAL
    local: IsLocalOutputStorage = field(default_factory=LocalOutputStorage)
    s3: IsS3OutputStorage = field(default_factory=S3OutputStorage)


@dataclass
class JobConfig:
    output_storage: IsOutputStorage = field(default_factory=OutputStorage)
