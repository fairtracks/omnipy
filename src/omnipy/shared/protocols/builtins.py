from collections.abc import Iterable, Iterator, Sized
import sys
from typing import Any, Callable, overload, Protocol, SupportsIndex, TypeVar

from typing_extensions import override, Self

from omnipy.shared.exceptions import AssumedToBeImplementedException

_KeyT = TypeVar('_KeyT')
_ValT = TypeVar('_ValT')
_ValCovT = TypeVar('_ValCovT', covariant=True)
_SecondValT = TypeVar('_SecondValT')
_OtherValT = TypeVar('_OtherValT')


class SupportsKeysAndGetItem(Protocol[_KeyT, _ValCovT]):
    def keys(self) -> Iterable[_KeyT]:
        ...

    def __getitem__(self, __key: _KeyT, /) -> _ValCovT:
        ...


class IsCollection(Protocol[_ValT]):
    """
    IsCollection is a protocol with the same interface as the abstract class
    Collection.
    """
    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_ValT]:
        raise AssumedToBeImplementedException

    def __contains__(self, value: _ValT, /) -> bool:
        raise AssumedToBeImplementedException


class IsReversible(Protocol[_ValCovT]):
    """
    IsReversible is a protocol with the same interface as the abstract class
    Reversible.
    """
    def __reversed__(self) -> Iterator[_ValCovT]:
        raise AssumedToBeImplementedException


class IsHashable(Protocol):
    """
    IsHashable is a protocol with the same interface as the abstract class
    Hashable.
    """
    def __hash__(self) -> int:
        raise AssumedToBeImplementedException


class IsSequence(IsCollection[_ValT], IsReversible[_ValT], Protocol[_ValT]):
    """
    IsSequence is a protocol with the same interface as the abstract class
    Sequence.
    """
    def __getitem__(self, index: SupportsIndex, /) -> _ValT:
        raise AssumedToBeImplementedException

    def index(self,
              value: _ValT,
              start: SupportsIndex = 0,
              stop: SupportsIndex = sys.maxsize,
              /) -> int:
        """
        S.index(value, [start, [stop]]) -> integer -- return first index of value.
        Raises ValueError if the value is not present.

        Supporting start and stop arguments is optional, but recommended.
        """
        raise AssumedToBeImplementedException

    def count(self, value: _ValT, /) -> int:
        """
        S.count(value) -> integer -- return number of occurrences of value
        """
        raise AssumedToBeImplementedException

    def __add__(self, values: Self, /) -> Self:
        raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def __gt__(self, value: Self, /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: Self, /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, value: Self, /) -> bool:
        raise AssumedToBeImplementedException

    def __le__(self, value: Self, /) -> bool:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException


class IsMutableSequence(IsSequence[_ValT], Protocol[_ValT]):
    """
    IsMutableSequence is a protocol with the same interface as the abstract class
    MutableSequence.
    """
    def __setitem__(self, index: SupportsIndex, value: _ValT, /) -> None:
        raise AssumedToBeImplementedException

    def __delitem__(self, index: SupportsIndex | slice, /) -> None:
        raise AssumedToBeImplementedException

    def insert(self, index: SupportsIndex, value: _ValT, /) -> None:
        """
        S.insert(index, value) -- insert value before index
        """
        raise AssumedToBeImplementedException

    def append(self, object: _ValT, /) -> None:
        """
        S.append(value) -- append value to the end of the sequence
        """
        raise AssumedToBeImplementedException

    def clear(self) -> None:
        """
        S.clear() -> None -- remove all items from S
        """
        raise AssumedToBeImplementedException

    def reverse(self) -> None:
        """
        S.reverse() -- reverse *IN PLACE*
        """
        raise AssumedToBeImplementedException

    def extend(self, iterable: Iterable[_ValT], /) -> None:
        """
        S.extend(iterable) -- extend sequence by appending elements from the iterable
        """
        raise AssumedToBeImplementedException

    def pop(self, index: SupportsIndex = -1, /) -> _ValT:
        """
        S.pop([index]) -> item -- remove and return item at index (default last).
        Raise IndexError if list is empty or index is out of range.
        """
        raise AssumedToBeImplementedException

    def remove(self, value: _ValT, /) -> None:
        """
        S.remove(value) -- remove first occurrence of value.
        Raise ValueError if the value is not present.
        """
        raise AssumedToBeImplementedException

    def __iadd__(self, values: Iterable[_ValT], /) -> Self:
        raise AssumedToBeImplementedException

    def __imul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException


class SupportsRichComparison(Protocol):
    def __lt__(self, other: Any, /) -> bool:
        ...

    def __gt__(self, other: Any, /) -> bool:
        ...


class IsList(IsMutableSequence[_ValT], Protocol[_ValT]):
    """
    IsList is a protocol with the same interface as the builtin class list.
    """
    @overload
    def sort(self, *, key: None = None, reverse: bool = False) -> None:
        raise AssumedToBeImplementedException

    @overload
    def sort(self,
             *,
             key: Callable[[_ValT], SupportsRichComparison],
             reverse: bool = False) -> None:
        raise AssumedToBeImplementedException

    def sort(self,
             *,
             key: Callable[[_ValT], SupportsRichComparison] | None = None,
             reverse: bool = False) -> None:
        raise AssumedToBeImplementedException


class IsSameTypeTuple(IsHashable, IsSequence[_ValT], Protocol[_ValT]):
    """
    IsSameTypeTuple is a protocol with the same interface as the builtin
    class tuple, with all elements of the same type (e.g. tuple[int, ...]).
    """
    @overload  # type: ignore [override]
    def __add__(self, value: tuple[_ValT, ...], /) -> tuple[_ValT, ...]:
        raise AssumedToBeImplementedException

    @overload
    def __add__(self, value: tuple[_OtherValT, ...], /) -> tuple[_OtherValT | _ValT, ...]:
        raise AssumedToBeImplementedException

    @override
    def __add__(  # pyright: ignore [reportIncompatibleMethodOverride]
        self,
        value: tuple[_ValT, ...] | tuple[_OtherValT, ...],
        /,
    ) -> tuple[_ValT, ...] | tuple[_OtherValT | _ValT, ...]:
        raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> tuple[_ValT, ...]:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: SupportsIndex, /) -> tuple[_ValT, ...]:
        raise AssumedToBeImplementedException


class IsPairTuple(IsSameTypeTuple[_ValT | _SecondValT], Protocol[_ValT, _SecondValT]):
    """
    IsPairTuple is a protocol with the same interface as the builtin class
    tuple, with exactly two elements (e.g. tuple[int, str]).
    """


class IsMapping(IsCollection[_KeyT], Protocol[_KeyT, _ValT]):
    """
    IsMapping is a protocol with the same interface as the abstract class
    Mapping. It is the protocol of a generic container for associating
    key/value pairs.
    """
    def __getitem__(self, key: _KeyT, /) -> _ValT:
        raise AssumedToBeImplementedException

    def get(self, key: _KeyT, /) -> _ValT | None:
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        raise AssumedToBeImplementedException

    def __contains__(self, key: _KeyT, /) -> bool:
        raise AssumedToBeImplementedException

    def keys(self) -> 'IsKeysView[_KeyT]':
        """
        D.keys() -> a set-like object providing a view on D's keys
        """
        raise AssumedToBeImplementedException

    def items(self) -> 'IsItemsView[_KeyT, _ValT]':
        """
        D.items() -> a set-like object providing a view on D's items
        """
        raise AssumedToBeImplementedException

    def values(self) -> 'IsValuesView[_ValT]':
        """
        D.values() -> an object providing a view on D's values
        """
        raise AssumedToBeImplementedException

    def __eq__(self, other: object, /) -> bool:
        raise AssumedToBeImplementedException


class IsMappingView(Sized, Protocol):
    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __repr__(self) -> str:
        raise AssumedToBeImplementedException


class IsKeysView(IsMappingView, Protocol[_KeyT]):
    def __contains__(self, key: _KeyT) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_KeyT]:
        raise AssumedToBeImplementedException


class IsItemsView(IsMappingView, Protocol[_KeyT, _ValT]):
    def __contains__(self, item: tuple[_KeyT, _ValT]) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[tuple[_KeyT, _ValT]]:
        raise AssumedToBeImplementedException


class IsValuesView(IsMappingView, Protocol[_ValT]):
    def __contains__(self, value: _ValT) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_ValT]:
        raise AssumedToBeImplementedException


class IsMutableMapping(IsMapping[_KeyT, _ValT], Protocol[_KeyT, _ValT]):
    """
    IsMutableMapping is a protocol with the same interface as the abstract class MutableMapping.
    It is the protocol of a generic mutable container for associating key/value pairs.
    """
    def __setitem__(self, key: _KeyT, value: _ValT, /) -> None:
        raise AssumedToBeImplementedException

    def __delitem__(self, key: _KeyT, /) -> None:
        raise AssumedToBeImplementedException

    def pop(self, key: _KeyT, /) -> _ValT:
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised.
        """
        raise AssumedToBeImplementedException

    def popitem(self) -> tuple[_KeyT, _ValT]:
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair
           as a 2-tuple; but raise KeyError if D is empty.
        """
        raise AssumedToBeImplementedException

    def clear(self) -> None:
        """
        D.clear() -> None.  Remove all items from D.
        """
        raise AssumedToBeImplementedException

    @overload
    def update(self, other: SupportsKeysAndGetItem[_KeyT, _ValT], /) -> None:
        raise AssumedToBeImplementedException

    @overload
    def update(self, other: SupportsKeysAndGetItem[_KeyT, _ValT], /, **kwargs: _ValT) -> None:
        raise AssumedToBeImplementedException

    @overload
    def update(self, other: Iterable[tuple[_KeyT, _ValT]], /) -> None:
        raise AssumedToBeImplementedException

    @overload
    def update(self, other: Iterable[tuple[_KeyT, _ValT]], /, **kwargs: _ValT) -> None:
        raise AssumedToBeImplementedException

    @overload
    def update(self, /, **kwargs: _ValT) -> None:
        raise AssumedToBeImplementedException

    def update(self, other: Any = None, /, **kwargs: _ValT) -> None:
        """
        D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k, v in F.items(): D[k] = v
        """
        raise AssumedToBeImplementedException

    def setdefault(self, key: _KeyT, default: _ValT, /) -> _ValT:
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
        raise AssumedToBeImplementedException

    def __or__(self, other: dict[_KeyT, _ValT], /) -> dict[_KeyT, _ValT]:
        raise AssumedToBeImplementedException

    def __ror__(self, other: dict[_KeyT, _ValT], /) -> dict[_KeyT, _ValT]:
        raise AssumedToBeImplementedException

    def __ior__(self, other: Self, /) -> Self:
        raise AssumedToBeImplementedException


class IsDict(IsMutableMapping[_KeyT, _ValT], IsReversible[_KeyT], Protocol[_KeyT, _ValT]):
    """
    IsDict is a protocol with the same interface as the builtin class dict.
    """
    @classmethod
    @overload
    def fromkeys(cls,
                 iterable: Iterable[_KeyT],
                 value: None = None,
                 /) -> 'IsMutableMapping[_KeyT, Any | None]':
        raise AssumedToBeImplementedException

    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_KeyT], value: _ValT, /) -> Self:
        raise AssumedToBeImplementedException

    @classmethod
    def fromkeys(cls,
                 iterable: Iterable[_KeyT],
                 value: _ValT | None = None,
                 /) -> 'IsMutableMapping[_KeyT, Any | None] | Self':
        raise AssumedToBeImplementedException
