from typing import Protocol


class AssertLineOfOsLinesepSplitCrlfTextFunc(Protocol):
    """Callable protocol for asserting models or plain values."""

    def __call__(
        self,
        data: str,
        expected: str,
        with_newline: bool,
    ) -> None:
        """Assert a model-or-value object against type and content."""
        ...
