"""Protocols shared by test helpers and fixtures."""

from typing import Protocol

from omnipy.shared.typedefs import TypeForm


class AssertModelOrValFunc(Protocol):
    """Callable protocol for asserting models or plain values."""

    def __call__(
        self,
        model_or_val: object,
        target_type: TypeForm,
        content: object,
    ) -> None:
        """Assert a model-or-value object against type and content."""
        ...
