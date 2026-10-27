"""Shared type aliases and protocol-based callable definitions."""

from collections.abc import Callable
from types import GenericAlias, UnionType

from typing import _AnnotatedAlias  # type: ignore[attr-defined]  # isort: skip
from typing import _LiteralGenericAlias  # type: ignore[attr-defined]  # isort: skip
from typing import _UnionGenericAlias  # type: ignore[attr-defined]  # isort: skip
from typing import (
    _SpecialForm,
    ForwardRef,
    Generic,
    ParamSpec,
    Protocol,
    Self,
    TYPE_CHECKING,
    TypeAlias,
)

from typing_extensions import TypeVar

import omnipy.util.pydantic as pyd

GeneralDecorator = Callable[[Callable], Callable]
LocaleType: TypeAlias = str | tuple[str | None, str | None]

# As for the constrained types of pydantic, type checkers see a plain float
if TYPE_CHECKING:
    ZeroToOneFloat = float
else:

    class ZeroToOneFloat(pyd.ConstrainedFloat):
        """A float strictly between 0 and 1, validated by pydantic."""

        gt = 0
        lt = 1


# TODO: While waiting for https://github.com/python/mypy/issues/9773
TypeForm: TypeAlias = (
    type
    | UnionType
    | None
    | _UnionGenericAlias
    | _AnnotatedAlias
    | GenericAlias
    | _LiteralGenericAlias
    | _SpecialForm
    | ForwardRef
    | TypeVar
)

P = ParamSpec('P')
RetT = TypeVar('RetT', covariant=True)


class Method(Protocol, Generic[P, RetT]):
    """Protocol for bound methods with preserved parameter and return types."""

    def __call__(self: Self, *args: P.args, **kwargs: P.kwargs) -> RetT: ...
