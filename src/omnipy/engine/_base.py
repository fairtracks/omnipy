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
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISENGINE_GET_CONFIG_CLS_SUMMARY}}
        #
        # {{ISENGINE_GET_CONFIG_CLS_DETAILS}}
        """Return the config class associated with this engine type.

        Args:
            cls: Engine subclass whose configuration class is being requested.
        
        Returns:
            Type[IsJobRunnerConfig]: Configuration class used to instantiate engine settings.
"""

    def set_config(self, config: IsJobRunnerConfig) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISENGINE_SET_CONFIG_SUMMARY}}
        #
        # {{ISENGINE_SET_CONFIG_DETAILS}}
        """Replace the active config and refresh config-dependent state.

        Args:
            config: Runtime configuration object for the engine.
"""
        self._config = config
        self._update_from_config()

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISENGINE_SET_REGISTRY_SUMMARY}}
        #
        # {{ISENGINE_SET_REGISTRY_DETAILS}}
        """Attach or clear the run-state registry used for job state reporting.

        Args:
            registry: Registry implementation, or ``None`` to disable state reporting.
"""
        self._registry = registry

    @property
    def config(self) -> IsJobRunnerConfig:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISENGINE_CONFIG_SUMMARY}}
        #
        # {{ISENGINE_CONFIG_DETAILS}}
        """Return the currently active engine configuration.

        Returns:
            IsJobRunnerConfig: Active configuration object controlling engine behavior.
"""
        return self._config

    @property
    def registry(self) -> IsRunStateRegistry | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISENGINE_REGISTRY_SUMMARY}}
        #
        # {{ISENGINE_REGISTRY_DETAILS}}
        """Return the registry currently used for run-state reporting.

        Returns:
            IsRunStateRegistry | None: Registry receiving job-state updates, or ``None`` when
                state reporting is disabled.
"""
        return self._registry
