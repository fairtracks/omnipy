from dataclasses import dataclass


@dataclass
class EngineConfig:
    ...


@dataclass
class LocalRunnerConfig(EngineConfig):
    ...


@dataclass
class PrefectEngineConfig(EngineConfig):
    use_cached_results: int = False
