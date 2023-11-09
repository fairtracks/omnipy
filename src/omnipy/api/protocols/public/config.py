from __future__ import annotations

from typing import Protocol, runtime_checkable

from omnipy.api.enums import (ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions)
from omnipy.api.types import LocaleType


@runtime_checkable
class IsEngineConfig(Protocol):
    """"""
    ...


@runtime_checkable
class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    """"""
    ...


@runtime_checkable
class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    """"""
    use_cached_results: int = False


@runtime_checkable
class IsJobConfig(Protocol):
    """"""
    output_storage: IsOutputStorage


@runtime_checkable
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


@runtime_checkable
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
