from abc import abstractmethod
from typing import AbstractSet, Any, Iterable, Iterator, Mapping, overload, Protocol, Sized

from omnipy.shared.protocols.data import KeyT, ValCoT, ValT


class SupportsKeysAndGetItem(Protocol[KeyT, ValCoT]):
    def keys(self) -> Iterable[KeyT]:
        ...

    def __getitem__(self, __key: KeyT) -> ValCoT:
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


class IsMapping(Protocol[KeyT, ValT]):
    """
    IsMapping is a protocol with the same interface as the abstract class Mapping.
    It is the protocol of a generic container for associating key/value pairs.
    """
    @abstractmethod
    def __getitem__(self, key: KeyT) -> ValT:
        raise KeyError

    def get(self, key: KeyT, /) -> ValT | None:
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        ...

    def __contains__(self, key: KeyT) -> bool:
        ...

    def keys(self) -> 'IsKeysView[KeyT]':
        """
        D.keys() -> a set-like object providing a view on D's keys
        """
        ...

    def items(self) -> 'IsItemsView[KeyT, ValT]':
        """
        D.items() -> a set-like object providing a view on D's items
        """
        ...

    def values(self) -> 'IsValuesView[ValT]':
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


class IsKeysView(IsMappingView, Protocol[KeyT]):
    def __contains__(self, key: KeyT) -> bool:
        ...

    def __iter__(self) -> Iterator[KeyT]:
        ...


class IsItemsView(IsMappingView, Protocol[KeyT, ValT]):
    def __contains__(self, item: tuple[KeyT, ValT]) -> bool:
        ...

    def __iter__(self) -> Iterator[tuple[KeyT, ValT]]:
        ...


class IsValuesView(IsMappingView, Protocol[ValT]):
    def __contains__(self, value: ValT) -> bool:
        ...

    def __iter__(self) -> Iterator[ValT]:
        ...


class IsMutableMapping(IsMapping[KeyT, ValT], Protocol[KeyT, ValT]):
    """
    IsMutableMapping is a protocol with the same interface as the abstract class MutableMapping.
    It is the protocol of a generic mutable container for associating key/value pairs.
    """
    def __setitem__(
        self,
        selector: str | int | slice | Iterable[str | int],
        data_obj: ValT | Mapping[str, ValT] | Iterable[ValT],
    ) -> None:
        ...

    def __delitem__(self, key: KeyT) -> None:
        ...

    def pop(self, key: KeyT, /) -> ValT:
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised.
        """
        ...

    def popitem(self) -> tuple[KeyT, ValT]:
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
    def update(self, other: SupportsKeysAndGetItem[KeyT, ValT], /, **kwargs: ValT) -> None:
        ...

    @overload
    def update(self, other: Iterable[tuple[KeyT, ValT]], /, **kwargs: ValT) -> None:
        ...

    @overload
    def update(self, /, **kwargs: ValT) -> None:
        ...

    def update(self, other: Any = None, /, **kwargs: ValT) -> None:
        """
        D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k, v in F.items(): D[k] = v
        """
        ...

    def setdefault(self, key: KeyT, default: ValT, /):
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
        ...
