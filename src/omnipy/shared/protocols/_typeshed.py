# Modified from the "_typeshed.py.imported" file in the same directory,
# which was imported from the Typeshed (https://github.com/python/typeshed).
#
# Note: Importing SupportsKeysAndGetItem from _typeshed instead of the
#       local copy in typing.py causes basedpyright to enter an infinite
#       loop. Hence, we maintain a local copy of the elements used from
#       _typeshed.
#
# The Typeshed is licensed under the Apache License, Version 2.0 and the
# MIT License. See the LICENSE file in the root of the repository for
# details (https://github.com/python/typeshed/blob/main/LICENSE).
#
# See "_typeshed.py.imported" for more details.

from collections.abc import Iterable
import sys
from typing import Any, Protocol, SupportsFloat, SupportsIndex, SupportsInt

from typing_extensions import TypeAlias, TypeVar

# Utility types for typeshed

_KT = TypeVar('_KT')
_KT_contra = TypeVar('_KT_contra', contravariant=True)
_VT_co = TypeVar('_VT_co', covariant=True)
_T_contra = TypeVar('_T_contra', contravariant=True)


class SupportsBool(Protocol):
    def __bool__(self) -> bool:
        ...


# Comparison protocols
class SupportsDunderLT(Protocol[_T_contra]):
    def __lt__(self, other: _T_contra, /) -> SupportsBool:
        ...


class SupportsDunderGT(Protocol[_T_contra]):
    def __gt__(self, other: _T_contra, /) -> SupportsBool:
        ...


SupportsRichComparison: TypeAlias = SupportsDunderLT[Any] | SupportsDunderGT[Any]
SupportsRichComparisonT = TypeVar(
    'SupportsRichComparisonT', bound=SupportsRichComparison)  # noqa: Y001


class SupportsTrunc(Protocol):
    def __trunc__(self) -> int:
        ...


# Mapping-like protocols


class SupportsGetItem(Protocol[_KT, _VT_co]):
    def __getitem__(self, key: _KT, /) -> _VT_co:
        ...


class SupportsKeysAndGetItem(Protocol[_KT, _VT_co]):
    def keys(self) -> Iterable[_KT]:
        ...

    def __getitem__(self, key: _KT, /) -> _VT_co:
        ...


# @runtime_checkable
class Buffer(Protocol):
    __slots__ = ()

    def __buffer__(self, flags: int, /) -> memoryview:
        ...


# Unfortunately PEP 688 does not allow us to distinguish read-only
# from writable buffers. We use these aliases for readability for now.
# Perhaps a future extension of the buffer protocol will allow us to
# distinguish these cases in the type system.
ReadOnlyBuffer: TypeAlias = Buffer  # stable
# Anything that implements the read-write buffer interface.
WriteableBuffer: TypeAlias = Buffer
# Same as WriteableBuffer, but also includes read-only buffer types (like bytes).
ReadableBuffer: TypeAlias = Buffer  # stable

# Anything that can be passed to the int/float constructors
if sys.version_info >= (3, 14):
    ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex
else:
    ConvertibleToInt: TypeAlias = str | ReadableBuffer | SupportsInt | SupportsIndex | SupportsTrunc
ConvertibleToFloat: TypeAlias = str | ReadableBuffer | SupportsFloat | SupportsIndex
