from collections.abc import Generator, Iterable
from typing import Any, Literal, overload, Protocol, SupportsIndex

from typing_extensions import override, Self, TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols._typeshed import (ConvertibleToFloat,
                                               ConvertibleToInt,
                                               SupportsKeysAndGetItem)
from omnipy.shared.protocols.builtins import (_NegativeInteger,
                                              _PositiveInteger,
                                              IsBool,
                                              IsBytes,
                                              IsDict,
                                              IsFloat,
                                              IsInt,
                                              IsList,
                                              IsSet,
                                              IsStr,
                                              IsTuple)
from omnipy.shared.protocols.typing import (IsAbstractSet,
                                            IsHashable,
                                            IsMapping,
                                            IsSequenceNotStrBytes)

_KeyT = TypeVar('_KeyT')
_NestedKeyT = TypeVar('_NestedKeyT')
_ValT = TypeVar('_ValT')
_OtherT = TypeVar('_OtherT')
_ValSeqOrGenT = TypeVar('_ValSeqOrGenT', bound=IsSequenceNotStrBytes | Generator)
_ValMappingT = TypeVar('_ValMappingT', bound=IsMapping)
_NestedValT = TypeVar('_NestedValT')
_SecondValT = TypeVar('_SecondValT')


class IsIntContent(IsInt, Protocol):
    def __add__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __sub__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __mul__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __floordiv__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __truediv__(self, value: ConvertibleToInt, /) -> float:
        raise AssumedToBeImplementedException

    def __mod__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __divmod__(self, value: ConvertibleToInt, /) -> tuple[int, int]:
        raise AssumedToBeImplementedException

    def __radd__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rsub__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rmul__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rfloordiv__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rtruediv__(self, value: ConvertibleToInt, /) -> float:
        raise AssumedToBeImplementedException

    def __rmod__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rdivmod__(self, value: ConvertibleToInt, /) -> tuple[int, int]:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __pow__(self, x: Literal[0], /) -> Literal[1]:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: Literal[0], mod: None, /) -> Literal[1]:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: _PositiveInteger, mod: None = None, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: _NegativeInteger, mod: None = None, /) -> float:
        raise AssumedToBeImplementedException

    # positive __value -> int; negative __value -> float
    # return type must be Any as `int | float` causes too many false-positive errors
    @overload
    def __pow__(self, value: ConvertibleToInt, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: ConvertibleToInt, mod: ConvertibleToInt, /) -> Self:
        raise AssumedToBeImplementedException

    def __pow__(  # pyright: ignore[reportIncompatibleMethodOverride]
            self,
            value: ConvertibleToInt,
            mod: ConvertibleToInt | None = None,
            /) -> Self | float:
        raise AssumedToBeImplementedException

    def __rpow__(self, value: ConvertibleToInt, mod: ConvertibleToInt | None = None, /) -> Any:
        raise AssumedToBeImplementedException

    def __and__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __or__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __xor__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __lshift__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rshift__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rand__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __ror__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rxor__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rlshift__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rrshift__(self, value: ConvertibleToInt, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException


class IsFloatContent(IsFloat, Protocol):
    def __add__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __sub__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __mul__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __floordiv__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __truediv__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __mod__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __divmod__(self, value: ConvertibleToFloat, /) -> tuple[float, float]:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __pow__(self, value: ConvertibleToFloat, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: ConvertibleToInt, mod: None = None, /) -> Self:
        raise AssumedToBeImplementedException

    # positive __value -> float; negative __value -> complex
    # return type must be Any as `float | complex` causes too many false-positive errors

    def __pow__(self, value: ConvertibleToFloat | ConvertibleToInt, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException

    def __radd__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rsub__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rmul__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rfloordiv__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rtruediv__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rmod__(self, value: ConvertibleToFloat, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    def __rdivmod__(self, value: ConvertibleToFloat, /) -> tuple[float, float]:
        raise AssumedToBeImplementedException

    def __rpow__(self, value: ConvertibleToInt | ConvertibleToFloat, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException


class IsBoolContent(IsBool, Protocol):
    @overload  # type: ignore [override]
    def __and__(self, value: IsBool, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __and__(self, value: int, /) -> int:  # type: ignore [overload-overlap]
        raise AssumedToBeImplementedException

    @overload
    def __and__(self, value: ConvertibleToInt, /) -> Self:
        raise AssumedToBeImplementedException

    def __and__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: ConvertibleToInt | IsBool,
        /,
    ) -> int | Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __or__(self, value: IsBool, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: int, /) -> int:  # type: ignore [overload-overlap]
        raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: ConvertibleToInt, /) -> Self:
        raise AssumedToBeImplementedException

    def __or__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: ConvertibleToInt | IsBool,
        /,
    ) -> int | Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __xor__(self, value: IsBool, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __xor__(self, value: int, /) -> int:  # type: ignore [overload-overlap]
        raise AssumedToBeImplementedException

    @overload
    def __xor__(self, value: ConvertibleToInt, /) -> Self:
        raise AssumedToBeImplementedException

    def __xor__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: ConvertibleToInt | IsBool,
        /,
    ) -> int | Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __rand__(self, value: IsBool, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __rand__(self, value: int, /) -> int:  # type: ignore [overload-overlap]
        raise AssumedToBeImplementedException

    @overload
    def __rand__(self, value: ConvertibleToInt, /) -> Self:
        raise AssumedToBeImplementedException

    def __rand__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: ConvertibleToInt | IsBool,
        /,
    ) -> int | Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __ror__(self, value: IsBool, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __ror__(self, value: int, /) -> int:  # type: ignore [overload-overlap]
        raise AssumedToBeImplementedException

    @overload
    def __ror__(self, value: ConvertibleToInt, /) -> Self:
        raise AssumedToBeImplementedException

    def __ror__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: ConvertibleToInt | IsBool,
        /,
    ) -> int | Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __rxor__(self, value: IsBool, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __rxor__(self, value: int, /) -> int:  # type: ignore [overload-overlap]
        raise AssumedToBeImplementedException

    @overload
    def __rxor__(self, value: ConvertibleToInt, /) -> Self:
        raise AssumedToBeImplementedException

    def __rxor__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: ConvertibleToInt | IsBool,
        /,
    ) -> int | Self:
        raise AssumedToBeImplementedException


class IsStrContent(IsStr, Protocol):
    def __add__(self, value: IsStr, /) -> Self:
        raise AssumedToBeImplementedException


class IsBytesContent(IsBytes, Protocol):
    def __add__(self, value: IsBytes, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException


class IsSetContent(IsSet[_ValT], Protocol[_ValT]):
    @override
    def difference(self, *s: Iterable[object]) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    @override
    def difference_update(self, *s: Iterable[object]) -> None:
        raise AssumedToBeImplementedException

    @override
    def intersection(self, *s: Iterable[object]) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    @override
    def intersection_update(self, *s: Iterable[object]) -> None:
        raise AssumedToBeImplementedException

    @overload
    def symmetric_difference(  # pyright: ignore[reportOverlappingOverload]
            self,
            value: Iterable[_ValT],
            /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def symmetric_difference(self, value: Iterable[_OtherT], /) -> set[_ValT | _OtherT]:
        raise AssumedToBeImplementedException

    @override
    def symmetric_difference(self, value: Iterable[object], /) -> Self | set[_ValT | _OtherT]:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def union(  # pyright: ignore[reportOverlappingOverload]
            self,
            value: Iterable[_ValT],
            /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def union(self, value: Iterable[_OtherT], /) -> set[_ValT | _OtherT]:
        raise AssumedToBeImplementedException

    @override
    def union(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: Iterable[object],
        /,
    ) -> Self | set[_ValT | _OtherT]:
        raise AssumedToBeImplementedException

    @override
    def __and__(  # type: ignore [override]
        self,
        value: IsAbstractSet[object] | IsSequenceNotStrBytes[object] | Generator[object],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @override
    def __iand__(  # type: ignore [override]
        self,
        value: IsAbstractSet[object] | IsSequenceNotStrBytes[object] | Generator[object],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __or__(
        self,
        value: IsAbstractSet[_ValT] | IsSequenceNotStrBytes[_ValT] | Generator[_ValT],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: IsAbstractSet[_OtherT], /) -> set[_ValT | _OtherT]:
        raise AssumedToBeImplementedException

    @override
    def __or__(
        self,
        value: IsAbstractSet[object] | IsSequenceNotStrBytes[_ValT] | Generator[_ValT],
        /,
    ) -> Self | set[_ValT | _OtherT]:
        raise AssumedToBeImplementedException

    @override
    def __ior__(  # type: ignore [override]
        self,
        value: IsAbstractSet[_ValT] | IsSequenceNotStrBytes[_ValT] | Generator[_ValT],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @override
    def __sub__(  # type: ignore [override]
        self,
        value: (IsAbstractSet[_ValT | None] | IsSequenceNotStrBytes[_ValT | None]
                | Generator[_ValT | None]),
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @override
    def __isub__(  # type: ignore [override]
        self,
        value: IsAbstractSet[object] | IsSequenceNotStrBytes[object] | Generator[object],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __xor__(
        self,
        value: IsAbstractSet[_ValT] | IsSequenceNotStrBytes[_ValT] | Generator[_ValT],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __xor__(self, value: IsAbstractSet[_OtherT], /) -> set[_ValT | _OtherT]:
        raise AssumedToBeImplementedException

    @override
    def __xor__(
        self,
        value: IsAbstractSet[object] | IsSequenceNotStrBytes[_ValT] | Generator[_ValT],
        /,
    ) -> Self | set[_ValT | _OtherT]:
        raise AssumedToBeImplementedException

    @override
    def __ixor__(  # type: ignore [override]
        self,
        value: IsAbstractSet[_ValT] | IsSequenceNotStrBytes[_ValT] | Generator[_ValT],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException


class IsListContent(IsList[_ValT], Protocol[_ValT]):
    @override
    def __add__(  # type: ignore [override]
        self,
        values: IsSequenceNotStrBytes[_ValT] | Generator[_ValT],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __getitem__(self, i: SupportsIndex, /) -> _ValT:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, s: slice, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, s: slice | SupportsIndex, /) -> Self | _ValT:
        raise AssumedToBeImplementedException

    @override
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        index: SupportsIndex | slice,
        /,
    ) -> Self | _ValT:
        raise AssumedToBeImplementedException

    @override
    def __mul__(self, value: SupportsIndex, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

    @override
    def __rmul__(self, value: SupportsIndex, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException


class IsListOfListsContent(IsListContent[_ValSeqOrGenT | IsSequenceNotStrBytes[_NestedValT]
                                         | Generator[_NestedValT]],
                           Protocol[_ValSeqOrGenT, _NestedValT]):
    @overload  # type: ignore [override]
    def __getitem__(self, index: SupportsIndex, /) -> _ValSeqOrGenT:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(
        self,
        index: slice,
        /,
    ) -> IsListContent[_ValSeqOrGenT]:
        raise AssumedToBeImplementedException

    @override
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
            self, index: SupportsIndex | slice, /) -> _ValSeqOrGenT | IsListContent[_ValSeqOrGenT]:
        raise AssumedToBeImplementedException

    @override
    def __mul__(  # type: ignore [override]
            self, value: SupportsIndex, /) -> IsListContent[_ValSeqOrGenT]:
        raise AssumedToBeImplementedException

    @override
    def __rmul__(  # type: ignore [override]
            self, value: SupportsIndex, /) -> IsListContent[_ValSeqOrGenT]:
        raise AssumedToBeImplementedException


class IsListOfDictsContent(IsListContent[(_ValMappingT
                                          | SupportsKeysAndGetItem[_NestedKeyT, _NestedValT]
                                          | Iterable[tuple[_NestedKeyT, _NestedValT]])],
                           Protocol[_ValMappingT, _NestedKeyT, _NestedValT]):
    @overload  # type: ignore [override]
    def __getitem__(self, index: SupportsIndex, /) -> _ValMappingT:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, index: slice, /) -> IsListContent[_ValMappingT]:
        raise AssumedToBeImplementedException

    @override
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        index: SupportsIndex | slice,
        /,
    ) -> _ValMappingT | IsListContent[_ValMappingT]:
        raise AssumedToBeImplementedException

    @override
    def __mul__(  # type: ignore [override]
            self, value: SupportsIndex, /) -> IsListContent[_ValMappingT]:
        raise AssumedToBeImplementedException

    @override
    def __rmul__(  # type: ignore [override]
            self, value: SupportsIndex, /) -> IsListContent[_ValMappingT]:
        raise AssumedToBeImplementedException


class IsSameTypeTupleContent(IsHashable, IsTuple[_ValT], Protocol[_ValT]):
    """Protocol for single-type tuples as Model content, e.g. `Model[tuple[int, ...]]`

    IsSameTypeTupleContent has the same interface as the builtin class
    `tuple`, but where all elements of the same type (e.g. `tuple[int,
    ...]`). As it is meant to annotate Omnipy Models for static typing, it
    supports broader interoperability with other iterables of the same
    element type.
    """
    @override
    def __add__(  # type: ignore [override]
        self,
        value: IsSequenceNotStrBytes[_ValT] | Generator[_ValT],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException


class IsPairTupleContent(IsHashable, IsTuple[_ValT | _SecondValT], Protocol[_ValT, _SecondValT]):
    """Protocol for paired-type tuples as Model content, e.g. `Model[tuple[int, str]]`

    IsPairTupleContent is a protocol with the same interface as the builtin class
    tuple, with exactly two elements (e.g. tuple[int, str]). As it is meant
    to annotate Omnipy Models for static typing, it does not support `+`
    and `*` operators (other than for empty tuples and multiplying by 1),
    as these operations would cause validation to fail.
    """
    @override
    def __add__(  # type: ignore [override]
            self, value: tuple[()], /) -> Self:
        raise AssumedToBeImplementedException

    @override
    def __mul__(  # type: ignore [override]
            self, value: Literal[1], /) -> Self:
        raise AssumedToBeImplementedException

    @override
    def __rmul__(  # type: ignore [override]
            self, value: Literal[1], /) -> Self:
        raise AssumedToBeImplementedException


class IsDictContent(IsDict[_KeyT, _ValT], Protocol[_KeyT, _ValT]):
    @override
    @classmethod
    def fromkeys(  # type: ignore [override]
        cls,
        iterable: Iterable[_KeyT],
        value: _ValT | None = None,
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __or__(self, value: SupportsKeysAndGetItem[_KeyT, _ValT], /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: Iterable[tuple[_KeyT, _ValT]], /) -> Self:
        raise AssumedToBeImplementedException

    @override
    def __or__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: SupportsKeysAndGetItem[_KeyT, _ValT] | Iterable[tuple[_KeyT, _ValT]],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __ror__(self, value: SupportsKeysAndGetItem[_KeyT, _ValT], /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __ror__(self, value: Iterable[tuple[_KeyT, _ValT]], /) -> Self:
        raise AssumedToBeImplementedException

    @override
    def __ror__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value: SupportsKeysAndGetItem[_KeyT, _ValT] | Iterable[tuple[_KeyT, _ValT]],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException


class IsDictOfListsContent(IsDictContent[_KeyT,
                                         _ValSeqOrGenT | IsSequenceNotStrBytes[_NestedValT]
                                         | Generator[_NestedValT]],
                           Protocol[_KeyT, _ValSeqOrGenT, _NestedValT]):
    @override
    def __getitem__(self, key: _KeyT, /) -> _ValSeqOrGenT:
        raise AssumedToBeImplementedException


class IsDictOfDictsContent(IsDictContent[_KeyT,
                                         (_ValMappingT
                                          | SupportsKeysAndGetItem[_NestedKeyT, _NestedValT]
                                          | Iterable[tuple[_NestedKeyT, _NestedValT]])],
                           Protocol[_KeyT, _ValMappingT, _NestedKeyT, _NestedValT]):
    @override
    def __getitem__(self, key: _KeyT, /) -> _ValMappingT:
        raise AssumedToBeImplementedException
