"""Base engine contracts for runtime execution backends."""

from abc import ABC, abstractmethod
from typing import Type

from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry


class Engine(ABC):
    """Base class for runtime engine implementations.
    """

    def __init__(self) -> None:
        """Initialize engine config, registry holder, and subclass state."""
        config_cls = self.get_config_cls()
        self._config: IsJobRunnerConfig = config_cls()
        self._registry: IsRunStateRegistry | None = None

        self._init_engine()

    @abstractmethod
    def _init_engine(self) -> None:
        """Initialize subclass-specific engine state."""

    @abstractmethod
    def _update_from_config(self) -> None:
        """Update internal state after config replacement."""

    @classmethod
    @abstractmethod
    def get_config_cls(cls) -> Type[IsJobRunnerConfig]:
        """Return the config class associated with the engine type.

        Args:
            cls: Engine subclass that provides the configuration mapping.

        Returns:
            Type[IsJobRunnerConfig]: Configuration class used to create engine config instances.
        """

    def set_config(self, config: IsJobRunnerConfig) -> None:
        """Replace the active config and refresh config-dependent state.

        Args:
            config: Runtime configuration object for the engine.
        """
        self._config = config
        self._update_from_config()

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        """Attach or clear the run-state registry used for job state reporting.

        Args:
            registry: Registry implementation, or ``None`` to disable state reporting.
        """
        self._registry = registry

    @property
    def config(self) -> IsJobRunnerConfig:
        """Return the currently active engine configuration.
        """
        return self._config

    @property
    def registry(self) -> IsRunStateRegistry | None:
        """Return the registry currently used for run-state reporting.
        """
        return self._registry
