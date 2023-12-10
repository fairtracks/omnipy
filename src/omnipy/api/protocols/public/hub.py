import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Protocol

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
    formatter: logging.Formatter | None = None
    stdout_handler: logging.StreamHandler | None = None
    stderr_handler: logging.StreamHandler | None = None
    file_handler: TimedRotatingFileHandler | None = None

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
            job: IsJobConfig | None = None,  # noqa
            engine: EngineChoice = EngineChoice.LOCAL,  # noqa
            local: IsLocalRunnerConfig | None = None,  # noqa
            prefect: IsPrefectEngineConfig | None = None,  # noqa
            root_log: 'IsRootLogConfigEntryPublisher | None' = None,  # noqa
            *args: object,
            **kwargs: object) -> None:
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
            job_creator: IsJobConfigHolder | None = None,  # noqa
            local: IsEngine | None = None,  # noqa
            prefect: IsEngine | None = None,  # noqa
            registry: IsRunStateRegistry | None = None,  # noqa
            root_log: IsRootLogObjects | None = None,  # noqa
            *args: object,
            **kwargs: object) -> None:
        ...


class IsRuntime(Protocol):
    """"""
    config: IsRuntimeConfig
    objects: IsRuntimeObjects

    def __init__(
            self,
            config: IsRuntimeConfig | None = None,  # noqa
            objects: IsRuntimeObjects | None = None,  # noqa
            *args: object,
            **kwargs: object) -> None:
        ...

    def reset_subscriptions(self):
        ...
