from typing import Type

from unifair.config.engine import LocalRunnerConfig
from unifair.engine.base import Engine
from unifair.engine.protocols import IsLocalRunnerConfig


class LocalRunner(Engine):
    def _init_engine(self) -> None:
        ...

    def _update_from_config(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsLocalRunnerConfig]:
        return LocalRunnerConfig
