from __future__ import annotations

from typing import Optional, Protocol

from omnipy.api.enums import (ConfigOutputStorageProtocolOptions,
                              ConfigPersistOutputsOptions,
                              ConfigRestoreOutputsOptions,
                              EngineChoice)
from omnipy.api.types import LocaleType


class IsRuntimeConfig(Protocol):
    """"""
    job: IsJobConfig
    engine: EngineChoice
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    root_log: IsRootLogConfig

    def __init__(
            self,
            job: Optional[IsJobConfig] = None,  # noqa
            engine: EngineChoice = EngineChoice.LOCAL,  # noqa
            local: Optional[IsLocalRunnerConfig] = None,  # noqa
            prefect: Optional[IsPrefectEngineConfig] = None,  # noqa
            root_log: Optional[IsRootLogConfig] = None,  # noqa
            *args: object,
            **kwargs: object) -> None:
        ...


class IsJobConfig(Protocol):
    """"""
    output_storage: IsOutputStorage


class IsEngineConfig(Protocol):
    """"""
    ...


class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    """"""
    ...


class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    """"""
    use_cached_results: int = False


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


class IsOutputStorage(Protocol):
    persist_outputs: ConfigPersistOutputsOptions
    restore_outputs: ConfigRestoreOutputsOptions
    protocol: ConfigOutputStorageProtocolOptions
    local: IsLocalOutputStorage
    s3: IsS3OutputStorage


class IsOutputStorageProtocolBase(Protocol):
    persist_data_dir_path: str


class IsLocalOutputStorage(IsOutputStorageProtocolBase, Protocol):
    ...


class IsS3OutputStorage(IsOutputStorageProtocolBase, Protocol):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str
