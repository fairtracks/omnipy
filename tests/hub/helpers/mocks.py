from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol, Tuple, Type

from omnipy.api.enums import RunState
from omnipy.api.protocols.private import IsEngineConfig, IsRunStateRegistry
from omnipy.api.protocols.public.engine import IsTaskRunnerEngine
from omnipy.api.protocols.public.job import IsTask
from omnipy.api.protocols.public.runtime import (IsLocalRunnerConfig,
                                                 IsPrefectEngineConfig,
                                                 IsRootLogConfig)


class MockIsJobConfig(Protocol):
    persist_outputs: bool = True
    restore_outputs: bool = False


@dataclass
class MockJobConfig:
    persist_outputs: bool = True
    restore_outputs: bool = False


class MockJobCreator:
    def __init__(self) -> None:
        self.engine: Optional[IsTaskRunnerEngine] = None
        self.config: MockIsJobConfig = MockJobConfig()

    def set_engine(self, engine: IsTaskRunnerEngine) -> None:
        self.engine = engine

    def set_config(self, config: MockIsJobConfig) -> None:
        self.config = config


class MockJobCreator2(MockJobCreator):
    ...


class MockEngine(ABC):
    def __init__(self) -> None:
        config_cls = self.get_config_cls()
        self._config: IsEngineConfig = config_cls()
        self.registry: Optional[IsRunStateRegistry] = None

    @classmethod
    @abstractmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        ...

    def set_config(self, config: IsEngineConfig) -> None:
        self._config = config

    def set_registry(self, registry: Optional[IsRunStateRegistry]) -> None:
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
        self.config: Optional[IsRootLogConfig] = None

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

    def all_tasks(self, state: Optional[RunState] = None) -> Tuple[IsTask, ...]:  # noqa
        ...

    def set_task_state(self, task: IsTask, state: RunState) -> None:
        ...


class MockRunStateRegistry2(MockRunStateRegistry):
    ...
