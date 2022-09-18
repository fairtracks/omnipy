from typing import Type

from unifair.config.engine import PrefectEngineConfig
from unifair.engine.base import Engine
from unifair.engine.protocols import IsPrefectEngineConfig


class PrefectEngine(Engine):
    def _init_engine(self) -> None:
        ...

    def _update_from_config(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsPrefectEngineConfig]:
        return PrefectEngineConfig
