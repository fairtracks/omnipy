from abc import ABC, abstractmethod
from typing import cast, Generic, Protocol

from typing_extensions import TypeVar

from omnipy.config import ConfigBase
from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry

EngineConfigT = TypeVar('EngineConfigT', bound=IsJobRunnerConfig)


class MockEngine(ABC, Generic[EngineConfigT]):
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
    backend_verbose: bool = True


class IsMockLocalRunnerConfig(IsJobRunnerConfig, Protocol):
    backend_verbose: bool


class MockLocalRunner(MockEngine[IsMockLocalRunnerConfig]):
    @classmethod
    def get_config_cls(cls) -> type[IsMockLocalRunnerConfig]:
        return MockLocalRunnerConfig

    @property
    def config(self) -> IsMockLocalRunnerConfig:
        return cast(IsMockLocalRunnerConfig, self._config)


class MockPrefectEngineConfig(ConfigBase):
    server_url: str = ''
    use_cached_results: bool = False


class IsMockPrefectEngineConfig(IsJobRunnerConfig, Protocol):
    server_url: str = ''
    use_cached_results: bool


class MockPrefectEngine(MockEngine[IsMockPrefectEngineConfig]):
    @classmethod
    def get_config_cls(cls) -> type[IsMockPrefectEngineConfig]:
        return MockPrefectEngineConfig

    @property
    def config(self) -> IsMockPrefectEngineConfig:
        return cast(IsMockPrefectEngineConfig, self._config)
