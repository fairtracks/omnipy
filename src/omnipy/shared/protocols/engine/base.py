"""Base protocols for Omnipy engine implementations."""

import os
from textwrap import dedent
from typing import Protocol, runtime_checkable, Type

from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.util.helpers import is_package_editable

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISENGINE_GET_CONFIG_CLS_SUMMARY'] = (
        'Return the config class associated with this engine type.')
    os.environ['OMNIPY_MACRO_ISENGINE_GET_CONFIG_CLS_DETAILS'] = dedent("""\
        Args:
            cls: Engine subclass whose configuration class is being requested.

        Returns:
            Type[IsJobRunnerConfig]: Configuration class used to instantiate engine settings.
    """)

    os.environ['OMNIPY_MACRO_ISENGINE_SET_CONFIG_SUMMARY'] = (
        'Replace the active config and refresh config-dependent state.')
    os.environ['OMNIPY_MACRO_ISENGINE_SET_CONFIG_DETAILS'] = dedent("""\
        Args:
            config: Runtime configuration object for the engine.
    """)

    os.environ['OMNIPY_MACRO_ISENGINE_SET_REGISTRY_SUMMARY'] = (
        'Attach or clear the run-state registry used for job state reporting.')
    os.environ['OMNIPY_MACRO_ISENGINE_SET_REGISTRY_DETAILS'] = dedent("""\
        Args:
            registry: Registry implementation, or ``None`` to disable state reporting.
    """)

    os.environ['OMNIPY_MACRO_ISENGINE_CONFIG_SUMMARY'] = (
        'Return the currently active engine configuration.')
    os.environ['OMNIPY_MACRO_ISENGINE_CONFIG_DETAILS'] = dedent("""\
        Returns:
            IsJobRunnerConfig: Active configuration object controlling engine behavior.
    """)

    os.environ['OMNIPY_MACRO_ISENGINE_REGISTRY_SUMMARY'] = (
        'Return the registry currently used for run-state reporting.')
    os.environ['OMNIPY_MACRO_ISENGINE_REGISTRY_DETAILS'] = dedent("""\
        Returns:
            IsRunStateRegistry | None: Registry receiving job-state updates, or ``None`` when
                state reporting is disabled.
    """)


@runtime_checkable
class IsEngine(Protocol):
    """Protocol for execution engines configured with registry state."""
    def __init__(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsJobRunnerConfig]:
        """{{ISENGINE_GET_CONFIG_CLS_SUMMARY}}

        {{ISENGINE_GET_CONFIG_CLS_DETAILS}}"""
        ...

    def set_config(self, config: IsJobRunnerConfig) -> None:
        """{{ISENGINE_SET_CONFIG_SUMMARY}}

        {{ISENGINE_SET_CONFIG_DETAILS}}"""
        ...

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        """{{ISENGINE_SET_REGISTRY_SUMMARY}}

        {{ISENGINE_SET_REGISTRY_DETAILS}}"""
        ...

    @property
    def config(self) -> IsJobRunnerConfig:
        """{{ISENGINE_CONFIG_SUMMARY}}

        {{ISENGINE_CONFIG_DETAILS}}"""
        ...

    @property
    def registry(self) -> IsRunStateRegistry | None:
        """{{ISENGINE_REGISTRY_SUMMARY}}

        {{ISENGINE_REGISTRY_DETAILS}}"""
        ...
