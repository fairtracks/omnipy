"""Shared type aliases and protocol-based callable definitions."""

from collections.abc import Callable
from types import GenericAlias, UnionType
from typing import (
    _AnnotatedAlias,  # type: ignore[attr-defined]
    _LiteralGenericAlias,  # type: ignore[attr-defined]
    _SpecialForm,
    _UnionGenericAlias,  # type: ignore[attr-defined]
    ForwardRef,
    Generic,
    ParamSpec,
    Protocol,
    Self,
    TypeAlias,
)

from typing_extensions import TypeVar

GeneralDecorator = Callable[[Callable], Callable]
LocaleType: TypeAlias = str | tuple[str | None, str | None]

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
