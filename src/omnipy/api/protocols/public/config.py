from typing import Protocol

from omnipy.api.enums import (ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions)
from omnipy.api.typedefs import LocaleType


class IsEngineConfig(Protocol):
    """"""
    ...


class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    """"""
    ...


class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    """"""
    use_cached_results: int = False


class IsJobConfig(Protocol):
    """"""
    output_storage: 'IsOutputStorage'


class IsRootLogConfig(Protocol):
    """"""
    log_format_str: str
    locale: LocaleType
    log_to_stdout: bool
    log_to_stderr: bool
    log_to_file: bool
    stdout_log_min_level: int
    stderr_log_min_level: int
    file_log_min_level: int
    file_log_dir_path: str


class IsOutputStorageBase(Protocol):
    persist_data_dir_path: str


class IsLocalOutputStorage(IsOutputStorageBase, Protocol):
    ...


class IsS3OutputStorage(IsOutputStorageBase, Protocol):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str


class IsOutputStorage(Protocol):
    persist_outputs: ConfigPersistOutputsOptions
    restore_outputs: ConfigRestoreOutputsOptions
    protocol: ConfigOutputStorageProtocolOptions
    local: IsLocalOutputStorage
    s3: IsS3OutputStorage
