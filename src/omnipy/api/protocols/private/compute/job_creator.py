from __future__ import annotations

from datetime import datetime
from typing import Optional, Protocol

from omnipy.api.protocols.private.compute.mixins import IsNestedContext
from omnipy.api.protocols.private.hub import IsJobConfigHolder


class IsJobCreator(IsNestedContext, IsJobConfigHolder, Protocol):
    """"""
    @property
    def nested_context_level(self) -> int:
        ...

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> Optional[datetime]:
        ...
