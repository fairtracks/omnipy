from omnipy.config import ConfigBase
from omnipy.shared.enums.job import EngineChoice
from omnipy.shared.protocols.config import IsLocalRunnerConfig, IsPrefectEngineConfig
import omnipy.util._pydantic as pyd


class JobRunnerConfig(ConfigBase):
    ...


class LocalRunnerConfig(JobRunnerConfig):
    ...


class PrefectEngineConfig(JobRunnerConfig):
    use_cached_results: bool = False


class EngineConfig(ConfigBase):
    choice: EngineChoice.Literals = EngineChoice.LOCAL
    local: IsLocalRunnerConfig = pyd.Field(default_factory=LocalRunnerConfig)
    prefect: IsPrefectEngineConfig = pyd.Field(default_factory=PrefectEngineConfig)
