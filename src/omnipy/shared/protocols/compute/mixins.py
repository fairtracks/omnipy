"""Shared mixin protocols for compute contracts."""

from typing import Protocol


class IsUniquelyNamedJob(Protocol):
    """Protocol for jobs with stable and regenerated names."""

    @property
    def name(self) -> str:
        ...

    @property
    def unique_run_slug(self) -> str:
        ...

    @property
    def unique_name(self) -> str:
        ...

    def __init__(self, *args, name: str | None = None):
        ...

    def regenerate_unique_name(self) -> None:
        ...


class IsNestedContext(Protocol):
    """Protocol for objects that manage nested execution contexts."""

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...
