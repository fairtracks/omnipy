from collections import defaultdict
from typing import Protocol, TextIO

from omnipy.api.enums import (BackoffStrategy,
                              ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions)
from omnipy.api.protocols.private.util import IsDataPublisher
from omnipy.api.typedefs import LocaleType


class IsEngineConfig(IsDataPublisher, Protocol):
    """"""
    ...


class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    """"""
    ...


class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    """"""
    use_cached_results: bool = False


class IsJobConfig(IsDataPublisher, Protocol):
    """"""
    output_storage: 'IsOutputStorageConfig'


class IsDataConfig(IsDataPublisher, Protocol):
    """"""
    interactive_mode: bool
    dynamically_convert_elements_to_models: bool
    terminal_size_columns: int
    terminal_size_lines: int
    http_defaults: 'IsHttpConfig'
    http_config_for_host: defaultdict[str, 'IsHttpConfig']


class IsHttpConfig(IsDataPublisher, Protocol):
    """"""
    requests_per_time_period: float
    time_period_in_secs: float
    retry_http_statuses: tuple[int, ...]
    retry_attempts: int
    retry_backoff_strategy: BackoffStrategy


class IsRootLogConfig(IsDataPublisher, Protocol):
    """"""
    log_format_str: str
    locale: LocaleType
    log_to_stdout: bool
    log_to_stderr: bool
    log_to_file: bool
    stdout: TextIO
    stderr: TextIO
    stdout_log_min_level: int
    stderr_log_min_level: int
    file_log_min_level: int
    file_log_path: str


class IsOutputStorageConfigBase(IsDataPublisher, Protocol):
    persist_data_dir_path: str


class IsLocalOutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    ...


class IsS3OutputStorageConfig(IsOutputStorageConfigBase, Protocol):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str


class IsOutputStorageConfig(IsDataPublisher, Protocol):
    persist_outputs: ConfigPersistOutputsOptions
    restore_outputs: ConfigRestoreOutputsOptions
    protocol: ConfigOutputStorageProtocolOptions
    local: IsLocalOutputStorageConfig
    s3: IsS3OutputStorageConfig
