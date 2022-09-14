from typing import Callable

from unifair.engine.base import Engine


class LocalRunner(Engine):
    def _init_engine(self) -> None:
        ...
