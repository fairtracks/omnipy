from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class EngineConfig:
    ...


class Engine(ABC):
    def __init__(self, config: Optional[EngineConfig] = None):
        if config is None:
            config = EngineConfig()
        self._config: EngineConfig = config
        self._init_engine()

    @abstractmethod
    def _init_engine(self) -> None:
        ...
