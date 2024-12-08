import omnipy.util.pydantic as pyd

from omnipy.util.publisher import DataPublisher


@pyd.dataclass
class EngineConfig(DataPublisher):
    ...


@pyd.dataclass
class LocalRunnerConfig(EngineConfig):
    ...


@pyd.dataclass
class PrefectEngineConfig(EngineConfig):
    use_cached_results: bool = False
