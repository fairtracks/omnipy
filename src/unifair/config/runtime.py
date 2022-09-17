from dataclasses import dataclass
from typing import Optional

from unifair.engine.protocols import EngineProtocol, RunStateRegistryProtocol


@dataclass
class RuntimeConfig:
    engine: EngineProtocol
    registry: Optional[RunStateRegistryProtocol] = None
    verbose: bool = False

    def __post_init__(self):
        self.engine.set_runtime(self)
        if self.registry is not None:
            self.registry.set_runtime(self)
