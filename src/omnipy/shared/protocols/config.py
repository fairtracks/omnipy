from collections import defaultdict
from io import TextIOBase
from typing import Protocol, runtime_checkable

from omnipy.shared.enums import (BackoffStrategy,
                                 ConfigOutputStorageProtocolOptions,
                                 ConfigPersistOutputsOptions,
                                 ConfigRestoreOutputsOptions)
from omnipy.shared.protocols.util import IsDataPublisher
from omnipy.shared.typedefs import LocaleType


@runtime_checkable
class IsEngineConfig(IsDataPublisher, Protocol):
    """"""
    ...


@runtime_checkable
class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    """"""
    ...


@runtime_checkable
class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    """"""
    use_cached_results: bool = False


@runtime_checkable
class IsJobConfig(IsDataPublisher, Protocol):
    """"""
    output_storage: 'IsOutputStorageConfig'


@runtime_checkable
class IsDataConfig(IsDataPublisher, Protocol):
    """"""
    interactive_mode: bool
    dynamically_convert_elements_to_models: bool
    terminal_size_columns: int
    terminal_size_lines: int
    http_defaults: 'IsHttpConfig'
    http_config_for_host: defaultdict[str, 'IsHttpConfig']


@runtime_checkable
class IsHttpConfig(IsDataPublisher, Protocol):
    """"""
    requests_per_time_period: float
    time_period_in_secs: float
    retry_http_statuses: tuple[int, ...]
    retry_attempts: int
    retry_backoff_strategy: BackoffStrategy


@runtime_checkable
class IsRootLogConfig(IsDataPublisher, Protocol):
    """"""
    log_format_str: str
    locale: LocaleType
    log_to_stdout: bool
    log_to_stderr: bool
    log_to_file: bool
    stdout: TextIOBase
    stderr: TextIOBase
    stdout_log_min_level: int
    stderr_log_min_level: int
    file_log_min_level: int
    file_log_path: str


@runtime_checkable
class IsOutputStorageConfigBase(IsDataPublisher, Protocol):
    persist_data_dir_path: str


@runtime_checkable
class IsLocalOutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    ...


@runtime_checkable
class IsS3OutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str


@runtime_checkable
class IsOutputStorageConfig(IsDataPublisher, Protocol):
    persist_outputs: ConfigPersistOutputsOptions
    restore_outputs: ConfigRestoreOutputsOptions
    protocol: ConfigOutputStorageProtocolOptions
    local: IsLocalOutputStorageConfig
    s3: IsS3OutputStorageConfig
