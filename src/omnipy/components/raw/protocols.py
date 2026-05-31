"""Protocols for raw-text content transformation callbacks."""

from typing import Protocol


class IsModifyContentCallable(Protocol):
    """Protocol for callbacks that rewrite an entire raw content item."""

    def __call__(self, data_file: str, **kwargs: object) -> str:
        ...


class IsModifyEachLineCallable(Protocol):
    """Protocol for callbacks that rewrite one line at a time."""

    def __call__(self, line_no: int, line: str, **kwargs: object) -> str:
        ...


class IsModifyAllLinesCallable(Protocol):
    """Protocol for callbacks that rewrite a list of lines in bulk."""

    def __call__(self, all_lines: list[str], **kwargs: object) -> list[str]:
        ...
