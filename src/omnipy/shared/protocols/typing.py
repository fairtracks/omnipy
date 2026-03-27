# Modified from the "typing.py.imported" file in the same directory,
# which was imported from the Typeshed (https://github.com/python/typeshed).
#
# The Typeshed is licensed under the Apache License, Version 2.0 and the
# MIT License. See the LICENSE file in the root of the repository for
# details (https://github.com/python/typeshed/blob/main/LICENSE).
#
# See "typing.py.imported" for more details.

from __future__ import annotations

from collections.abc import Collection, Iterable, Iterator, Reversible
from types import TracebackType
from typing import AbstractSet, Any, AnyStr, overload, Protocol, runtime_checkable

from typing_extensions import Self, TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols._typeshed import (ReadableBuffer,
                                               SupportsGetItem,
                                               SupportsKeysAndGetItem)

_T = TypeVar('_T')
_T2 = TypeVar('_T2')
_KT = TypeVar('_KT')  # Key type.
_VT = TypeVar('_VT')  # Value type.
_T_co = TypeVar('_T_co', covariant=True)  # Any type covariant containers.
_KT_co = TypeVar('_KT_co', covariant=True)  # Key type covariant containers.
_VT_co = TypeVar('_VT_co', covariant=True)  # Value type covariant containers.


# class Hashable(Protocol, metaclass=ABCMeta):
@runtime_checkable
class IsHashable(Protocol):
    # FIXME: This is special, in that a subclass of a hashable class may not be hashable
    #   (for example, list vs. object). It's not obvious how to represent this. This class
    #   is currently mostly useless for static checking.
    # @abstractmethod
    def __hash__(self) -> int:
        ...


# class Sequence(Reversible[_T_co], Collection[_T_co]):
class IsSequenceNotStrBytes(Reversible[_T_co], Collection[_T_co], Protocol[_T_co]):
    """Protocol with the same interface as the abstract class `typing.Sequence`.

    Note that with no custom handling, as is typically be done in a type
    checker, the `string`, `bytes`, and `bytearray` types will not be
    considered Sequences by this protocol, due to differences in the
    `__contains__` method.
    """
    @overload
    # @abstractmethod
    def __getitem__(self, index: int, /) -> _T_co:
        raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    # def __getitem__(self, index: slice[int | None], /) -> Sequence[_T_co]:
    def __getitem__(self, index: slice, /) -> IsSequenceNotStrBytes[_T_co]:
        raise AssumedToBeImplementedException

    def __getitem__(self, index: int | slice, /) -> _T_co | IsSequenceNotStrBytes[_T_co]:
        raise AssumedToBeImplementedException

    # Mixin methods
    # def index(self, value: Any, start: int = 0, stop: int = ..., /) -> int:

    # Omnipy: start and stop removed to support range as IsSequenceNotStrBytes
    def index(self, value: Any, /) -> int:
        """
        S.index(value, [start, [stop]]) -> integer -- return first index of value.
        Raises ValueError if the value is not present.

        Supporting start and stop arguments is optional, but recommended.
        """
        raise AssumedToBeImplementedException

    def count(self, value: Any, /) -> int:
        """
        S.count(value) -> integer -- return number of occurrences of value
        """
        raise AssumedToBeImplementedException

    def __contains__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_T_co]:
        raise AssumedToBeImplementedException

    def __reversed__(self) -> Iterator[_T_co]:
        raise AssumedToBeImplementedException


# class MutableSequence(Sequence[_T]):
class IsMutableSequence(IsSequenceNotStrBytes[_T], Protocol[_T]):
    """Protocol with the same interface as the abstract class `typing.MutableSequence`.
    """

    # @abstractmethod
    def insert(self, index: int, value: _T, /) -> None:
        """
        S.insert(index, value) -- insert value before index
        """
        raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    def __getitem__(self, index: int, /) -> _T:
        raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    # def __getitem__(self, index: slice[int | None], /) -> MutableSequence[_T]:
    def __getitem__(self, index: slice, /) -> IsMutableSequence[_T]:
        raise AssumedToBeImplementedException

    def __getitem__(self, index: int | slice, /) -> _T | IsMutableSequence[_T_co]:
        raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    def __setitem__(self, index: int, value: _T, /) -> None:
        raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    # def __setitem__(self, index: slice[int | None], value: Iterable[_T], /) -> None:
    def __setitem__(self, index: slice, value: Iterable[_T], /) -> None:
        raise AssumedToBeImplementedException

    def __setitem__(self, index: int | slice, value: _T | Iterable[_T], /) -> None:
        raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    def __delitem__(self, index: int, /) -> None:
        raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    # def __delitem__(self, index: slice[int | None], /) -> None:
    def __delitem__(self, index: slice, /) -> None:
        raise AssumedToBeImplementedException

    def __delitem__(self, index: int | slice, /) -> None:
        raise AssumedToBeImplementedException

    # Mixin methods
    def append(self, value: _T, /) -> None:
        """
        S.append(value) -- append value to the end of the sequence
        """
        raise AssumedToBeImplementedException

    def clear(self) -> None:
        """
        S.clear() -> None -- remove all items from S
        """
        raise AssumedToBeImplementedException

    def extend(self, values: Iterable[_T], /) -> None:
        """
        S.extend(iterable) -- extend sequence by appending elements from the iterable
        """
        raise AssumedToBeImplementedException

    def reverse(self) -> None:
        """
        S.reverse() -- reverse *IN PLACE*
        """
        raise AssumedToBeImplementedException

    def pop(self, index: int = -1, /) -> _T:
        """
        S.pop([index]) -> item -- remove and return item at index (default last).
        Raise IndexError if list is empty or index is out of range.
        """
        raise AssumedToBeImplementedException

    def remove(self, value: _T, /) -> None:
        """
        S.remove(value) -- remove first occurrence of value.
        Raise ValueError if the value is not present.
        """
        raise AssumedToBeImplementedException

    def __iadd__(self, values: Iterable[_T], /) -> Self:
        raise AssumedToBeImplementedException


# class AbstractSet(Collection[_T_co]):
class IsAbstractSet(Collection[_T_co], Protocol[_T_co]):
    """Protocol with the same interface as the abstract class `typing.AbstractSet`.
    """

    # @abstractmethod
    def __contains__(self, x: object, /) -> bool:
        raise AssumedToBeImplementedException

    def _hash(self) -> int:
        raise AssumedToBeImplementedException

    # # Mixin methods
    # @classmethod
    # def _from_iterable(cls, it: Iterable[_S], /) -> IsAbstractSet[_S]:
    #     raise AssumedToBeImplementedException

    def __le__(self, value: AbstractSet[Any], /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, other: AbstractSet[Any], /) -> bool:
        raise AssumedToBeImplementedException

    def __gt__(self, other: AbstractSet[Any], /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, other: AbstractSet[Any], /) -> bool:
        raise AssumedToBeImplementedException

    def __and__(self, other: AbstractSet[Any], /) -> AbstractSet[_T_co]:
        raise AssumedToBeImplementedException

    def __or__(self, other: AbstractSet[_T], /) -> AbstractSet[_T_co | _T]:
        raise AssumedToBeImplementedException

    def __sub__(self, other: AbstractSet[Any], /) -> AbstractSet[_T_co]:
        raise AssumedToBeImplementedException

    def __xor__(self, other: AbstractSet[_T], /) -> AbstractSet[_T_co | _T]:
        raise AssumedToBeImplementedException

    def __eq__(self, other: object, /) -> bool:
        raise AssumedToBeImplementedException

    def isdisjoint(self, other: Iterable[Any], /) -> bool:
        raise AssumedToBeImplementedException


# class MutableSet(AbstractSet[_T]):
class IsMutableSet(IsAbstractSet[_T], Protocol[_T]):
    """Protocol with the same interface as the abstract class `typing.MutableSet`.
    """

    # @abstractmethod
    def add(self, value: _T, /) -> None:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def discard(self, value: _T, /) -> None:
        raise AssumedToBeImplementedException

    # Mixin methods
    def clear(self) -> None:
        raise AssumedToBeImplementedException

    def pop(self) -> _T:
        raise AssumedToBeImplementedException

    def remove(self, value: _T, /) -> None:
        raise AssumedToBeImplementedException

    def __ior__(self, it: AbstractSet[_T], /) -> Self:  # type: ignore[misc, override]
        raise AssumedToBeImplementedException

    def __iand__(self, it: AbstractSet[Any], /) -> IsMutableSet[Any]:  # type: ignore[override]
        raise AssumedToBeImplementedException

    def __ixor__(self, it: AbstractSet[_T], /) -> Self:  # type: ignore[misc, override]
        raise AssumedToBeImplementedException

    def __isub__(self, it: AbstractSet[Any], /) -> IsMutableSet[Any]:  # type: ignore[override]
        raise AssumedToBeImplementedException


# class MappingView(Sized):
class IsMappingView(Protocol):
    """Protocol with the same interface as the abstract class `typing.MappingView`.
    """

    # __slots__ = ("_mapping",)

    # def __init__(self, mapping: IsSized) -> None:
    #     raise AssumedToBeImplementedException  # undocumented

    def __len__(self) -> int:
        raise AssumedToBeImplementedException


# class ItemsView(MappingView, AbstractSet[tuple[_KT_co, _VT_co]], Generic[_KT_co, _VT_co]):
class IsItemsView(  # type: ignore[misc]
        IsMappingView,
        IsAbstractSet[tuple[_KT_co, _VT_co]],
        Protocol[_KT_co, _VT_co],
):
    """Protocol with the same interface as the abstract class `typing.ItemsView`.
    """

    # def __init__(self, mapping: SupportsGetItemViewable[_KT_co, _VT_co]) -> None:
    #     raise AssumedToBeImplementedException  # undocumented

    # @classmethod
    # def _from_iterable(cls, it: Iterable[_S], /) -> set[_S]:  # type: ignore[override]
    #     raise AssumedToBeImplementedException

    def __and__(self, other: Iterable[Any], /) -> set[tuple[_KT_co, _VT_co]]:
        raise AssumedToBeImplementedException

    def __rand__(self, other: Iterable[_T], /) -> set[_T]:
        raise AssumedToBeImplementedException

    def __contains__(self, item: tuple[object, object], /) -> bool:  # type: ignore[override]
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[tuple[_KT_co, _VT_co]]:
        raise AssumedToBeImplementedException

    def __or__(self, other: Iterable[_T], /) -> set[tuple[_KT_co, _VT_co] | _T]:
        raise AssumedToBeImplementedException

    def __ror__(self, other: Iterable[_T], /) -> set[tuple[_KT_co, _VT_co] | _T]:
        raise AssumedToBeImplementedException

    def __sub__(self, other: Iterable[Any], /) -> set[tuple[_KT_co, _VT_co]]:
        raise AssumedToBeImplementedException

    def __rsub__(self, other: Iterable[_T], /) -> set[_T]:
        raise AssumedToBeImplementedException

    def __xor__(self, other: Iterable[_T], /) -> set[tuple[_KT_co, _VT_co] | _T]:
        raise AssumedToBeImplementedException

    def __rxor__(self, other: Iterable[_T], /) -> set[tuple[_KT_co, _VT_co] | _T]:
        raise AssumedToBeImplementedException


# class KeysView(MappingView, AbstractSet[_KT_co]):
class IsKeysView(IsMappingView, IsAbstractSet[_KT_co], Protocol[_KT_co]):  # type: ignore[misc]
    """Protocol with the same interface as the abstract class `typing.KeysView`.
    """

    # def __init__(self, mapping: Viewable[_KT_co]) -> None:
    #     raise AssumedToBeImplementedException  # undocumented

    # @classmethod
    # def _from_iterable(cls, it: Iterable[_S], /) -> set[_S]:  # type: ignore[override]
    #     raise AssumedToBeImplementedException

    def __and__(self, other: Iterable[Any], /) -> set[_KT_co]:
        raise AssumedToBeImplementedException

    def __rand__(self, other: Iterable[_T], /) -> set[_T]:
        raise AssumedToBeImplementedException

    def __contains__(self, key: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_KT_co]:
        raise AssumedToBeImplementedException

    def __or__(self, other: Iterable[_T], /) -> set[_KT_co | _T]:
        raise AssumedToBeImplementedException

    def __ror__(self, other: Iterable[_T], /) -> set[_KT_co | _T]:
        raise AssumedToBeImplementedException

    def __sub__(self, other: Iterable[Any], /) -> set[_KT_co]:
        raise AssumedToBeImplementedException

    def __rsub__(self, other: Iterable[_T2], /) -> set[_T2]:
        raise AssumedToBeImplementedException

    def __xor__(self, other: Iterable[_T], /) -> set[_KT_co | _T]:
        raise AssumedToBeImplementedException

    def __rxor__(self, other: Iterable[_T], /) -> set[_KT_co | _T]:
        raise AssumedToBeImplementedException


# class ValuesView(MappingView, Collection[_VT_co]):
class IsValuesView(IsMappingView, Collection[_VT_co], Protocol[_VT_co]):
    """Protocol with the same interface as the abstract class `typing.ValuesView`.
    """

    # def __init__(self, mapping: SupportsGetItemViewable[Any, _VT_co]) -> None:
    #     raise AssumedToBeImplementedException  # undocumented

    def __contains__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_VT_co]:
        raise AssumedToBeImplementedException


# note for Mapping.get and MutableMapping.pop and MutableMapping.setdefault
# In _collections_abc.py the parameters are positional-or-keyword,
# but dict and types.MappingProxyType (the vast majority of Mapping types)
# don't allow keyword arguments.


# class Mapping(Collection[_KT], Generic[_KT, _VT_co]):
class IsMapping(Collection[_KT], Protocol[_KT, _VT_co]):  # type: ignore[misc]
    """Protocol with the same interface as the abstract class `typing.Mapping`.

    IsMapping is the protocol of a generic container for associating
    key/value pairs.
    """

    # FIXME: We wish the key type could also be covariant, but that doesn't work,
    # see discussion in https://github.com/python/typing/pull/273.
    # @abstractmethod
    def __getitem__(self, key: _KT, /) -> _VT_co:
        raise AssumedToBeImplementedException

    # Mixin methods
    @overload
    def get(self, key: _KT, /) -> _VT_co | None:
        raise AssumedToBeImplementedException

    @overload
    def get(self, key: _KT, default: _VT_co, /) -> _VT_co:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    @overload
    def get(self, key: _KT, default: _T, /) -> _VT_co | _T:
        raise AssumedToBeImplementedException

    def get(self, key: _KT, default: None | _VT_co | _T = None, /) -> _VT_co | _T | None:
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        raise AssumedToBeImplementedException

    #
    # def items(self) -> IsItemsView[_KT, _VT_co]:
    #     """
    #     D.items() -> a set-like object providing a view on D's items
    #     """
    #     raise AssumedToBeImplementedException

    def keys(self) -> IsKeysView[_KT]:
        """
        D.keys() -> a set-like object providing a view on D's keys
        """
        raise AssumedToBeImplementedException

    def values(self) -> IsValuesView[_VT_co]:
        """
        D.values() -> an object providing a view on D's values
        """
        raise AssumedToBeImplementedException

    def __contains__(self, key: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __eq__(self, other: object, /) -> bool:
        raise AssumedToBeImplementedException


# class MutableMapping(Mapping[_KT, _VT]):
class IsMutableMapping(IsMapping[_KT, _VT], Protocol[_KT, _VT]):
    """Protocol with the same interface as the abstract class `typing.MutableMapping`.

    IsMutableMapping is the protocol of a generic mutable container for
    associating key/value pairs.
    """

    # @abstractmethod
    def __setitem__(self, key: _KT, value: _VT, /) -> None:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def __delitem__(self, key: _KT, /) -> None:
        raise AssumedToBeImplementedException

    def clear(self) -> None:
        """
        D.clear() -> None.  Remove all items from D.
        """
        raise AssumedToBeImplementedException

    @overload
    def pop(self, key: _KT, /) -> _VT:
        raise AssumedToBeImplementedException

    @overload
    def pop(self, key: _KT, default: _VT, /) -> _VT:
        raise AssumedToBeImplementedException

    @overload
    def pop(self, key: _KT, default: _T, /) -> _VT | _T:
        raise AssumedToBeImplementedException

    def pop(self, key: _KT, default: None | _VT | _T = None, /) -> _VT | _T | None:
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised.
        """
        raise AssumedToBeImplementedException

    def popitem(self) -> tuple[_KT, _VT]:
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair
           as a 2-tuple; but raise KeyError if D is empty.
        """
        raise AssumedToBeImplementedException

    # This overload should be allowed only if the value type is compatible with None.
    #
    # Keep the following methods in line with MutableMapping.setdefault,
    # modulo positional-only differences:
    # -- collections.OrderedDict.setdefault
    # -- collections.ChainMap.setdefault
    # -- weakref.WeakKeyDictionary.setdefault
    # @overload
    # def setdefault(self: IsMutableMapping[_KT, _T | None],
    #                key: _KT,
    #                default: None = None,
    #                /) -> _T | None:
    #     raise AssumedToBeImplementedException
    #
    # @overload
    def setdefault(self, key: _KT, default: _VT, /) -> _VT:
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
        raise AssumedToBeImplementedException

    # def setdefault(self: IsMutableMapping[_KT, _VT] | IsMutableMapping[_KT, _T | None],
    #                key: _KT,
    #                default: _VT | None = None,
    #                /) -> _VT | _T | None:
    #     raise AssumedToBeImplementedException

    # 'update' used to take a Union, but using overloading is better.
    # The second overloaded type here is a bit too general, because
    # Mapping[tuple[_KT, _VT], W] is a subclass of Iterable[tuple[_KT, _VT]],
    # but will always have the behavior of the first overloaded type
    # at runtime, leading to keys of a mix of types _KT and tuple[_KT, _VT].
    # We don't currently have any way of forcing all Mappings to use
    # the first overload, but by using overloading rather than a Union,
    # mypy will commit to using the first overload when the argument is
    # known to be a Mapping with unknown type parameters, which is closer
    # to the behavior we want. See mypy issue  #1430.
    #
    # Various mapping classes have __ior__ methods that should be kept
    # roughly in line with .update():
    # -- dict.__ior__
    # -- os._Environ.__ior__
    # -- collections.UserDict.__ior__
    # -- collections.ChainMap.__ior__
    # -- peewee.attrdict.__add__
    # -- peewee.attrdict.__iadd__
    # -- weakref.WeakValueDictionary.__ior__
    # -- weakref.WeakKeyDictionary.__ior__
    @overload
    def update(self: SupportsGetItem[_KT, _VT], m: SupportsKeysAndGetItem[_KT, _VT], /) -> None:
        raise AssumedToBeImplementedException

    @overload
    def update(self: SupportsGetItem[str, _VT],
               m: SupportsKeysAndGetItem[str, _VT],
               /,
               **kwargs: _VT) -> None:
        raise AssumedToBeImplementedException

    @overload
    def update(self: SupportsGetItem[_KT, _VT], m: Iterable[tuple[_KT, _VT]], /) -> None:
        raise AssumedToBeImplementedException

    @overload
    def update(self: SupportsGetItem[str, _VT], m: Iterable[tuple[str, _VT]], /,
               **kwargs: _VT) -> None:
        raise AssumedToBeImplementedException

    @overload
    def update(self: SupportsGetItem[str, _VT], /, **kwargs: _VT) -> None:
        raise AssumedToBeImplementedException

    def update(
        self: SupportsGetItem[_KT, _VT] | SupportsGetItem[str, _VT],
        m: (SupportsKeysAndGetItem[_KT, _VT] | SupportsKeysAndGetItem[str, _VT]
            | Iterable[tuple[_KT, _VT]] | Iterable[tuple[str, _VT]] | None) = None,
        /,
        **kwargs: _VT,
    ) -> None:
        """
        D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k, v in F.items(): D[k] = v
        """
        raise AssumedToBeImplementedException


# In stubs, the arguments of the IO class are marked as positional-only.
# This differs from runtime, but better reflects the fact that in reality
# classes deriving from IO use different names for the arguments.
# class IO(Generic[AnyStr]):
class IsIO(Protocol[AnyStr]):
    """Protocol with the same interface as the abstract class `typing.IO`.
    """
    # At runtime these are all abstract properties,
    # but making them abstract in the stub is hugely disruptive, for not much gain.
    # See #8726
    # __slots__ = ()

    @property
    def mode(self) -> str:
        raise AssumedToBeImplementedException

    # Usually str, but may be bytes if a bytes path was passed to open(). See #10737.
    # If PEP 696 becomes available, we may want to use a defaulted TypeVar here.
    @property
    def name(self) -> str | Any:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def close(self) -> None:
        raise AssumedToBeImplementedException

    @property
    def closed(self) -> bool:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def fileno(self) -> int:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def flush(self) -> None:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def isatty(self) -> bool:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def read(self, n: int = -1, /) -> AnyStr:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def readable(self) -> bool:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def readline(self, limit: int = -1, /) -> AnyStr:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def readlines(self, hint: int = -1, /) -> list[AnyStr]:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def seek(self, offset: int, whence: int = 0, /) -> int:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def seekable(self) -> bool:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def tell(self) -> int:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def truncate(self, size: int | None = None, /) -> int:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def writable(self) -> bool:
        raise AssumedToBeImplementedException

    # @abstractmethod
    @overload
    def write(self: IsIO[bytes], s: ReadableBuffer, /) -> int:
        raise AssumedToBeImplementedException

    # @abstractmethod
    @overload
    def write(self, s: AnyStr, /) -> int:
        raise AssumedToBeImplementedException

    def write(self: IsIO[AnyStr] | IsIO[bytes], s: AnyStr | ReadableBuffer, /) -> int:
        raise AssumedToBeImplementedException

    # @abstractmethod
    @overload
    def writelines(self: IsIO[bytes], lines: Iterable[ReadableBuffer], /) -> None:
        raise AssumedToBeImplementedException

    # @abstractmethod
    @overload
    def writelines(self, lines: Iterable[AnyStr], /) -> None:
        raise AssumedToBeImplementedException

    def writelines(
        self: IsIO[AnyStr] | IsIO[bytes],
        lines: Iterable[AnyStr] | Iterable[ReadableBuffer],
        /,
    ) -> None:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def __next__(self) -> AnyStr:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def __iter__(self) -> Iterator[AnyStr]:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def __enter__(self) -> IsIO[AnyStr]:
        raise AssumedToBeImplementedException

    # @abstractmethod
    def __exit__(self,
                 type: type[BaseException] | None,
                 value: BaseException | None,
                 traceback: TracebackType | None,
                 /) -> None:
        raise AssumedToBeImplementedException


# class BinaryIO(IO[bytes]):
class IsBinaryIO(IsIO[bytes], Protocol):
    """Protocol with the same interface as the abstract class `typing.BinaryIO`.
    """

    # __slots__ = ()

    # @abstractmethod
    def __enter__(self) -> IsBinaryIO:
        raise AssumedToBeImplementedException


# class TextIO(IO[str]):
class IsTextIO(IsIO[str], Protocol):
    # See comment regarding the @properties in the `IO` class
    # __slots__ = ()

    @property
    def buffer(self) -> IsBinaryIO:
        raise AssumedToBeImplementedException

    @property
    def encoding(self) -> str:
        raise AssumedToBeImplementedException

    @property
    def errors(self) -> str | None:
        raise AssumedToBeImplementedException

    @property
    def line_buffering(self) -> int:
        raise AssumedToBeImplementedException  # int on PyPy, bool on CPython

    @property
    def newlines(self) -> Any:
        raise AssumedToBeImplementedException  # None, str or tuple

    # @abstractmethod
    def __enter__(self) -> IsTextIO:
        raise AssumedToBeImplementedException
