"""Protocols for job creator and job config holder contracts."""

from datetime import datetime
import os
from textwrap import dedent
from typing import Protocol, runtime_checkable

from omnipy.shared.protocols.compute.mixins import IsNestedContext
from omnipy.shared.protocols.config import IsJobConfig
from omnipy.shared.protocols.engine.base import IsEngine
from omnipy.util.helpers import is_package_editable

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISJOBCONFIGHOLDER_CONFIG_SUMMARY'] = (
        'Return the shared job configuration associated with the holder.')
    os.environ['OMNIPY_MACRO_ISJOBCONFIGHOLDER_CONFIG_DETAILS'] = dedent("""\
        Returns:
            IsJobConfig: Shared job configuration used for future jobs and runtime lookups.
    """)

    os.environ['OMNIPY_MACRO_ISJOBCONFIGHOLDER_ENGINE_SUMMARY'] = (
        'Return the engine currently associated with the holder, if any.')
    os.environ['OMNIPY_MACRO_ISJOBCONFIGHOLDER_ENGINE_DETAILS'] = dedent("""\
        Returns:
            IsEngine | None: Engine used for decorating applied jobs, or ``None`` when no engine
                has been configured.
    """)

    os.environ['OMNIPY_MACRO_ISJOBCONFIGHOLDER_SET_CONFIG_SUMMARY'] = (
        'Replace the shared job configuration used by the holder.')
    os.environ['OMNIPY_MACRO_ISJOBCONFIGHOLDER_SET_CONFIG_DETAILS'] = dedent("""\
        Args:
            config: Job configuration object to store for future jobs.
    """)

    os.environ['OMNIPY_MACRO_ISJOBCONFIGHOLDER_SET_ENGINE_SUMMARY'] = (
        'Set the engine used by the holder for future applied jobs.')
    os.environ['OMNIPY_MACRO_ISJOBCONFIGHOLDER_SET_ENGINE_DETAILS'] = dedent("""\
        Args:
            engine: Engine that should decorate jobs created through this holder.
    """)

    os.environ['OMNIPY_MACRO_ISJOBCREATOR_NESTED_CONTEXT_LEVEL_SUMMARY'] = (
        'Return the current depth of nested job-execution contexts.')
    os.environ['OMNIPY_MACRO_ISJOBCREATOR_NESTED_CONTEXT_LEVEL_DETAILS'] = dedent("""\
        Returns:
            int: Number of currently active nested execution contexts.
    """)

    os.environ['OMNIPY_MACRO_ISJOBCREATOR_TIME_OF_CUR_TOPLEVEL_NESTED_CONTEXT_RUN_SUMMARY'] = (
        'Return the start time for the active top-level execution context, if any.')
    os.environ['OMNIPY_MACRO_ISJOBCREATOR_TIME_OF_CUR_TOPLEVEL_NESTED_CONTEXT_RUN_DETAILS'] = (
        dedent("""\
        Returns:
            datetime | None: Timestamp recorded when the outermost execution context started, or
                ``None`` when no top-level context is active.
    """))


@runtime_checkable
class IsJobConfigHolder(Protocol):
    """Protocol for objects that hold mutable job config and engine state."""
    @property
    def config(self) -> IsJobConfig:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBCONFIGHOLDER_CONFIG_SUMMARY}}
        #
        # {{ISJOBCONFIGHOLDER_CONFIG_DETAILS}}
        """Return the shared job configuration associated with the holder.

        Returns:
            IsJobConfig: Shared job configuration used for future jobs and runtime lookups.
        """
        ...

    @property
    def engine(self) -> IsEngine | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBCONFIGHOLDER_ENGINE_SUMMARY}}
        #
        # {{ISJOBCONFIGHOLDER_ENGINE_DETAILS}}
        """Return the engine currently associated with the holder, if any.

        Returns:
            IsEngine | None: Engine used for decorating applied jobs, or ``None`` when no engine
                has been configured.
        """
        ...

    def set_config(self, config: IsJobConfig) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBCONFIGHOLDER_SET_CONFIG_SUMMARY}}
        #
        # {{ISJOBCONFIGHOLDER_SET_CONFIG_DETAILS}}
        """Replace the shared job configuration used by the holder.

        Args:
            config: Job configuration object to store for future jobs.
        """
        ...

    def set_engine(self, engine: IsEngine) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBCONFIGHOLDER_SET_ENGINE_SUMMARY}}
        #
        # {{ISJOBCONFIGHOLDER_SET_ENGINE_DETAILS}}
        """Set the engine used by the holder for future applied jobs.

        Args:
            engine: Engine that should decorate jobs created through this holder.
        """
        ...


@runtime_checkable
class IsJobCreator(IsNestedContext, IsJobConfigHolder, Protocol):
    """Protocol for nested-context job creators."""
    @property
    def nested_context_level(self) -> int:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBCREATOR_NESTED_CONTEXT_LEVEL_SUMMARY}}
        #
        # {{ISJOBCREATOR_NESTED_CONTEXT_LEVEL_DETAILS}}
        """Return the current depth of nested job-execution contexts.

        Returns:
            int: Number of currently active nested execution contexts.
        """
        ...

    @property
    def time_of_cur_toplevel_nested_context_run(self) -> datetime | None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISJOBCREATOR_TIME_OF_CUR_TOPLEVEL_NESTED_CONTEXT_RUN_SUMMARY}}
        #
        # {{ISJOBCREATOR_TIME_OF_CUR_TOPLEVEL_NESTED_CONTEXT_RUN_DETAILS}}
        """Return the start time for the active top-level execution context, if any.

        Returns:
            datetime | None: Timestamp recorded when the outermost execution context started, or
                ``None`` when no top-level context is active.
        """
        ...
