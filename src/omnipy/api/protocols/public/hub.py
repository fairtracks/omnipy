import logging
from logging.handlers import RotatingFileHandler
from typing import Protocol, runtime_checkable

from omnipy.api.enums import EngineChoice
from omnipy.api.protocols.private.compute.job_creator import IsJobConfigHolder
from omnipy.api.protocols.private.data import IsDataClassCreator
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.private.util import IsDataPublisher
from omnipy.api.protocols.public.config import (IsDataConfig,
                                                IsJobConfig,
                                                IsLocalRunnerConfig,
                                                IsPrefectEngineConfig,
                                                IsRootLogConfig)
from omnipy.api.protocols.public.data import IsSerializerRegistry


@runtime_checkable
class IsRootLogObjects(Protocol):
    """"""
    formatter: logging.Formatter | None = None
    stdout_handler: logging.StreamHandler | None = None
    stderr_handler: logging.StreamHandler | None = None
    file_handler: RotatingFileHandler | None = None

    def set_config(self, config: IsRootLogConfig) -> None:
        ...

    @property
    def config(self) -> IsRootLogConfig:
        ...


@runtime_checkable
class IsRuntimeConfig(IsDataPublisher, Protocol):
    """"""
    job: IsJobConfig
    data: IsDataConfig
    engine: EngineChoice
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    root_log: IsRootLogConfig

    def reset_to_defaults(self) -> None:
        ...


@runtime_checkable
class IsRuntimeObjects(IsDataPublisher, Protocol):
    """"""

    job_creator: IsJobConfigHolder
    data_class_creator: IsDataClassCreator
    local: IsEngine
    prefect: IsEngine
    registry: IsRunStateRegistry
    serializers: IsSerializerRegistry
    root_log: IsRootLogObjects


@runtime_checkable
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
