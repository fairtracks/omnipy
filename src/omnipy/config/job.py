# from dataclasses import field
import os
# from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from omnipy.api.enums import (ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions)
from omnipy.api.protocols.public.config import (IsLocalOutputStorage,
                                                IsOutputStorage,
                                                IsS3OutputStorage)

# from typing import Optional


def _get_persist_data_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('outputs')))


# @dataclass
class LocalOutputStorage:
    persist_data_dir_path: str = Field(default_factory=_get_persist_data_dir_path)


# @dataclass
class S3OutputStorage:
    persist_data_dir_path: str = os.path.join('omnipy', 'outputs')
    endpoint_url: str = ""
    bucket_name: str = ""
    access_key: str = ""
    secret_key: str = ""


# @dataclass
class OutputStorage:
    persist_outputs: ConfigPersistOutputsOptions = \
        ConfigPersistOutputsOptions.ENABLE_FLOW_AND_TASK_OUTPUTS
    restore_outputs: ConfigRestoreOutputsOptions = \
        ConfigRestoreOutputsOptions.DISABLED
    protocol: ConfigOutputStorageProtocolOptions = ConfigOutputStorageProtocolOptions.LOCAL
    local: IsLocalOutputStorage = Field(default_factory=LocalOutputStorage)
    s3: IsS3OutputStorage = Field(default_factory=S3OutputStorage)


# @dataclass
class JobConfig(BaseModel):
    output_storage: IsOutputStorage = Field(default_factory=OutputStorage)
