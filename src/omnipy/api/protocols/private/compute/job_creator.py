from datetime import datetime
from typing import Protocol, runtime_checkable

from omnipy.api.protocols.private.compute.mixins import IsNestedContext
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.public.config import IsJobConfig


@runtime_checkable
class IsJobConfigHolder(Protocol):
    """"""
    @property
    def config(self) -> IsJobConfig:
        ...

    @property
    def engine(self) -> IsEngine | None:
        ...

    def set_config(self, config: IsJobConfig) -> None:
        ...

    def set_engine(self, engine: IsEngine) -> None:
        ...


@runtime_checkable
class IsJobCreator(IsNestedContext, IsJobConfigHolder, Protocol):
    """"""
    @property
    def nested_context_level(self) -> int:
        ...

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> datetime | None:
        ...
