"""Mock helpers for hub runtime tests."""

from abc import ABC, abstractmethod
from typing import cast, Generic, Protocol

from typing_extensions import TypeVar

from omnipy.config import ConfigBase
from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry

EngineConfigT = TypeVar('EngineConfigT', bound=IsJobRunnerConfig)


class MockEngine(ABC, Generic[EngineConfigT]):
    """Define mock Engine."""
    def __init__(self) -> None:
        config_cls = self.get_config_cls()
        self._config: IsJobRunnerConfig = config_cls()
        self.registry: IsRunStateRegistry | None = None

    @classmethod
    @abstractmethod
    def get_config_cls(cls) -> type[EngineConfigT]:
        ...

    def set_config(self, config: IsJobRunnerConfig) -> None:
        self._config = config

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        self.registry = registry


class MockLocalRunnerConfig(ConfigBase):
    """Define mock Local Runner Config."""
    backend_verbose: bool = True


class IsMockLocalRunnerConfig(IsJobRunnerConfig, Protocol):
    """Define IsMockLocalRunnerConfig."""
    backend_verbose: bool


class MockLocalRunner(MockEngine[IsMockLocalRunnerConfig]):
    """Define mock Local Runner."""
    @classmethod
    def get_config_cls(cls) -> type[IsMockLocalRunnerConfig]:
        return MockLocalRunnerConfig

    @property
    def config(self) -> IsMockLocalRunnerConfig:
        return cast(IsMockLocalRunnerConfig, self._config)


class MockPrefectEngineConfig(ConfigBase):
    """Define mock Prefect Engine Config."""
    server_url: str = ''
    use_cached_results: bool = False


class IsMockPrefectEngineConfig(IsJobRunnerConfig, Protocol):
    """Define IsMockPrefectEngineConfig."""
    server_url: str = ''
    use_cached_results: bool


class MockPrefectEngine(MockEngine[IsMockPrefectEngineConfig]):
    """Define mock Prefect Engine."""
    @classmethod
    def get_config_cls(cls) -> type[IsMockPrefectEngineConfig]:
        return MockPrefectEngineConfig

    @property
    def config(self) -> IsMockPrefectEngineConfig:
        return cast(IsMockPrefectEngineConfig, self._config)
