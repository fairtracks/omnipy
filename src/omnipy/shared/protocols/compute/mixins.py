"""Shared mixin protocols for compute contracts."""

import os
from textwrap import dedent
from typing import Protocol

from omnipy.util.helpers import is_package_editable

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_ISUNIQUELYNAMEDJOB_NAME_SUMMARY'] = (
        'Return the configured base name for the job.')
    os.environ['OMNIPY_MACRO_ISUNIQUELYNAMEDJOB_NAME_DETAILS'] = dedent("""\
        Returns:
            str: Human-readable name used as the basis for display and registration.
    """)

    os.environ['OMNIPY_MACRO_ISUNIQUELYNAMEDJOB_UNIQUE_NAME_SUMMARY'] = (
        'Return the generated unique name used to identify the job instance.')
    os.environ['OMNIPY_MACRO_ISUNIQUELYNAMEDJOB_UNIQUE_NAME_DETAILS'] = dedent("""\
        Returns:
            str: Unique job identifier suitable for registry lookups and logging.
    """)

    os.environ['OMNIPY_MACRO_ISUNIQUELYNAMEDJOB_UNIQUE_RUN_SLUG_SUMMARY'] = (
        'Return the run-specific slug generated for this job instance.')
    os.environ['OMNIPY_MACRO_ISUNIQUELYNAMEDJOB_UNIQUE_RUN_SLUG_DETAILS'] = dedent("""\
        Returns:
            str: Short slug used in per-run names and identifiers.
    """)

    os.environ['OMNIPY_MACRO_ISUNIQUELYNAMEDJOB_REGENERATE_UNIQUE_NAME_SUMMARY'] = (
        'Regenerate the unique job name from the current base name.')
    os.environ['OMNIPY_MACRO_ISUNIQUELYNAMEDJOB_REGENERATE_UNIQUE_NAME_DETAILS'] = dedent("""\
        Updates the stored unique identifier so later registry entries and log messages use a
        fresh value.
    """)


class IsUniquelyNamedJob(Protocol):
    """Protocol for jobs with stable and regenerated names."""
    @property
    def name(self) -> str:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISUNIQUELYNAMEDJOB_NAME_SUMMARY}}
        #
        # {{ISUNIQUELYNAMEDJOB_NAME_DETAILS}}
        """Return the configured base name for the job.

        Returns:
            str: Human-readable name used as the basis for display and registration.
"""
        ...

    @property
    def unique_run_slug(self) -> str:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISUNIQUELYNAMEDJOB_UNIQUE_RUN_SLUG_SUMMARY}}
        #
        # {{ISUNIQUELYNAMEDJOB_UNIQUE_RUN_SLUG_DETAILS}}
        """Return the run-specific slug generated for this job instance.

        Returns:
            str: Short slug used in per-run names and identifiers.
"""
        ...

    @property
    def unique_name(self) -> str:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISUNIQUELYNAMEDJOB_UNIQUE_NAME_SUMMARY}}
        #
        # {{ISUNIQUELYNAMEDJOB_UNIQUE_NAME_DETAILS}}
        """Return the generated unique name used to identify the job instance.

        Returns:
            str: Unique job identifier suitable for registry lookups and logging.
"""
        ...

    def __init__(self, *args, name: str | None = None):
        ...

    def regenerate_unique_name(self) -> None:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{ISUNIQUELYNAMEDJOB_REGENERATE_UNIQUE_NAME_SUMMARY}}
        #
        # {{ISUNIQUELYNAMEDJOB_REGENERATE_UNIQUE_NAME_DETAILS}}
        """Regenerate the unique job name from the current base name.

        Updates the stored unique identifier so later registry entries and log messages use a
        fresh value.
"""
        ...


class IsNestedContext(Protocol):
    """Protocol for objects that manage nested execution contexts."""
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...
