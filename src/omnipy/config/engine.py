from omnipy.util.publisher import DataPublisher


class EngineConfig(DataPublisher):
    ...


class LocalRunnerConfig(EngineConfig):
    ...


class PrefectEngineConfig(EngineConfig):
    use_cached_results: bool = False
