from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from unifair.engine.protocols import EngineConfigProtocol, RuntimeConfigProtocol


@dataclass
class EngineConfig:
    ...


class Engine(ABC):
    def __init__(self, config: Optional[EngineConfigProtocol] = None):
        if config is None:
            config = self._get_default_config()
        self._config: EngineConfigProtocol = config
        self._runtime: Optional[RuntimeConfigProtocol] = None
        self._init_engine()

    @abstractmethod
    def _init_engine(self) -> None:
        ...

    def _get_default_config(self) -> EngineConfigProtocol:
        return EngineConfig()

    def set_runtime(self, runtime: RuntimeConfigProtocol) -> None:
        self._runtime = runtime
