from typing import Literal, overload, Protocol, SupportsIndex
from collections.abc import Generator, Iterable

from typing_extensions import override, Self, TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols._typeshed import SupportsKeysAndGetItem
from omnipy.shared.protocols.builtins import IsBytes, IsDict, IsList, IsStr, IsTuple
from omnipy.shared.protocols.typing import IsHashable, IsMapping, IsSequenceNotStrBytes

_KeyT = TypeVar('_KeyT')
_NestedKeyT = TypeVar('_NestedKeyT')
_ValT = TypeVar('_ValT')
_ValSeqOrGenT = TypeVar('_ValSeqOrGenT', bound=IsSequenceNotStrBytes | Generator)
_ValMappingT = TypeVar('_ValMappingT', bound=IsMapping)
_NestedValT = TypeVar('_NestedValT')
_SecondValT = TypeVar('_SecondValT')


class IsStrContent(IsStr, Protocol):
    def __add__(self, value: IsStr, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException


class IsBytesContent(IsBytes, Protocol):
    def __add__(self, value: IsBytes, /) -> Self:  # type: ignore [override]
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

    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        index: SupportsIndex | slice,
        /,
    ) -> Self | _ValT:
        raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException

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

    def __mul__(  # type: ignore [override]
            self, value: SupportsIndex, /) -> IsListContent[_ValSeqOrGenT]:
        raise AssumedToBeImplementedException

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

    def __mul__(  # type: ignore [override]
            self, value: SupportsIndex, /) -> IsListContent[_ValMappingT]:
        raise AssumedToBeImplementedException

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
    @classmethod
    def fromkeys(  # type: ignore [override]
            cls,
            iterable: Iterable[_KeyT],
            value: _ValT = None,
            /,
    ) -> Self:
        raise AssumedToBeImplementedException

    @overload  # type: ignore [override]
    def __or__(self, value: SupportsKeysAndGetItem[_KeyT, _ValT], /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: Iterable[tuple[_KeyT, _ValT]], /) -> Self:
        raise AssumedToBeImplementedException

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
    def __getitem__(self, key: _KeyT, /) -> _ValMappingT:
        raise AssumedToBeImplementedException
