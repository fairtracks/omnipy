from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from unifair.engine.protocols import EngineConfigProtocol, RunStateRegistryProtocol


@dataclass
class EngineConfig:
    ...


class Engine(ABC):
    def __init__(self,
                 config: Optional[EngineConfigProtocol] = None,
                 registry: Optional[RunStateRegistryProtocol] = None):
        if config is None:
            config = self._get_default_config()
        self._config: EngineConfigProtocol = config
        self._registry: RunStateRegistryProtocol = registry
        self._init_engine()

    @abstractmethod
    def _init_engine(self) -> None:
        ...

    def _get_default_config(self) -> EngineConfigProtocol:
        return EngineConfig()
