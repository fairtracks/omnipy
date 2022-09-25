from __future__ import annotations

from typing import Optional

from unifair.engine.protocols import IsEngine


class JobCreator:
    def __init__(self):
        self._engine: Optional[IsEngine] = None

    def set_engine(self, engine: IsEngine) -> None:
        self._engine = engine

    @property
    def engine(self):
        return self._engine
