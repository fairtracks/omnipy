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
        """{{ISENGINE_GET_CONFIG_CLS_SUMMARY}}

        {{ISENGINE_GET_CONFIG_CLS_DETAILS}}"""

    def set_config(self, config: IsJobRunnerConfig) -> None:
        """{{ISENGINE_SET_CONFIG_SUMMARY}}

        {{ISENGINE_SET_CONFIG_DETAILS}}"""
        self._config = config
        self._update_from_config()

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        """{{ISENGINE_SET_REGISTRY_SUMMARY}}

        {{ISENGINE_SET_REGISTRY_DETAILS}}"""
        self._registry = registry

    @property
    def config(self) -> IsJobRunnerConfig:
        """{{ISENGINE_CONFIG_SUMMARY}}

        {{ISENGINE_CONFIG_DETAILS}}"""
        return self._config

    @property
    def registry(self) -> IsRunStateRegistry | None:
        """{{ISENGINE_REGISTRY_SUMMARY}}

        {{ISENGINE_REGISTRY_DETAILS}}"""
        return self._registry
