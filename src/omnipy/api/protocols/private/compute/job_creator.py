from datetime import datetime
from typing import Protocol

from omnipy.api.protocols.private.compute.mixins import IsNestedContext
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.public.config import IsJobConfig


class IsJobConfigHolder(Protocol):
    """"""
    @property
    def config(self) -> IsJobConfig | None:
        ...

    @property
    def engine(self) -> IsEngine | None:
        ...

    def set_config(self, config: IsJobConfig) -> None:
        ...

    def set_engine(self, engine: IsEngine) -> None:
        ...


class IsJobCreator(IsNestedContext, IsJobConfigHolder, Protocol):
    """"""
    @property
    def nested_context_level(self) -> int:
        ...

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> datetime | None:
        ...
