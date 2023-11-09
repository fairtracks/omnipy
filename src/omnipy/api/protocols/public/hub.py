from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Optional, Protocol

from omnipy.api.protocols.private.compute.job_creator import IsJobConfigHolder
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.config import IsRootLogConfig, IsRuntimeConfig


class IsRuntime(Protocol):
    """"""
    config: IsRuntimeConfig
    objects: IsRuntimeObjects

    def __init__(
            self,
            config: Optional[IsRuntimeConfig] = None,  # noqa
            objects: Optional[IsRuntimeObjects] = None,  # noqa
            *args: object,
            **kwargs: object) -> None:
        ...

    def reset_subscriptions(self):
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
            *args: object,
            **kwargs: object) -> None:
        ...


class IsRootLogObjects(Protocol):
    """"""
    formatter: Optional[logging.Formatter] = None
    stdout_handler: Optional[logging.StreamHandler] = None
    stderr_handler: Optional[logging.StreamHandler] = None
    file_handler: Optional[TimedRotatingFileHandler] = None

    def set_config(self, config: IsRootLogConfig) -> None:
        ...
