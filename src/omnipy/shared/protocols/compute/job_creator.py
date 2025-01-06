from datetime import datetime
from typing import Protocol, runtime_checkable

from omnipy.shared.protocols.compute.mixins import IsNestedContext
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.engine.base import IsEngine


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
