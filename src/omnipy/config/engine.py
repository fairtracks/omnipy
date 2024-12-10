from omnipy.config import ConfigBase


class EngineConfig(ConfigBase):
    ...


class LocalRunnerConfig(EngineConfig):
    ...


class PrefectEngineConfig(EngineConfig):
    use_cached_results: bool = False
