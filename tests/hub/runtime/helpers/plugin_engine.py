"""Mock plugin engine, loaded through a fake entry point in the plugin engine tests.

Kept in its own module so that tests can check that it is only imported on first use.
"""

from typing import cast, Protocol

from omnipy.config import ConfigBase
from omnipy.shared.protocols.config import IsJobRunnerConfig

from .mocks import MockEngine

PLUGIN_ENGINE_MODULE = __name__
PLUGIN_ENGINE_IMPORT_PATH = f'{__name__}:MockPluginEngine'
OTHER_PLUGIN_ENGINE_IMPORT_PATH = f'{__name__}:OtherMockPluginEngine'


class MockPluginEngineConfig(ConfigBase):
    """Config of the mock plugin engine."""

    server_url: str = ''


class IsMockPluginEngineConfig(IsJobRunnerConfig, Protocol):
    """Protocol for the config of the mock plugin engine."""

    server_url: str


class MockPluginEngine(MockEngine[IsMockPluginEngineConfig]):
    """Mock plugin engine that records the configs it receives."""

    def __init__(self) -> None:
        self.received_configs: list[IsJobRunnerConfig] = []
        super().__init__()

    @classmethod
    def get_config_cls(cls) -> type[IsMockPluginEngineConfig]:
        return MockPluginEngineConfig

    def set_config(self, config: IsJobRunnerConfig) -> None:
        self.received_configs.append(config)
        super().set_config(config)

    @property
    def config(self) -> IsMockPluginEngineConfig:
        return cast(IsMockPluginEngineConfig, self._config)


class OtherMockPluginEngineConfig(ConfigBase):
    """Config of a second mock plugin engine, with a different config class."""

    queue: str = 'default'


class IsOtherMockPluginEngineConfig(IsJobRunnerConfig, Protocol):
    """Protocol for the config of the second mock plugin engine."""

    queue: str


class OtherMockPluginEngine(MockEngine[IsOtherMockPluginEngineConfig]):
    """Second mock plugin engine, used for replacing engine objects."""

    @classmethod
    def get_config_cls(cls) -> type[IsOtherMockPluginEngineConfig]:
        return OtherMockPluginEngineConfig

    @property
    def config(self) -> IsOtherMockPluginEngineConfig:
        return cast(IsOtherMockPluginEngineConfig, self._config)
