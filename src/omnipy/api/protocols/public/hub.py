from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Optional, Protocol

from omnipy.api.enums import EngineChoice
from omnipy.api.protocols.private.engine import IsEngine, IsEngineConfig
from omnipy.api.protocols.private.hub import IsDataPublisher, IsJobConfigBase, IsJobConfigHolder
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.types import LocaleType


class IsRuntimeConfig(IsDataPublisher, Protocol):
    """"""
    job: IsJobConfig
    engine: EngineChoice
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    root_log: IsRootLogConfigEntryPublisher

    def __init__(
            self,
            job: Optional[IsJobConfig] = None,  # noqa
            engine: EngineChoice = EngineChoice.LOCAL,  # noqa
            local: Optional[IsLocalRunnerConfig] = None,  # noqa
            prefect: Optional[IsPrefectEngineConfig] = None,  # noqa
            root_log: Optional[IsRootLogConfigEntryPublisher] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntimeObjects(IsDataPublisher, Protocol):
    """"""

    job_creator: IsJobConfigHolder
    local: IsEngine
    prefect: IsEngine
    registry: IsRunStateRegistry
    root_log: IsRootLogObjects

    def __init__(
            self,
            job_creator: Optional[IsJobConfigHolder] = None,  # noqa
            local: Optional[IsEngine] = None,  # noqa
            prefect: Optional[IsEngine] = None,  # noqa
            registry: Optional[IsRunStateRegistry] = None,  # noqa
            root_log: Optional[IsRootLogObjects] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntime(IsDataPublisher, Protocol):
    """"""
    config: IsRuntimeConfig
    objects: IsRuntimeObjects

    def __init__(
            self,
            config: Optional[IsRuntimeConfig] = None,  # noqa
            objects: Optional[IsRuntimeObjects] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...

    def reset_subscriptions(self):
        ...


class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    """"""
    ...


class IsJobConfig(IsJobConfigBase, Protocol):
    """"""
    ...


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


class IsRootLogObjects(Protocol):
    """"""
    formatter: Optional[logging.Formatter] = None
    stdout_handler: Optional[logging.StreamHandler] = None
    stderr_handler: Optional[logging.StreamHandler] = None
    file_handler: Optional[TimedRotatingFileHandler] = None

    def set_config(self, config: IsRootLogConfig) -> None:
        ...


class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    """"""
    use_cached_results: int = False


class IsRootLogConfigEntryPublisher(IsRootLogConfig, IsDataPublisher, Protocol):
    """"""
    ...
