"""Protocols for runtime configuration, objects, and root logging."""

import logging
from logging.handlers import RotatingFileHandler
import os
from textwrap import dedent
from typing import Protocol, runtime_checkable

from omnipy.shared.enums.ui import UserInterfaceType
from omnipy.shared.protocols.compute.job_creator import IsJobConfigHolder
from omnipy.shared.protocols.config import (IsConfigBase,
                                            IsDataConfig,
                                            IsEngineConfig,
                                            IsJobConfig,
                                            IsRootLogConfig)
from omnipy.shared.protocols.data import IsDataClassCreator, IsReactiveObjects, IsSerializerRegistry
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry
from omnipy.shared.protocols.util import IsDataPublisher
from omnipy.util.helpers import is_package_editable

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISROOTLOGOBJECTS_SET_CONFIG_SUMMARY'] = (
        'Replace root logging configuration and rebuild logging objects.')
    os.environ['OMNIPY_MACRO_ISROOTLOGOBJECTS_SET_CONFIG_DETAILS'] = dedent("""\
        Args:
            config: New root logger configuration to apply.
    """)

    os.environ['OMNIPY_MACRO_ISROOTLOGOBJECTS_CONFIG_SUMMARY'] = (
        'Return the active root logging configuration.')
    os.environ['OMNIPY_MACRO_ISROOTLOGOBJECTS_CONFIG_DETAILS'] = dedent("""\
        Returns:
            IsRootLogConfig: Configuration currently used to construct formatter and handlers.
    """)

    os.environ['OMNIPY_MACRO_ISRUNTIMECONFIG_RESET_TO_DEFAULTS_SUMMARY'] = (
        'Reset all runtime configuration sections to their default values.')
    os.environ['OMNIPY_MACRO_ISRUNTIMECONFIG_RESET_TO_DEFAULTS_DETAILS'] = dedent("""\
        Rebuilds the data, engine, job, and root-log config sections and then refreshes runtime
        subscriptions when the config is attached to a runtime object.
    """)

    os.environ['OMNIPY_MACRO_ISRUNTIMEOBJECTS_SETUP_REACTIVE_SUMMARY'] = (
        'Create or remove reactive UI helpers for the detected interface.')
    os.environ['OMNIPY_MACRO_ISRUNTIMEOBJECTS_SETUP_REACTIVE_DETAILS'] = dedent("""\
        Args:
            ui_type: Detected user-interface type for the current runtime.
    """)

    os.environ['OMNIPY_MACRO_ISRUNTIME_RESET_SUBSCRIPTIONS_SUMMARY'] = (
        'Reset runtime subscriptions between config and runtime objects.')
    os.environ['OMNIPY_MACRO_ISRUNTIME_RESET_SUBSCRIPTIONS_DETAILS'] = dedent("""\
        This method rebuilds the callback graph that keeps configuration, engines, registries,
        logging, and reactive UI objects synchronized. Call it after replacing runtime subobjects
        manually.

        Raises:
            AssertionError: If a Jupyter UI is detected but reactive objects are unexpectedly
                missing.
    """)


@runtime_checkable
class IsRootLogObjects(Protocol):
    """Protocol for root logger helper objects."""

    formatter: logging.Formatter | None = None
    stdout_handler: logging.StreamHandler | None = None
    stderr_handler: logging.StreamHandler | None = None
    file_handler: RotatingFileHandler | None = None

    def set_config(self, config: IsRootLogConfig) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISROOTLOGOBJECTS_SET_CONFIG_SUMMARY}}
        #
        # {{ISROOTLOGOBJECTS_SET_CONFIG_DETAILS}}
        """Replace root logging configuration and rebuild logging objects.

        Args:
            config: New root logger configuration to apply.
"""
        ...

    @property
    def config(self) -> IsRootLogConfig:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISROOTLOGOBJECTS_CONFIG_SUMMARY}}
        #
        # {{ISROOTLOGOBJECTS_CONFIG_DETAILS}}
        """Return the active root logging configuration.

        Returns:
            IsRootLogConfig: Configuration currently used to construct formatter and handlers.
"""
        ...


@runtime_checkable
class IsRuntimeConfig(IsConfigBase, Protocol):
    """Protocol for the aggregated runtime configuration."""

    data: IsDataConfig
    engine: IsEngineConfig
    job: IsJobConfig
    root_log: IsRootLogConfig

    def reset_to_defaults(self) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISRUNTIMECONFIG_RESET_TO_DEFAULTS_SUMMARY}}
        #
        # {{ISRUNTIMECONFIG_RESET_TO_DEFAULTS_DETAILS}}
        """Reset all runtime configuration sections to their default values.

        Rebuilds the data, engine, job, and root-log config sections and then refreshes runtime
        subscriptions when the config is attached to a runtime object.
"""
        ...


@runtime_checkable
class IsRuntimeObjects(IsDataPublisher, Protocol):
    """Protocol for the instantiated objects owned by the runtime."""

    job_creator: IsJobConfigHolder
    data_class_creator: IsDataClassCreator
    reactive: IsReactiveObjects | None
    local: IsEngine
    prefect: IsEngine
    registry: IsRunStateRegistry
    serializers: IsSerializerRegistry
    root_log: IsRootLogObjects

    def setup_reactive(self, ui_type: UserInterfaceType.Literals) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISRUNTIMEOBJECTS_SETUP_REACTIVE_SUMMARY}}
        #
        # {{ISRUNTIMEOBJECTS_SETUP_REACTIVE_DETAILS}}
        """Create or remove reactive UI helpers for the detected interface.

        Args:
            ui_type: Detected user-interface type for the current runtime.
"""
        ...


@runtime_checkable
class IsRuntime(Protocol):
    """Protocol for the Omnipy runtime container."""

    config: IsRuntimeConfig
    objects: IsRuntimeObjects

    def reset_subscriptions(self):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISRUNTIME_RESET_SUBSCRIPTIONS_SUMMARY}}
        #
        # {{ISRUNTIME_RESET_SUBSCRIPTIONS_DETAILS}}
        """Reset runtime subscriptions between config and runtime objects.

        This method rebuilds the callback graph that keeps configuration, engines, registries,
        logging, and reactive UI objects synchronized. Call it after replacing runtime subobjects
        manually.
        
        Raises:
            AssertionError: If a Jupyter UI is detected but reactive objects are unexpectedly
                missing.
"""
        ...
