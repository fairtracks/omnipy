from __future__ import annotations

from datetime import datetime
from typing import Optional, Protocol

from omnipy.api.protocols.private.compute.mixins import IsNestedContext
from omnipy.api.protocols.private.engine import IsEngine
from omnipy.api.protocols.public.config import IsJobConfig


class IsJobConfigHolder(Protocol):
    """"""
    @property
    def config(self) -> Optional[IsJobConfig]:
        ...

    @property
    def engine(self) -> Optional[IsEngine]:
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
    def time_of_cur_toplevel_nested_context_run(self) -> Optional[datetime]:
        ...
