"""Configuration models for selecting and tuning job runner engines."""

from omnipy.config import ConfigBase
from omnipy.engine._engine_attrs import EngineAttrsMixin
from omnipy.engine.registry import engine_registry
from omnipy.shared.enums.job import EngineChoice
from omnipy.shared.protocols.config import IsLocalRunnerConfig, IsPrefectEngineConfig
from omnipy.shared.protocols.hub.runtime import IsRuntime
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


class EngineConfig(EngineAttrsMixin, ConfigBase):
    """Top-level engine selection and per-engine configuration.

    The built-in engines have declared fields. The config of a plugin engine is an extra
    attribute named after the engine, such as ``tes``, added when the runtime loads the engine.
    """

    _back: IsRuntime | None = pyd.PrivateAttr(default=None)

    choice: str = EngineChoice.LOCAL
    local: IsLocalRunnerConfig = pyd.Field(default_factory=LocalRunnerConfig)
    prefect: IsPrefectEngineConfig = pyd.Field(default_factory=PrefectEngineConfig)

    @pyd.validator('choice')
    def _check_registered_engine(cls, choice: str) -> str:
        engine_registry.check_name(choice)
        return choice
