"""Base engine contracts for runtime execution backends.

Args:
    None.

Returns:
    None.

Raises:
    None.

Example:
    >>> from omnipy.engine._base import Engine
    >>> isinstance(Engine.__name__, str)
    True
"""

from abc import ABC, abstractmethod
from typing import Type

from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry


class Engine(ABC):
    """Base class for runtime engine implementations.

    Args:
        None.

    Returns:
        None.

    Raises:
        TypeError: If the configured engine config class cannot be instantiated.

    Example:
        >>> from omnipy.engine._base import Engine
        >>> issubclass(Engine, ABC)
        True
    """

    def __init__(self) -> None:
        """Initialize engine config, registry holder, and subclass state.

        Args:
            None.

        Returns:
            None.

        Raises:
            Exception: Propagates exceptions raised by config creation or subclass initialization.

        Example:
            >>> # Engine subclasses call this automatically.
            >>> isinstance(Engine.__init__, object)
            True
        """
        config_cls = self.get_config_cls()
        self._config: IsJobRunnerConfig = config_cls()
        self._registry: IsRunStateRegistry | None = None

        self._init_engine()

    @abstractmethod
    def _init_engine(self) -> None:
        """Initialize subclass-specific engine state.

        Args:
            None.

        Returns:
            None.

        Raises:
            NotImplementedError: Raised by subclasses that do not implement this hook.

        Example:
            >>> # A concrete engine may initialize clients or caches here.
            >>> True
            True
        """

    @abstractmethod
    def _update_from_config(self) -> None:
        """Update internal state after config replacement.

        Args:
            None.

        Returns:
            None.

        Raises:
            NotImplementedError: Raised by subclasses that do not implement this hook.

        Example:
            >>> # A concrete engine may recalculate runtime options here.
            >>> True
            True
        """

    @classmethod
    @abstractmethod
    def get_config_cls(cls) -> Type[IsJobRunnerConfig]:
        """Return the config class associated with the engine type.

        Args:
            cls: Engine subclass that provides the configuration mapping.

        Returns:
            Type[IsJobRunnerConfig]: Configuration class used to create engine config instances.

        Raises:
            NotImplementedError: Raised by subclasses that do not define a config class.

        Example:
            >>> # Concrete engines return their config type.
            >>> hasattr(Engine, 'get_config_cls')
            True
        """

    def set_config(self, config: IsJobRunnerConfig) -> None:
        """Replace the active config and refresh config-dependent state.

        Args:
            config: Runtime configuration object for the engine.

        Returns:
            None.

        Raises:
            Exception: Propagates subclass errors from ``_update_from_config``.

        Example:
            >>> # engine.set_config(new_config)
            >>> True
            True
        """
        self._config = config
        self._update_from_config()

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        """Attach or clear the run-state registry used for job state reporting.

        Args:
            registry: Registry implementation, or ``None`` to disable state reporting.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> # engine.set_registry(runtime_registry)
            >>> True
            True
        """
        self._registry = registry

    @property
    def config(self) -> IsJobRunnerConfig:
        """Return the currently active engine configuration.

        Args:
            None.

        Returns:
            IsJobRunnerConfig: Current configuration bound to this engine instance.

        Raises:
            None.

        Example:
            >>> # current = engine.config
            >>> True
            True
        """
        return self._config

    @property
    def registry(self) -> IsRunStateRegistry | None:
        """Return the registry currently used for run-state reporting.

        Args:
            None.

        Returns:
            IsRunStateRegistry | None: Active registry, or ``None`` when disabled.

        Raises:
            None.

        Example:
            >>> # active_registry = engine.registry
            >>> True
            True
        """
        return self._registry
