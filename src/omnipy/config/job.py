import os
from pathlib import Path

from omnipy.api.enums import (ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions)
from omnipy.api.protocols.public.config import (IsLocalOutputStorageConfig,
                                                IsOutputStorageConfig,
                                                IsS3OutputStorageConfig)
from omnipy.util.publisher import DataPublisher
import omnipy.util.pydantic as pyd


def _get_persist_data_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('outputs')))


class LocalOutputStorageConfig(DataPublisher):
    persist_data_dir_path: str = pyd.Field(default_factory=_get_persist_data_dir_path)


class S3OutputStorageConfig(DataPublisher):
    persist_data_dir_path: str = os.path.join('omnipy', 'outputs')
    endpoint_url: str = ''
    bucket_name: str = ''
    access_key: str = ''
    secret_key: str = ''


class OutputStorageConfig(DataPublisher):
    persist_outputs: ConfigPersistOutputsOptions = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    restore_outputs: ConfigRestoreOutputsOptions = \
        ConfigRestoreOutputsOptions.DISABLED
    protocol: ConfigOutputStorageProtocolOptions = ConfigOutputStorageProtocolOptions.LOCAL
    local: IsLocalOutputStorageConfig = pyd.Field(default_factory=LocalOutputStorageConfig)
    s3: IsS3OutputStorageConfig = pyd.Field(default_factory=S3OutputStorageConfig)


class JobConfig(DataPublisher):
    output_storage: IsOutputStorageConfig = pyd.Field(default_factory=OutputStorageConfig)
