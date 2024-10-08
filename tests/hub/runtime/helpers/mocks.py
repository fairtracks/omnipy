from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Type

from omnipy.api.enums import RunState
from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.compute import IsTask
from omnipy.api.protocols.public.config import (IsEngineConfig,
                                                IsLocalRunnerConfig,
                                                IsPrefectEngineConfig,
                                                IsRootLogConfig)
from omnipy.api.protocols.public.engine import IsTaskRunnerEngine


class IsMockJobConfig(Protocol):
    persist_outputs: bool = True
    restore_outputs: bool = False


@dataclass
class MockJobConfig:
    persist_outputs: bool = True
    restore_outputs: bool = False


class MockJobCreator:
    def __init__(self) -> None:
        self.engine: IsTaskRunnerEngine | None = None
        self.config: IsMockJobConfig = MockJobConfig()

    def set_engine(self, engine: IsTaskRunnerEngine) -> None:
        self.engine = engine

    def set_config(self, config: IsMockJobConfig) -> None:
        self.config = config


class MockJobCreator2(MockJobCreator):
    ...


class IsMockDataConfig(Protocol):
    interactive_mode: bool = True


@dataclass
class MockDataConfig:
    interactive_mode: bool = True


class MockDataClassCreator:
    def __init__(self) -> None:
        self.config: IsMockDataConfig = MockDataConfig()

    def set_config(self, config: IsMockDataConfig) -> None:
        self.config = config


class MockDataClassCreator2(MockDataClassCreator):
    ...


class MockEngine(ABC):
    def __init__(self) -> None:
        config_cls = self.get_config_cls()
        self._config: IsEngineConfig = config_cls()
        self.registry: IsRunStateRegistry | None = None

    @classmethod
    @abstractmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        ...

    def set_config(self, config: IsEngineConfig) -> None:
        self._config = config

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        self.registry = registry


@dataclass
class MockLocalRunnerConfig:
    backend_verbose: bool = True


class MockLocalRunnerConfig2(MockLocalRunnerConfig):
    ...


class MockLocalRunner(MockEngine):
    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        return MockLocalRunnerConfig

    @property
    def config(self) -> IsLocalRunnerConfig:
        return self._config


class MockLocalRunner2(MockLocalRunner):
    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        return MockLocalRunnerConfig2


@dataclass
class MockPrefectEngineConfig:
    server_url: str = ''


class MockPrefectEngineConfig2(MockPrefectEngineConfig):
    ...


class MockPrefectEngine(MockEngine):
    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        return MockPrefectEngineConfig

    @property
    def config(self) -> IsPrefectEngineConfig:
        return self._config


class MockPrefectEngine2(MockPrefectEngine):
    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        return MockPrefectEngineConfig2


class MockRootLogObjects:
    def __init__(self):
        self.config: IsRootLogConfig | None = None

    def set_config(self, config: IsRootLogConfig):
        self.config = config


class MockRootLogObjects2(MockRootLogObjects):
    ...


@dataclass
class MockRootLogConfig:
    log_to_stderr: bool = True


class MockRunStateRegistry:
    def get_task_state(self, task: IsTask) -> RunState:
        ...

    def get_task_state_datetime(self, task: IsTask, state: RunState) -> datetime:
        ...

    def all_tasks(self, state: RunState | None = None) -> tuple[IsTask, ...]:  # noqa
        ...

    def set_task_state(self, task: IsTask, state: RunState) -> None:
        ...


class MockRunStateRegistry2(MockRunStateRegistry):
    ...
