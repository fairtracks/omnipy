from __future__ import annotations

from typing import Optional, Protocol


class IsUniquelyNamedJob(Protocol):
    """"""
    @property
    def name(self) -> str:
        ...

    @property
    def unique_name(self) -> str:
        ...

    def __init__(self, *, name: Optional[str] = None):
        ...

    def regenerate_unique_name(self) -> None:
        ...


class IsNestedContext(Protocol):
    """"""
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...
