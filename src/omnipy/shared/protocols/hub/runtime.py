import logging
from logging.handlers import RotatingFileHandler
from typing import Protocol, runtime_checkable

from omnipy.shared.enums import EngineChoice
from omnipy.shared.protocols.compute.job_creator import IsJobConfigHolder
from omnipy.shared.protocols.config import (IsDataConfig,
                                            IsJobConfig,
                                            IsLocalRunnerConfig,
                                            IsPrefectEngineConfig,
                                            IsRootLogConfig)
from omnipy.shared.protocols.data import IsDataClassCreator, IsSerializerRegistry
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.shared.protocols.util import IsDataPublisher


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
