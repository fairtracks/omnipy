from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Optional, Protocol

from omnipy.api.enums import EngineChoice
from omnipy.api.protocols.private.compute.job_creator import IsJobConfigHolder
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.config import (IsJobConfig,
                                                IsLocalRunnerConfig,
                                                IsPrefectEngineConfig,
                                                IsRootLogConfig)


class IsRootLogObjects(Protocol):
    """"""
    formatter: Optional[logging.Formatter] = None
    stdout_handler: Optional[logging.StreamHandler] = None
    stderr_handler: Optional[logging.StreamHandler] = None
    file_handler: Optional[TimedRotatingFileHandler] = None

    def set_config(self, config: IsRootLogConfig) -> None:
        ...


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
            root_log: Optional[IsRootLogConfigEntryPublisher] = None,  # noqa
            *args: Any,
            **kwargs: Any) -> None:
        ...


class IsRuntimeObjects(Protocol):
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


class IsRuntime(Protocol):
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
