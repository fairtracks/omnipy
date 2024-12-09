from dataclasses import dataclass

from omnipy.util.publisher import DataPublisher


@dataclass
class EngineConfig(DataPublisher):
    ...


@dataclass
class LocalRunnerConfig(EngineConfig):
    ...


@dataclass
class PrefectEngineConfig(EngineConfig):
    use_cached_results: bool = False
