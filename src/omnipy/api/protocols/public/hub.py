import logging
from logging.handlers import RotatingFileHandler
from typing import Protocol

from omnipy.api.enums import EngineChoice
from omnipy.api.protocols.private.compute.job_creator import IsJobConfigHolder
from omnipy.api.protocols.private.data import IsDataClassCreator
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.config import (IsDataConfig,
                                                IsJobConfig,
                                                IsLocalRunnerConfig,
                                                IsPrefectEngineConfig,
                                                IsRootLogConfig)
from omnipy.api.protocols.public.data import IsSerializerRegistry


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


class IsRuntimeConfig(Protocol):
    """"""
    job: IsJobConfig
    data: IsDataConfig
    engine: EngineChoice
    local: IsLocalRunnerConfig
    prefect: IsPrefectEngineConfig
    root_log: IsRootLogConfig

    def __init__(self,
                 job: IsJobConfig,
                 data: IsDataConfig,
                 engine: EngineChoice,
                 local: IsLocalRunnerConfig,
                 prefect: IsPrefectEngineConfig,
                 root_log: IsRootLogConfig) -> None:
        ...

    def reset_to_defaults(self) -> None:
        ...


class IsRuntimeObjects(Protocol):
    """"""

    job_creator: IsJobConfigHolder
    data_class_creator: IsDataClassCreator
    local: IsEngine
    prefect: IsEngine
    registry: IsRunStateRegistry
    serializers: IsSerializerRegistry
    root_log: IsRootLogObjects

    def __init__(self,
                 job_creator: IsJobConfigHolder,
                 data_class_creator: IsDataClassCreator,
                 local: IsEngine,
                 prefect: IsEngine,
                 registry: IsRunStateRegistry,
                 serializers: IsSerializerRegistry,
                 root_log: IsRootLogObjects) -> None:
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
