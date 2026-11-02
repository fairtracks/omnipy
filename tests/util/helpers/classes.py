"""Helper classes for utility tests."""

from collections.abc import Iterator


class UnavailableIterable:
    """Expose the iterable interface while rejecting iteration at runtime."""

    def __iter__(self) -> Iterator[int]:
        raise TypeError('Iteration is unavailable')


class SomeObject:
    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other):
        if isinstance(other, SomeObject):
            return self.name == other.name
        return False
