from abc import abstractmethod
from typing import AbstractSet, Any, Iterable, Iterator, Mapping, overload, Protocol, Sized, TypeVar

_KeyT = TypeVar('_KeyT')
_ValCovT = TypeVar('_ValCovT', covariant=True)


class SupportsKeysAndGetItem(Protocol[_KeyT, _ValCovT]):
    def keys(self) -> Iterable[_KeyT]:
        ...

    def __getitem__(self, __key: _KeyT) -> _ValCovT:
        ...


class IsSet(Protocol):
    """
    IsSet is a protocol with the same interface as the abstract class Set.
    It is the protocol of a finite, iterable container.
    """
    def __le__(self, other: AbstractSet) -> bool:
        ...

    def __lt__(self, other: AbstractSet) -> bool:
        ...

    def __gt__(self, other: AbstractSet) -> bool:
        ...

    def __ge__(self, other: AbstractSet) -> bool:
        ...

    def __eq__(self, other: object) -> bool:
        ...

    def __and__(self, other: Iterable) -> 'IsSet':
        ...

    def __rand__(self, other: Iterable) -> 'IsSet':
        ...

    def isdisjoint(self, other: AbstractSet) -> bool:
        ...

    def __or__(self, other: Iterable) -> 'IsSet':
        ...

    def __ror__(self, other: Iterable) -> 'IsSet':
        ...

    def __sub__(self, other: Iterable) -> 'IsSet':
        ...

    def __rsub__(self, other: Iterable) -> 'IsSet':
        ...

    def __xor__(self, other: Iterable) -> 'IsSet':
        ...

    def __rxor__(self, other: Iterable) -> 'IsSet':
        ...


_ValT = TypeVar('_ValT')


class IsMapping(Protocol[_KeyT, _ValT]):
    """
    IsMapping is a protocol with the same interface as the abstract class Mapping.
    It is the protocol of a generic container for associating key/value pairs.
    """
    @abstractmethod
    def __getitem__(self, key: _KeyT) -> _ValT:
        raise KeyError

    def get(self, key: _KeyT, /) -> _ValT | None:
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        ...

    def __contains__(self, key: _KeyT) -> bool:
        ...

    def keys(self) -> 'IsKeysView[_KeyT]':
        """
        D.keys() -> a set-like object providing a view on D's keys
        """
        ...

    def items(self) -> 'IsItemsView[_KeyT, _ValT]':
        """
        D.items() -> a set-like object providing a view on D's items
        """
        ...

    def values(self) -> 'IsValuesView[_ValT]':
        """
        D.values() -> an object providing a view on D's values
        """
        ...

    def __eq__(self, other: object) -> bool:
        ...


class IsMappingView(Sized, Protocol):
    def __len__(self) -> int:
        ...

    def __repr__(self) -> str:
        ...


class IsKeysView(IsMappingView, Protocol[_KeyT]):
    def __contains__(self, key: _KeyT) -> bool:
        ...

    def __iter__(self) -> Iterator[_KeyT]:
        ...


class IsItemsView(IsMappingView, Protocol[_KeyT, _ValT]):
    def __contains__(self, item: tuple[_KeyT, _ValT]) -> bool:
        ...

    def __iter__(self) -> Iterator[tuple[_KeyT, _ValT]]:
        ...


class IsValuesView(IsMappingView, Protocol[_ValT]):
    def __contains__(self, value: _ValT) -> bool:
        ...

    def __iter__(self) -> Iterator[_ValT]:
        ...


class IsMutableMapping(IsMapping[_KeyT, _ValT], Protocol[_KeyT, _ValT]):
    """
    IsMutableMapping is a protocol with the same interface as the abstract class MutableMapping.
    It is the protocol of a generic mutable container for associating key/value pairs.
    """
    def __setitem__(
        self,
        selector: str | int | slice | Iterable[str | int],
        data_obj: _ValT | Mapping[str, _ValT] | Iterable[_ValT],
    ) -> None:
        ...

    def __delitem__(self, key: _KeyT) -> None:
        ...

    def pop(self, key: _KeyT, /) -> _ValT:
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised.
        """
        ...

    def popitem(self) -> tuple[_KeyT, _ValT]:
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair
           as a 2-tuple; but raise KeyError if D is empty.
        """
        ...

    def clear(self) -> None:
        """
        D.clear() -> None.  Remove all items from D.
        """
        ...

    @overload
    def update(self, other: SupportsKeysAndGetItem[_KeyT, _ValT], /, **kwargs: _ValT) -> None:
        ...

    @overload
    def update(self, other: Iterable[tuple[_KeyT, _ValT]], /, **kwargs: _ValT) -> None:
        ...

    @overload
    def update(self, /, **kwargs: _ValT) -> None:
        ...

    def update(self, other: Any = None, /, **kwargs: _ValT) -> None:
        """
        D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k, v in F.items(): D[k] = v
        """
        ...

    def setdefault(self, key: _KeyT, default: _ValT, /):
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
        ...
