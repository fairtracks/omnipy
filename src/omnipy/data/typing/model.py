from typing import Any, Generic, Self, TypeVar

from omnipy import Model
from omnipy.shared.typing import TYPE_CHECKER

_RootT = TypeVar('_RootT')


class PlainModel(
    Model[_RootT],
    Generic[_RootT],
):
    """Minimal generic stand-in for ``Model[_RootT]`` during type checking."""

    if TYPE_CHECKER != 'mypy':

        def __new__(cls, *args: Any, **kwargs: Any) -> Self: ...
