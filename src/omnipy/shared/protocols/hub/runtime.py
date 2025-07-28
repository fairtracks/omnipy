import logging
from logging.handlers import RotatingFileHandler
from typing import Protocol, runtime_checkable

from omnipy.shared.protocols.compute.job_creator import IsJobConfigHolder
from omnipy.shared.protocols.config import (IsDataConfig,
                                            IsEngineConfig,
                                            IsJobConfig,
                                            IsRootLogConfig)
from omnipy.shared.protocols.data import IsDataClassCreator, IsReactiveObjects, IsSerializerRegistry
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
    data: IsDataConfig
    engine: IsEngineConfig
    job: IsJobConfig
    root_log: IsRootLogConfig

    def reset_to_defaults(self) -> None:
        ...


@runtime_checkable
class IsRuntimeObjects(IsDataPublisher, Protocol):
    """"""

    job_creator: IsJobConfigHolder
    data_class_creator: IsDataClassCreator
    reactive: IsReactiveObjects
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

    def reset_subscriptions(self):
        ...
