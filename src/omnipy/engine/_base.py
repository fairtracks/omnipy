from abc import ABC, abstractmethod
from typing import Type

from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry


class Engine(ABC):
    """Base class for engine implementations"""
    def __init__(self) -> None:
        config_cls = self.get_config_cls()
        self._config: IsJobRunnerConfig = config_cls()
        self._registry: IsRunStateRegistry | None = None

        self._init_engine()

    @abstractmethod
    def _init_engine(self) -> None:
        """
        Private method for initialization of an Engine subclass. Removes the need to override the
        __init__() method in the subclass, reducing class coupling and possible error sources.
        Must be implemented by all subclasses of Engine, but can remain empty.
        """

    @abstractmethod
    def _update_from_config(self) -> None:
        """
        Private method to signal to subclass to update any internal state that depends on config
        values.
        Must be implemented by all subclasses of Engine, but can remain empty.
        """

    @classmethod
    @abstractmethod
    def get_config_cls(cls) -> Type[IsJobRunnerConfig]:
        """
        Specification of config class mapped to an Engine subclass. Must be implemented by all
        subclasses of Engine. If no configuration is needed, then the EngineConfig class should be
        returned.
        :return: Class implementing the IsEngineConfig protocol
        """

    def set_config(self, config: IsJobRunnerConfig) -> None:
        self._config = config
        self._update_from_config()

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        self._registry = registry

    @property
    def config(self) -> IsJobRunnerConfig:
        return self._config

    @property
    def registry(self) -> IsRunStateRegistry | None:
        return self._registry
