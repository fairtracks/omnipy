# This stub was imported from the following source:
#   https://github.com/python/typeshed/blob/main/stdlib/_collections_abc.pyi
#
# The original file is part of the Typeshed
# (https://github.com/python/typeshed), imported at revision
# 132ae01fd184883857189406b5f13439c00078e4 (May 20, 2026)
# in line with pyright v1.1.409 / basedpyright v1.39.1.
#
# The Typeshed is licensed under the Apache License, Version 2.0 and the
# MIT License. See the LICENSE file in the root of the repository for
# details (https://github.com/python/typeshed/blob/main/LICENSE).

import sys
from abc import abstractmethod
from types import MappingProxyType
from typing import (  # noqa: Y022,Y038,UP035,Y057
    AbstractSet as Set,
    AsyncGenerator as AsyncGenerator,
    AsyncIterable as AsyncIterable,
    AsyncIterator as AsyncIterator,
    Awaitable as Awaitable,
    ByteString as ByteString,
    Callable as Callable,
    ClassVar,
    Collection as Collection,
    Container as Container,
    Coroutine as Coroutine,
    Generator as Generator,
    Generic,
    Hashable as Hashable,
    ItemsView as ItemsView,
    Iterable as Iterable,
    Iterator as Iterator,
    KeysView as KeysView,
    Mapping as Mapping,
    MappingView as MappingView,
    MutableMapping as MutableMapping,
    MutableSequence as MutableSequence,
    MutableSet as MutableSet,
    Protocol,
    Reversible as Reversible,
    Sequence as Sequence,
    Sized as Sized,
    TypeVar,
    ValuesView as ValuesView,
    final,
    runtime_checkable,
)

__all__ = [
    "Awaitable",
    "Coroutine",
    "AsyncIterable",
    "AsyncIterator",
    "AsyncGenerator",
    "Hashable",
    "Iterable",
    "Iterator",
    "Generator",
    "Reversible",
    "Sized",
    "Container",
    "Callable",
    "Collection",
    "Set",
    "MutableSet",
    "Mapping",
    "MutableMapping",
    "MappingView",
    "KeysView",
    "ItemsView",
    "ValuesView",
    "Sequence",
    "MutableSequence",
]
if sys.version_info < (3, 15):
    __all__ += ["ByteString"]
if sys.version_info >= (3, 12):
    __all__ += ["Buffer"]

_KT_co = TypeVar("_KT_co", covariant=True)  # Key type covariant containers.
_VT_co = TypeVar("_VT_co", covariant=True)  # Value type covariant containers.

@final
class dict_keys(KeysView[_KT_co], Generic[_KT_co, _VT_co]):  # undocumented
    def __eq__(self, value: object, /) -> bool: ...
    def __reversed__(self) -> Iterator[_KT_co]: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    if sys.version_info >= (3, 13):
        def isdisjoint(self, other: Iterable[_KT_co], /) -> bool: ...

    @property
    def mapping(self) -> MappingProxyType[_KT_co, _VT_co]: ...

@final
class dict_values(ValuesView[_VT_co], Generic[_KT_co, _VT_co]):  # undocumented
    def __reversed__(self) -> Iterator[_VT_co]: ...
    @property
    def mapping(self) -> MappingProxyType[_KT_co, _VT_co]: ...

@final
class dict_items(ItemsView[_KT_co, _VT_co]):  # undocumented
    def __eq__(self, value: object, /) -> bool: ...
    def __reversed__(self) -> Iterator[tuple[_KT_co, _VT_co]]: ...
    __hash__: ClassVar[None]  # type: ignore[assignment]
    if sys.version_info >= (3, 13):
        def isdisjoint(self, other: Iterable[tuple[_KT_co, _VT_co]], /) -> bool: ...

    @property
    def mapping(self) -> MappingProxyType[_KT_co, _VT_co]: ...

if sys.version_info >= (3, 12):
    @runtime_checkable
    class Buffer(Protocol):
        __slots__ = ()
        @abstractmethod
        def __buffer__(self, flags: int, /) -> memoryview: ...
