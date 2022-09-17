from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from unifair.engine.protocols import EngineConfigProtocol, RunStatsProtocol


@dataclass
class EngineConfig:
    ...


class Engine(ABC):
    def __init__(self,
                 config: Optional[EngineConfigProtocol] = None,
                 run_stats: Optional[RunStatsProtocol] = None):
        if config is None:
            config = self._get_default_config()
        self._config: EngineConfigProtocol = config
        self._run_stats: RunStatsProtocol = run_stats
        self._init_engine()

    @abstractmethod
    def _init_engine(self) -> None:
        ...

    def _get_default_config(self) -> EngineConfigProtocol:
        return EngineConfig()
