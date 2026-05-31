"""Configuration models for selecting and tuning job runner engines."""

from omnipy.config import ConfigBase
from omnipy.shared.enums.job import EngineChoice
from omnipy.shared.protocols.config import IsLocalRunnerConfig, IsPrefectEngineConfig
import omnipy.util.pydantic as pyd


class JobRunnerConfig(ConfigBase):
    """Base configuration shared by all job runner engines."""

    ...


class LocalRunnerConfig(JobRunnerConfig):
    """Configuration for the local in-process job runner."""

    ...


class PrefectEngineConfig(JobRunnerConfig):
    """Configuration for the Prefect-backed job runner."""

    use_cached_results: bool = False


class EngineConfig(ConfigBase):
    """Top-level engine selection and per-engine configuration."""

    choice: EngineChoice.Literals = EngineChoice.LOCAL
    local: IsLocalRunnerConfig = pyd.Field(default_factory=LocalRunnerConfig)
    prefect: IsPrefectEngineConfig = pyd.Field(default_factory=PrefectEngineConfig)
