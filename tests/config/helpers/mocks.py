from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, ClassVar, Optional, Tuple, Type

from unifair.config.publisher import ConfigPublisher
from unifair.engine.constants import RunState
from unifair.engine.protocols import (IsEngine,
                                      IsEngineConfig,
                                      IsLocalRunnerConfig,
                                      IsPrefectEngineConfig,
                                      IsRunStateRegistry,
                                      IsRunStateRegistryConfig,
                                      IsTask)


class MockFoo:
    ...


@dataclass
class MockConfigPublisher(ConfigPublisher):
    foo: Optional[MockFoo] = None
    text: str = 'bar'
    number: int = 42


class MockSubscriberCls:
    def __init__(self):
        self.foo: Optional[MockFoo] = None
        self.text: str = ''

    def set_foo(self, foo: Optional[MockFoo]) -> None:
        self.foo = foo

    def set_text(self, text: str) -> None:
        self.text = text


class MockTaskTemplate:
    name: str
    engine: ClassVar[Optional[IsEngine]] = None

    @classmethod
    def set_engine(cls, engine: IsEngine) -> None:
        cls.engine = engine

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def _call_func(self, *args: Any, **kwargs: Any) -> Any:
        ...

    def has_coroutine_task_func(self) -> bool:
        ...

    def apply(self) -> IsTask:
        ...


class MockTaskTemplate2(MockTaskTemplate):
    ...


class MockEngine(ABC):
    def __init__(self) -> None:
        config_cls = self.get_config_cls()
        self._config: IsEngineConfig = config_cls()
        self._registry: Optional[IsRunStateRegistry] = None

    @classmethod
    @abstractmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        ...

    def set_config(self, config: IsEngineConfig) -> None:
        self._config = config

    def set_registry(self, registry: Optional[IsRunStateRegistry]) -> None:
        self._registry = registry

    @property
    def registry(self) -> Optional[IsRunStateRegistry]:
        return self._registry


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


@dataclass
class MockRunStateRegistryConfig:
    verbose: bool = True


class MockRunStateRegistry:
    def __init__(self) -> None:
        self.logger: Optional[logging.Logger] = None
        self.config: IsRunStateRegistryConfig = MockRunStateRegistryConfig()

    def get_task_state(self, task: IsTask) -> RunState:
        ...

    def get_task_state_datetime(self, task: IsTask, state: RunState) -> datetime:
        ...

    def all_tasks(self, state: Optional[RunState] = None) -> Tuple[IsTask, ...]:  # noqa
        ...

    def set_task_state(self, task: IsTask, state: RunState) -> None:
        ...

    def set_logger(self, logger: Optional[logging.Logger]) -> None:
        self.logger = logger

    def set_config(self, config: IsRunStateRegistryConfig) -> None:
        self.config = config


class MockRunStateRegistry2(MockRunStateRegistry):
    ...
