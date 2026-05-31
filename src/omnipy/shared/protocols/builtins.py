# Modified from the "builtins.pyi" file in the `_typeshed_import` directory,
# which was imported from the Typeshed (https://github.com/python/typeshed).
#
# The Typeshed is licensed under the Apache License, Version 2.0 and the
# MIT License. See the LICENSE file in the root of the repository for
# details (https://github.com/python/typeshed/blob/main/LICENSE).
#
# See "builtins.pyi" for more details.

# flake8: noqa
# isort: skip_file

"""Builtin-compatible protocol definitions used by Omnipy typing."""

from __future__ import annotations

# import _ast
# import _sitebuiltins
# import _typeshed
import sys
# import types
# from _collections_abc import dict_items, dict_keys, dict_values
# from _typeshed import (
#     AnnotationForm,
#     ConvertibleToFloat,
#     ConvertibleToInt,
#     FileDescriptorOrPath,
#     OpenBinaryMode,
#     OpenBinaryModeReading,
#     OpenBinaryModeUpdating,
#     OpenBinaryModeWriting,
#     OpenTextMode,
#     ReadableBuffer,
#     SupportsAdd,
#     SupportsAiter,
#     SupportsAnext,
#     SupportsDivMod,
#     SupportsFlush,
#     SupportsIter,
#     SupportsKeysAndGetItem,
#     SupportsLenAndGetItem,
#     SupportsNext,
#     SupportsRAdd,
#     SupportsRDivMod,
#     SupportsRichComparison,
#     SupportsRichComparisonT,
#     SupportsWrite,
# )
# from collections.abc import Awaitable, Callable, Iterable, Iterator, MutableSet, Reversible, Set as AbstractSet, Sized
from collections.abc import Callable, Iterable, Iterator, Set as AbstractSet
# from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
# from os import PathLike
# from types import CellType, CodeType, EllipsisType, GenericAlias, NotImplementedType, TracebackType

# mypy crashes if any of {ByteString, Sequence, MutableSequence, Mapping, MutableMapping}
# are imported from collections.abc in builtins.pyi
from typing import (  # noqa: Y022,UP035
    # IO,
    Any,
    # BinaryIO,
    ClassVar,
    # Concatenate,
    # Final,
    # Generic,
    # Mapping,
    # MutableMapping,
    # MutableSequence,
    # ParamSpec,
    Protocol,
    # Sequence,
    # SupportsAbs,
    SupportsBytes,
    SupportsComplex,
    SupportsFloat,
    SupportsIndex,
    TypeAlias,
    # TypeGuard,
    # TypeVar,
    # final,
    overload,
    # type_check_only,
)

# we can't import `Literal` from typing or mypy crashes: see #11247
# from typing_extensions import Literal, LiteralString, Self, TypeIs, TypeVarTuple, deprecated, disjoint_base  # noqa: Y023, UP035
from typing_extensions import Literal, LiteralString, Self, deprecated, TypeVar

# if sys.version_info >= (3, 14):
#     from _typeshed import AnnotateFunc

from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols._collections_abc import IsDictItems, IsDictKeys, IsDictValues
from omnipy.shared.protocols._typeshed import (ReadableBuffer, SupportsKeysAndGetItem, SupportsRichComparison, SupportsRichComparisonT)
from omnipy.shared.protocols.typing import (IsAbstractSet, IsMutableMapping, IsMutableSequence, IsMutableSet, IsItemSequence)

_T = TypeVar("_T")
# _I = TypeVar("_I", default=int)
_T_co = TypeVar("_T_co", covariant=True)
# _T_contra = TypeVar("_T_contra", contravariant=True)
# _R_co = TypeVar("_R_co", covariant=True)
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")
_S = TypeVar("_S")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
# _T3 = TypeVar("_T3")
# _T4 = TypeVar("_T4")
# _T5 = TypeVar("_T5")
# _SupportsNextT_co = TypeVar("_SupportsNextT_co", bound=SupportsNext[Any], covariant=True)
# _SupportsAnextT_co = TypeVar("_SupportsAnextT_co", bound=SupportsAnext[Any], covariant=True)
# _AwaitableT = TypeVar("_AwaitableT", bound=Awaitable[Any])
# _AwaitableT_co = TypeVar("_AwaitableT_co", bound=Awaitable[Any], covariant=True)
# _P = ParamSpec("_P")

# # Type variables for slice
# _StartT_co = TypeVar("_StartT_co", covariant=True, default=Any)  # slice -> slice[Any, Any, Any]
# _StopT_co = TypeVar("_StopT_co", covariant=True, default=_StartT_co)  #  slice[A] -> slice[A, A, A]
# NOTE: step could differ from start and stop, (e.g. datetime/timedelta)l
#   the default (start|stop) is chosen to cater to the most common case of int/index slices.
# # FIXME: https://github.com/python/typing/issues/213 (replace step=start|stop with step=start&stop)
# _StepT_co = TypeVar("_StepT_co", covariant=True, default=_StartT_co | _StopT_co)  #  slice[A,B] -> slice[A, B, A|B]

# @disjoint_base
# class object:
#     __doc__: str | None
#     __dict__: dict[str, Any]
#     __module__: str
#     __annotations__: dict[str, Any]
# 
#     @property
#     def __class__(self) -> type[Self]: ...
#     @__class__.setter
#     def __class__(self, type: type[Self], /) -> None: ...
# 
#     def __init__(self) -> None: ...
#     def __new__(cls) -> Self: ...
#     # N.B. `object.__setattr__` and `object.__delattr__` are heavily special-cased by type checkers.
#     # Overriding them in subclasses has different semantics, even if the override has an identical signature.
#     def __setattr__(self, name: str, value: Any, /) -> None: ...
#     def __delattr__(self, name: str, /) -> None: ...
#     def __eq__(self, value: object, /) -> bool: ...
#     def __ne__(self, value: object, /) -> bool: ...
#     def __str__(self) -> str: ...  # noqa: Y029
#     def __repr__(self) -> str: ...  # noqa: Y029
#     def __hash__(self) -> int: ...
#     def __format__(self, format_spec: str, /) -> str: ...
#     def __getattribute__(self, name: str, /) -> Any: ...
#     def __sizeof__(self) -> int: ...
#     # return type of pickle methods is rather hard to express in the current type system
#     # see #6661 and https://docs.python.org/3/library/pickle.html#object.__reduce__
#     def __reduce__(self) -> str | tuple[Any, ...]: ...
#     def __reduce_ex__(self, protocol: SupportsIndex, /) -> str | tuple[Any, ...]: ...
#     if sys.version_info >= (3, 11):
#         def __getstate__(self) -> object: ...
# 
#     def __dir__(self) -> Iterable[str]: ...
#     def __init_subclass__(cls) -> None: ...
#     @classmethod
#     def __subclasshook__(cls, subclass: type, /) -> bool: ...
# 
# @disjoint_base
# class staticmethod(Generic[_P, _R_co]):
#     __name__: str
#     __qualname__: str
#     @property
#     def __func__(self) -> Callable[_P, _R_co]: ...
#     @property
#     def __isabstractmethod__(self) -> bool: ...
#     def __init__(self, f: Callable[_P, _R_co], /) -> None: ...
# 
#     @overload
#     def __get__(self, instance: None, owner: type, /) -> Callable[_P, _R_co]: ...
#     @overload
#     def __get__(self, instance: _T, owner: type[_T] | None = None, /) -> Callable[_P, _R_co]: ...
# 
#     @property
#     def __wrapped__(self) -> Callable[_P, _R_co]: ...
#     def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R_co: ...
#     if sys.version_info >= (3, 14):
#         def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...
#         __annotate__: AnnotateFunc | None
# 
# @disjoint_base
# class classmethod(Generic[_T, _P, _R_co]):
#     __name__: str
#     __qualname__: str
#     @property
#     def __func__(self) -> Callable[Concatenate[type[_T], _P], _R_co]: ...
#     @property
#     def __isabstractmethod__(self) -> bool: ...
#     def __init__(self, f: Callable[Concatenate[type[_T], _P], _R_co], /) -> None: ...
# 
#     @overload
#     def __get__(self, instance: _T, owner: type[_T] | None = None, /) -> Callable[_P, _R_co]: ...
#     @overload
#     def __get__(self, instance: None, owner: type[_T], /) -> Callable[_P, _R_co]: ...
# 
#     @property
#     def __wrapped__(self) -> Callable[Concatenate[type[_T], _P], _R_co]: ...
#     if sys.version_info >= (3, 14):
#         def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...
#         __annotate__: AnnotateFunc | None
# 
# @disjoint_base
# class type:
#     # object.__base__ is None. Otherwise, it would be a type.
#     @property
#     def __base__(self) -> type | None: ...
#     __bases__: tuple[type, ...]
#     @property
#     def __basicsize__(self) -> int: ...
#     # type.__dict__ is read-only at runtime, but that can't be expressed currently.
#     # See https://github.com/python/typeshed/issues/11033 for a discussion.
#     __dict__: Final[types.MappingProxyType[str, Any]]  # type: ignore[assignment]
#     @property
#     def __dictoffset__(self) -> int: ...
#     @property
#     def __flags__(self) -> int: ...
#     @property
#     def __itemsize__(self) -> int: ...
#     __module__: str
#     @property
#     def __mro__(self) -> tuple[type, ...]: ...
#     __name__: str
#     __qualname__: str
#     @property
#     def __text_signature__(self) -> str | None: ...
#     @property
#     def __weakrefoffset__(self) -> int: ...
# 
#     @overload
#     def __init__(self, o: object, /) -> None: ...
#     @overload
#     def __init__(self, name: str, bases: tuple[type, ...], dict: dict[str, Any], /, **kwds: Any) -> None: ...
# 
#     @overload
#     def __new__(cls, o: object, /) -> type: ...
#     @overload
#     def __new__(
#         cls: type[_typeshed.Self], name: str, bases: tuple[type, ...], namespace: dict[str, Any], /, **kwds: Any
#     ) -> _typeshed.Self: ...
# 
#     def __call__(self, *args: Any, **kwds: Any) -> Any: ...
#     def __subclasses__(self: _typeshed.Self) -> list[_typeshed.Self]: ...
#     # Note: the documentation doesn't specify what the return type is, the standard
#     # implementation seems to be returning a list.
#     def mro(self) -> list[type]: ...
#     def __instancecheck__(self, instance: Any, /) -> bool: ...
#     def __subclasscheck__(self, subclass: type, /) -> bool: ...
#     @classmethod
#     def __prepare__(metacls, name: str, bases: tuple[type, ...], /, **kwds: Any) -> MutableMapping[str, object]: ...
#     # `int | str` produces an instance of `UnionType`, but `int | int` produces an instance of `type`,
#     # and `abc.ABC | abc.ABC` produces an instance of `abc.ABCMeta`.
#     def __or__(self: _typeshed.Self, value: Any, /) -> types.UnionType | _typeshed.Self: ...
#     def __ror__(self: _typeshed.Self, value: Any, /) -> types.UnionType | _typeshed.Self: ...
#     if sys.version_info >= (3, 12):
#         __type_params__: tuple[TypeVar | ParamSpec | TypeVarTuple, ...]
#     __annotations__: dict[str, AnnotationForm]
#     if sys.version_info >= (3, 14):
#         __annotate__: AnnotateFunc | None
# 
# @disjoint_base
# class super:
#     @overload
#     def __init__(self, t: Any, obj: Any, /) -> None: ...
#     @overload
#     def __init__(self, t: Any, /) -> None: ...
#     @overload
#     def __init__(self) -> None: ...

_PositiveInteger: TypeAlias = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
_NegativeInteger: TypeAlias = Literal[-1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20]
# _LiteralInteger = _PositiveInteger | _NegativeInteger | Literal[0]  # noqa: Y026  # TODO: Use TypeAlias once mypy bugs are fixed

# @disjoint_base
# class int:

# TODO: Auto-generate docstrings for stdlib-mirroring protocol methods
#
# Most method stubs in this file (IsStr.capitalize, IsStr.casefold, IsList.sort,
# IsDict.get, etc.) mirror Python stdlib with identical signatures. Rather than
# hand-writing docstrings that duplicate CPython docs, investigate whether
# docstrings could be generated statically (e.g. via ast/token inspection of
# typeshed stubs) or dynamically (e.g. at import time from the real stdlib
# classes).  See also protocols/content.py, protocols/types.py and
# protocols/typing.py for similar stdlib-derived stubs.
#

class IsInt(Protocol):
    """Protocol for the subset of built-in ``int`` behavior used by Omnipy typing."""

    # @overload
    # def __new__(cls, x: ConvertibleToInt = 0, /) -> Self: ...
    # @overload
    # def __new__(cls, x: str | bytes | bytearray, /, base: SupportsIndex) -> Self: ...

    def as_integer_ratio(self) -> tuple[int, Literal[1]]: raise AssumedToBeImplementedException
    @property
    def real(self) -> int: raise AssumedToBeImplementedException
    @property
    def imag(self) -> Literal[0]: raise AssumedToBeImplementedException
    @property
    def numerator(self) -> int: raise AssumedToBeImplementedException
    @property
    def denominator(self) -> Literal[1]: raise AssumedToBeImplementedException
    def conjugate(self) -> int: raise AssumedToBeImplementedException
    def bit_length(self) -> int: raise AssumedToBeImplementedException
    def bit_count(self) -> int: raise AssumedToBeImplementedException

    if sys.version_info >= (3, 11):
        def to_bytes(
            self, length: SupportsIndex = 1, byteorder: Literal["little", "big"] = "big", *, signed: bool = False
        ) -> bytes: raise AssumedToBeImplementedException
        @classmethod
        def from_bytes(
            cls,
            bytes: Iterable[SupportsIndex] | SupportsBytes | ReadableBuffer,
            byteorder: Literal["little", "big"] = "big",
            *,
            signed: bool = False,
        ) -> Self: raise AssumedToBeImplementedException
    else:
        def to_bytes(self, length: SupportsIndex, byteorder: Literal["little", "big"], *, signed: bool = False) -> bytes: raise AssumedToBeImplementedException
        @classmethod
        def from_bytes(
            cls,
            bytes: Iterable[SupportsIndex] | SupportsBytes | ReadableBuffer,
            byteorder: Literal["little", "big"],
            *, 
            signed: bool = False,
        ) -> Self: raise AssumedToBeImplementedException

    if sys.version_info >= (3, 12):
        def is_integer(self) -> Literal[True]: raise AssumedToBeImplementedException

    def __add__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __sub__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __mul__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __floordiv__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __truediv__(self, value: int, /) -> float: raise AssumedToBeImplementedException
    def __mod__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __divmod__(self, value: int, /) -> tuple[int, int]: raise AssumedToBeImplementedException
    def __radd__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rsub__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rmul__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rfloordiv__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rtruediv__(self, value: int, /) -> float: raise AssumedToBeImplementedException
    def __rmod__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rdivmod__(self, value: int, /) -> tuple[int, int]: raise AssumedToBeImplementedException

    @overload
    def __pow__(self, x: Literal[0], /) -> Literal[1]: raise AssumedToBeImplementedException
    @overload
    def __pow__(self, value: Literal[0], mod: None, /) -> Literal[1]: raise AssumedToBeImplementedException
    @overload
    def __pow__(self, value: _PositiveInteger, mod: None = None, /) -> int: raise AssumedToBeImplementedException
    @overload
    def __pow__(self, value: _NegativeInteger, mod: None = None, /) -> float: raise AssumedToBeImplementedException
    # positive __value -> int; negative __value -> float
    # return type must be Any as `int | float` causes too many false-positive errors
    @overload
    def __pow__(self, value: int, mod: None = None, /) -> Any: raise AssumedToBeImplementedException
    @overload
    def __pow__(self, value: int, mod: int, /) -> int: raise AssumedToBeImplementedException
    def __pow__(self, value: int, mod: int | None = None, /) -> int | float: raise AssumedToBeImplementedException
    
    def __rpow__(self, value: int, mod: int | None = None, /) -> Any: raise AssumedToBeImplementedException
    def __and__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __or__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __xor__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __lshift__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rshift__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rand__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __ror__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rxor__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rlshift__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rrshift__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __neg__(self) -> int: raise AssumedToBeImplementedException
    def __pos__(self) -> int: raise AssumedToBeImplementedException
    def __invert__(self) -> int: raise AssumedToBeImplementedException
    def __trunc__(self) -> int: raise AssumedToBeImplementedException
    def __ceil__(self) -> int: raise AssumedToBeImplementedException
    def __floor__(self) -> int: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 14):
        def __round__(self, ndigits: SupportsIndex | None = None, /) -> int: raise AssumedToBeImplementedException
    else:
        # def __round__(self, ndigits: SupportsIndex = ..., /) -> int:
        def __round__(self, ndigits: SupportsIndex = 0, /) -> int: raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[int]: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __ne__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __lt__(self, value: int, /) -> bool: raise AssumedToBeImplementedException
    def __le__(self, value: int, /) -> bool: raise AssumedToBeImplementedException
    def __gt__(self, value: int, /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: int, /) -> bool: raise AssumedToBeImplementedException
    def __float__(self) -> float: raise AssumedToBeImplementedException
    def __int__(self) -> int: raise AssumedToBeImplementedException
    def __abs__(self) -> int: raise AssumedToBeImplementedException
    def __hash__(self) -> int: raise AssumedToBeImplementedException
    def __bool__(self) -> bool: raise AssumedToBeImplementedException
    def __index__(self) -> int: raise AssumedToBeImplementedException
    def __format__(self, format_spec: str, /) -> str: raise AssumedToBeImplementedException

# @disjoint_base
# class float:
class IsFloat(Protocol):
    """Define the ``IsFloat`` interface.
    """
    # def __new__(cls, x: ConvertibleToFloat = 0, /) -> Self: ...
    def as_integer_ratio(self) -> tuple[int, int]: raise AssumedToBeImplementedException
    def hex(self) -> str: raise AssumedToBeImplementedException
    def is_integer(self) -> bool: raise AssumedToBeImplementedException
    @classmethod
    def fromhex(cls, string: str, /) -> Self: raise AssumedToBeImplementedException
    @property
    def real(self) -> float: raise AssumedToBeImplementedException
    @property
    def imag(self) -> float: raise AssumedToBeImplementedException
    def conjugate(self) -> float: raise AssumedToBeImplementedException
    def __add__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __sub__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __mul__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __floordiv__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __truediv__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __mod__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __divmod__(self, value: float, /) -> tuple[float, float]: raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: int, mod: None = None, /) -> float: raise AssumedToBeImplementedException
    # positive __value -> float; negative __value -> complex
    # return type must be Any as `float | complex` causes too many false-positive errors
    @overload
    def __pow__(self, value: float, mod: None = None, /) -> Any: raise AssumedToBeImplementedException
    def __pow__(self, value: int | float, mod: None = None, /) -> Any: raise AssumedToBeImplementedException

    def __radd__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __rsub__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __rmul__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __rfloordiv__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __rtruediv__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __rmod__(self, value: float, /) -> float: raise AssumedToBeImplementedException
    def __rdivmod__(self, value: float, /) -> tuple[float, float]: raise AssumedToBeImplementedException

    @overload
    def __rpow__(self, value: _PositiveInteger, mod: None = None, /) -> float: raise AssumedToBeImplementedException
    @overload
    def __rpow__(self, value: _NegativeInteger, mod: None = None, /) -> complex: raise AssumedToBeImplementedException
    # Returning `complex` for the general case gives too many false-positive errors.
    @overload
    def __rpow__(self, value: float, mod: None = None, /) -> Any: raise AssumedToBeImplementedException
    def __rpow__(self, value: int | float, mod: None = None, /) -> Any: raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[float]: raise AssumedToBeImplementedException
    def __trunc__(self) -> int: raise AssumedToBeImplementedException
    def __ceil__(self) -> int: raise AssumedToBeImplementedException
    def __floor__(self) -> int: raise AssumedToBeImplementedException

    @overload
    def __round__(self, ndigits: None = None, /) -> int: raise AssumedToBeImplementedException
    @overload
    def __round__(self, ndigits: SupportsIndex, /) -> float: raise AssumedToBeImplementedException
    def __round__(self, ndigits: SupportsIndex | None = None, /) -> float | int: raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __ne__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __lt__(self, value: float, /) -> bool: raise AssumedToBeImplementedException
    def __le__(self, value: float, /) -> bool: raise AssumedToBeImplementedException
    def __gt__(self, value: float, /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: float, /) -> bool: raise AssumedToBeImplementedException
    def __neg__(self) -> float: raise AssumedToBeImplementedException
    def __pos__(self) -> float: raise AssumedToBeImplementedException
    def __int__(self) -> int: raise AssumedToBeImplementedException
    def __float__(self) -> float: raise AssumedToBeImplementedException
    def __abs__(self) -> float: raise AssumedToBeImplementedException
    def __hash__(self) -> int: raise AssumedToBeImplementedException
    def __bool__(self) -> bool: raise AssumedToBeImplementedException
    def __format__(self, format_spec: str, /) -> str: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 14):
        @classmethod
        def from_number(cls, number: float | SupportsIndex | SupportsFloat, /) -> Self: raise AssumedToBeImplementedException

# @disjoint_base
# class complex:
class IsComplex(Protocol):
    """Protocol for the subset of built-in ``complex`` behavior used by Omnipy typing."""
    # # Python doesn't currently accept SupportsComplex for the second argument
    # @overload
    # def __new__(
    #     cls,
    #     real: complex | SupportsComplex | SupportsFloat | SupportsIndex = 0,
    #     imag: complex | SupportsFloat | SupportsIndex = 0,
    # ) -> Self: ...
    # @overload
    # def __new__(cls, real: (str | SupportsComplex | SupportsFloat | SupportsIndex | complex)) -> Self: ...

    @property
    def real(self) -> float: raise AssumedToBeImplementedException
    @property
    def imag(self) -> float: raise AssumedToBeImplementedException
    def conjugate(self) -> complex: raise AssumedToBeImplementedException
    def __add__(self, value: complex, /) -> complex: raise AssumedToBeImplementedException
    def __sub__(self, value: complex, /) -> complex: raise AssumedToBeImplementedException
    def __mul__(self, value: complex, /) -> complex: raise AssumedToBeImplementedException
    def __pow__(self, value: complex, mod: None = None, /) -> complex: raise AssumedToBeImplementedException
    def __truediv__(self, value: complex, /) -> complex: raise AssumedToBeImplementedException
    def __radd__(self, value: complex, /) -> complex: raise AssumedToBeImplementedException
    def __rsub__(self, value: complex, /) -> complex: raise AssumedToBeImplementedException
    def __rmul__(self, value: complex, /) -> complex: raise AssumedToBeImplementedException
    def __rpow__(self, value: complex, mod: None = None, /) -> complex: raise AssumedToBeImplementedException
    def __rtruediv__(self, value: complex, /) -> complex: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __ne__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __neg__(self) -> complex: raise AssumedToBeImplementedException
    def __pos__(self) -> complex: raise AssumedToBeImplementedException
    def __abs__(self) -> float: raise AssumedToBeImplementedException
    def __hash__(self) -> int: raise AssumedToBeImplementedException
    def __bool__(self) -> bool: raise AssumedToBeImplementedException
    def __format__(self, format_spec: str, /) -> str: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 11):
        def __complex__(self) -> complex: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 14):
        @classmethod
        def from_number(cls, number: complex | SupportsComplex | SupportsFloat | SupportsIndex, /) -> Self: raise AssumedToBeImplementedException

# @type_check_only
class _FormatMapMapping(Protocol):
    def __getitem__(self, key: str, /) -> Any: raise AssumedToBeImplementedException

# @type_check_only
class _TranslateTable(Protocol):
    def __getitem__(self, key: int, /) -> str | int | None: raise AssumedToBeImplementedException

# @disjoint_base
# class str(Sequence[str]):
class IsStr(IsItemSequence[str], Protocol):
    """Protocol with the same interface as the builtin class `str`.
    """
    # @overload
    # def __new__(cls, object: object = "") -> Self: ...
    # @overload
    # def __new__(cls, object: ReadableBuffer, encoding: str = "utf-8", errors: str = "strict") -> Self: ...

    @overload
    def capitalize(self: LiteralString) -> LiteralString: raise AssumedToBeImplementedException  # type: ignore [misc]
    @overload
    # def capitalize(self) -> str: ...  # type: ignore[misc]
    def capitalize(self) -> Self: raise AssumedToBeImplementedException
    def capitalize(self) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def casefold(self: LiteralString) -> LiteralString: raise AssumedToBeImplementedException  # type: ignore [misc]
    @overload
    # def casefold(self) -> str: ...  # type: ignore[misc]
    def casefold(self) -> Self: raise AssumedToBeImplementedException
    def casefold(self) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def center(self: LiteralString, width: SupportsIndex, fillchar: LiteralString = " ", /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def center(self, width: SupportsIndex, fillchar: str = " ", /) -> str: ...  # type: ignore[misc]
    def center(self, width: SupportsIndex, fillchar: str = " ", /) -> Self: raise AssumedToBeImplementedException  # type: ignore[misc]
    def center(self, width: SupportsIndex, fillchar: str | LiteralString = ' ', /) -> Self | LiteralString: raise AssumedToBeImplementedException

    def count(self, sub: str, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> int: raise AssumedToBeImplementedException
    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes: raise AssumedToBeImplementedException
    def endswith(
        self, suffix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> bool: raise AssumedToBeImplementedException

    @overload
    def expandtabs(self: LiteralString, tabsize: SupportsIndex = 8) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def expandtabs(self, tabsize: SupportsIndex = 8) -> str: ...  # type: ignore[misc]
    def expandtabs(self, tabsize: SupportsIndex = 8) -> Self: raise AssumedToBeImplementedException
    def expandtabs(self, tabsize: SupportsIndex = 8) -> Self | LiteralString: raise AssumedToBeImplementedException

    def find(self, sub: str, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> int: raise AssumedToBeImplementedException

    @overload
    def format(self: LiteralString, *args: LiteralString, **kwargs: LiteralString) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def format(self, *args: object, **kwargs: object) -> str: ...
    def format(self, *args: object, **kwargs: object) -> Self: raise AssumedToBeImplementedException
    def format(self, *args: object | LiteralString, **kwargs: object | LiteralString) -> Self | LiteralString: raise AssumedToBeImplementedException

    # def format_map(self, mapping: _FormatMapMapping, /) -> str: ...
    def format_map(self, mapping: _FormatMapMapping, /) -> Self: raise AssumedToBeImplementedException
    
    def index(self, sub: str, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> int: raise AssumedToBeImplementedException
    def isalnum(self) -> bool: raise AssumedToBeImplementedException
    def isalpha(self) -> bool: raise AssumedToBeImplementedException
    def isascii(self) -> bool: raise AssumedToBeImplementedException
    def isdecimal(self) -> bool: raise AssumedToBeImplementedException
    def isdigit(self) -> bool: raise AssumedToBeImplementedException
    def isidentifier(self) -> bool: raise AssumedToBeImplementedException
    def islower(self) -> bool: raise AssumedToBeImplementedException
    def isnumeric(self) -> bool: raise AssumedToBeImplementedException
    def isprintable(self) -> bool: raise AssumedToBeImplementedException
    def isspace(self) -> bool: raise AssumedToBeImplementedException
    def istitle(self) -> bool: raise AssumedToBeImplementedException
    def isupper(self) -> bool: raise AssumedToBeImplementedException

    @overload
    def join(self: LiteralString, iterable: Iterable[LiteralString], /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def join(self, iterable: Iterable[str], /) -> str: ...  # type: ignore[misc]
    def join(self, iterable: Iterable[str], /) -> Self: raise AssumedToBeImplementedException
    def join(self, iterable: Iterable[str] | Iterable[LiteralString], /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def ljust(self: LiteralString, width: SupportsIndex, fillchar: LiteralString = " ", /) -> LiteralString: ...
    @overload
    # def ljust(self, width: SupportsIndex, fillchar: str = " ", /) -> str: ...  # type: ignore[misc]
    def ljust(self, width: SupportsIndex, fillchar: str = " ", /) -> Self: raise AssumedToBeImplementedException
    def ljust(self, width: SupportsIndex, fillchar: str | LiteralString = ' ', /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def lower(self: LiteralString) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def lower(self) -> str: ...  # type: ignore[misc]
    def lower(self) -> Self: raise AssumedToBeImplementedException
    def lower(self) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def lstrip(self: LiteralString, chars: LiteralString | None = None, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def lstrip(self, chars: str | None = None, /) -> str: ...  # type: ignore[misc]
    def lstrip(self, chars: str | None = None, /) -> Self: raise AssumedToBeImplementedException
    def lstrip(self, chars: str | LiteralString | None = None, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def partition(self: LiteralString, sep: LiteralString, /) -> tuple[LiteralString, LiteralString, LiteralString]: raise AssumedToBeImplementedException
    @overload
    # def partition(self, sep: str, /) -> tuple[str, str, str]: ...  # type: ignore[misc]
    def partition(self, sep: str, /) -> tuple[Self, Self, Self]: raise AssumedToBeImplementedException
    def partition(self, sep: str | LiteralString, /) -> tuple[Self, Self, Self] | tuple[LiteralString, LiteralString, LiteralString]: raise AssumedToBeImplementedException

    if sys.version_info >= (3, 13):
        @overload
        def replace(
            self: LiteralString, old: LiteralString, new: LiteralString, /, count: SupportsIndex = -1
        ) -> LiteralString: ...
        @overload
        # def replace(self, old: str, new: str, /, count: SupportsIndex = -1) -> str: ...  # type: ignore[misc]
        def replace(self, old: str, new: str, /, count: SupportsIndex = -1) -> Self: raise AssumedToBeImplementedException  # type: ignore[misc]
        def replace(self, old: str | LiteralString, new: str | LiteralString, /, count: SupportsIndex = -1) -> Self | LiteralString: raise AssumedToBeImplementedException
    else:
        @overload
        def replace(
            self: LiteralString, old: LiteralString, new: LiteralString, count: SupportsIndex = -1, /
        ) -> LiteralString: raise AssumedToBeImplementedException
        @overload
        # def replace(self, old: str, new: str, count: SupportsIndex = -1, /) -> str:
        def replace(self, old: str, new: str, count: SupportsIndex = -1, /) -> Self: raise AssumedToBeImplementedException
        def replace(self, old: str | LiteralString, new: str | LiteralString, count: SupportsIndex = -1, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def removeprefix(self: LiteralString, prefix: LiteralString, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def removeprefix(self, prefix: str, /) -> str:
    def removeprefix(self, prefix: str, /) -> Self: raise AssumedToBeImplementedException
    def removeprefix(self, prefix: str | LiteralString, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def removesuffix(self: LiteralString, suffix: LiteralString, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def removesuffix(self, suffix: str, /) -> str:
    def removesuffix(self, suffix: str, /) -> Self: raise AssumedToBeImplementedException
    def removesuffix(self, suffix: str | LiteralString, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    def rfind(self, sub: str, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> int: raise AssumedToBeImplementedException
    def rindex(self, sub: str, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> int: raise AssumedToBeImplementedException

    @overload
    def rjust(self: LiteralString, width: SupportsIndex, fillchar: LiteralString = " ", /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def rjust(self, width: SupportsIndex, fillchar: str = " ", /) -> str:
    def rjust(self, width: SupportsIndex, fillchar: str = ' ', /) -> Self: raise AssumedToBeImplementedException
    def rjust(self, width: SupportsIndex, fillchar: str | LiteralString = " ", /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def rpartition(self: LiteralString, sep: LiteralString, /) -> tuple[LiteralString, LiteralString, LiteralString]: raise AssumedToBeImplementedException
    @overload
    # def rpartition(self, sep: str, /) -> tuple[str, str, str]:
    def rpartition(self, sep: str, /) -> tuple[Self, Self, Self]: raise AssumedToBeImplementedException
    def rpartition(self, sep: str | LiteralString, /) -> tuple[Self, Self, Self] | tuple[LiteralString, LiteralString, LiteralString]: raise AssumedToBeImplementedException

    @overload
    def rsplit(self: LiteralString, sep: LiteralString | None = None, maxsplit: SupportsIndex = -1) -> list[LiteralString]: raise AssumedToBeImplementedException
    @overload
    # def rsplit(self, sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str]:
    def rsplit(self, sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[Self]: raise AssumedToBeImplementedException
    def rsplit(self, sep: str | LiteralString | None = None, maxsplit: SupportsIndex = -1) -> list[Self] | list[LiteralString]: raise AssumedToBeImplementedException

    @overload
    def rstrip(self: LiteralString, chars: LiteralString | None = None, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def rstrip(self, chars: str | None = None, /) -> str: ...
    def rstrip(self, chars: str | None = None, /) -> Self: raise AssumedToBeImplementedException
    def rstrip(self, chars: str | None = None, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def split(self: LiteralString, sep: LiteralString | None = None, maxsplit: SupportsIndex = -1) -> list[LiteralString]: raise AssumedToBeImplementedException
    @overload
    # def split(self, sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str]:
    def split(self, sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[Self]: raise AssumedToBeImplementedException
    def split(self, sep: str | LiteralString | None = None, maxsplit: SupportsIndex = -1) -> list[Self] | list[LiteralString]: raise AssumedToBeImplementedException

    @overload
    def splitlines(self: LiteralString, keepends: bool = False) -> list[LiteralString]: raise AssumedToBeImplementedException
    @overload
    # def splitlines(self, keepends: bool = False) -> list[str]:
    def splitlines(self, keepends: bool = False) -> list[Self]: raise AssumedToBeImplementedException
    def splitlines(self, keepends: bool = False) -> list[Self] | list[LiteralString]: raise AssumedToBeImplementedException

    def startswith(
        self, prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> bool: raise AssumedToBeImplementedException

    @overload
    def strip(  # type: ignore[misc]
        self: LiteralString, chars: LiteralString | None = None, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def strip(self, chars: str | None = None, /) -> str:
    def strip(self, chars: str | None = None, /) -> Self: raise AssumedToBeImplementedException
    def strip(self, chars: str | LiteralString | None = None, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def swapcase(self: LiteralString) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def swapcase(self) -> str: ...  # type: ignore[misc]
    def swapcase(self) -> Self: raise AssumedToBeImplementedException
    def swapcase(self) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def title(self: LiteralString) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def title(self) -> str: ...  # type: ignore[misc]
    def title(self) -> Self: raise AssumedToBeImplementedException
    def title(self) -> Self | LiteralString: raise AssumedToBeImplementedException

    # def translate(self, table: _TranslateTable, /) -> str: ...
    def translate(self, table: _TranslateTable, /) -> Self: raise AssumedToBeImplementedException

    @overload
    def upper(self: LiteralString) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def upper(self) -> str: ...  # type: ignore[misc]
    def upper(self) -> Self: raise AssumedToBeImplementedException
    def upper(self) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def zfill(self: LiteralString, width: SupportsIndex, /) -> LiteralString: raise AssumedToBeImplementedException

    @overload
    # def zfill(self, width: SupportsIndex, /) -> str: ...  # type: ignore[misc]
    def zfill(self, width: SupportsIndex, /) -> Self: raise AssumedToBeImplementedException
    def zfill(self, width: SupportsIndex, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    if sys.version_info >= (3, 15):
        @staticmethod
        @overload
        def maketrans(
            x: (
                dict[int, _T]
                | dict[str, _T]
                | dict[str | int, _T]
                | frozendict[int, _T]
                | frozendict[str, _T]
                | frozendict[str | int, _T]
            ),
            /,
        ) -> dict[int, _T]: raise AssumedToBeImplementedException
    else:
        @staticmethod
        @overload
        def maketrans(x: dict[int, _T] | dict[str, _T] | dict[str | int, _T], /) -> dict[int, _T]: raise AssumedToBeImplementedException

    @staticmethod
    @overload
    def maketrans(x: str, y: str, /) -> dict[int, int]: raise AssumedToBeImplementedException
    @staticmethod
    @overload
    def maketrans(x: str, y: str, z: str, /) -> dict[int, int | None]: raise AssumedToBeImplementedException
    @staticmethod
    def maketrans(x: str | dict[int, _T] | dict[str, _T] | dict[str | int, _T], y: str | None = None, z: str | None = None, /) -> dict[int, _T] | dict[int, int] | dict[int, int | None]: raise AssumedToBeImplementedException

    @overload
    def __add__(self: LiteralString, value: LiteralString, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def __add__(self, value: str, /) -> str: ...   # type: ignore[misc]
    def __add__(self, value: str, /) -> Self: raise AssumedToBeImplementedException
    def __add__(self, value: str | LiteralString, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    # Incompatible with Sequence.__contains__
    def __contains__(self, key: str, /) -> bool: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: str, /) -> bool: raise AssumedToBeImplementedException

    @overload
    # def __getitem__(self: LiteralString, key: SupportsIndex | slice[SupportsIndex | None], /) -> LiteralString: ...
    def __getitem__(self: LiteralString, key: SupportsIndex | slice, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def __getitem__(self, key: SupportsIndex | slice[SupportsIndex | None], /) -> str:
    def __getitem__(self, key: SupportsIndex | slice, /) -> Self: raise AssumedToBeImplementedException
    def __getitem__(self, key: SupportsIndex | slice, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    def __gt__(self, value: str, /) -> bool: raise AssumedToBeImplementedException
    def __hash__(self) -> int: raise AssumedToBeImplementedException

    @overload
    def __iter__(self: LiteralString) -> Iterator[LiteralString]: raise AssumedToBeImplementedException
    @overload
    # def __iter__(self) -> Iterator[str]: ...  # type: ignore[misc]
    def __iter__(self) -> Iterator[Self]: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[Self] | Iterator[LiteralString]: raise AssumedToBeImplementedException

    def __le__(self, value: str, /) -> bool: raise AssumedToBeImplementedException
    def __len__(self) -> int: raise AssumedToBeImplementedException
    def __lt__(self, value: str, /) -> bool: raise AssumedToBeImplementedException

    @overload
    def __mod__(self: LiteralString, value: LiteralString | tuple[LiteralString, ...], /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def __mod__(self, value: Any, /) -> str: ...
    def __mod__(self, value: Any, /) -> Self: raise AssumedToBeImplementedException
    def __mod__(self, value: Any, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    @overload
    def __mul__(self: LiteralString, value: SupportsIndex, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def __mul__(self, value: SupportsIndex, /) -> str: ...  # type: ignore[misc]
    def __mul__(self, value: SupportsIndex, /) -> Self: raise AssumedToBeImplementedException
    def __mul__(self, value: SupportsIndex, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    def __ne__(self, value: object, /) -> bool: raise AssumedToBeImplementedException

    @overload
    def __rmul__(self: LiteralString, value: SupportsIndex, /) -> LiteralString: raise AssumedToBeImplementedException
    @overload
    # def __rmul__(self, value: SupportsIndex, /) -> str: ...  # type: ignore[misc]
    def __rmul__(self, value: SupportsIndex, /) -> Self: raise AssumedToBeImplementedException
    def __rmul__(self, value: SupportsIndex, /) -> Self | LiteralString: raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[str]: raise AssumedToBeImplementedException
    # def __format__(self, format_spec: str, /) -> str:
    def __format__(self, format_spec: str, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException


# @disjoint_base
# class bytes(Sequence[int]):
class IsBytes(IsItemSequence[int], Protocol):
    """Protocol with the same interface as the builtin class `bytes`.
    """

    # @overload
    # def __new__(cls, o: Iterable[SupportsIndex] | SupportsIndex | SupportsBytes | ReadableBuffer, #             /) -> Self: ...
    # @overload
    # def __new__(cls, string: str, /, encoding: str, errors: str = 'strict') -> Self: ...
    # @overload
    # def __new__(cls) -> Self: ...

    # def capitalize(self) -> bytes:
    def capitalize(self) -> Self: raise AssumedToBeImplementedException
    # def center(self, width: SupportsIndex, fillchar: bytes = b" ", /) -> bytes:
    def center(self, width: SupportsIndex, fillchar: bytes = b' ', /) -> Self: raise AssumedToBeImplementedException
    def count(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    def decode(self, encoding: str = 'utf-8', errors: str = 'strict') -> str: raise AssumedToBeImplementedException
    def endswith(
        self,
        suffix: ReadableBuffer | tuple[ReadableBuffer, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
        ) -> bool: raise AssumedToBeImplementedException
    # def expandtabs(self, tabsize: SupportsIndex = 8) -> bytes: ...
    def expandtabs(self, tabsize: SupportsIndex = 8) -> Self: raise AssumedToBeImplementedException
    def find(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    # def hex(self, sep: str | bytes = ..., bytes_per_sep: SupportsIndex = 1) -> str:
    def hex(self, sep: str | bytes = '', bytes_per_sep: SupportsIndex = 1) -> str: raise AssumedToBeImplementedException
    def index(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    def isalnum(self) -> bool: raise AssumedToBeImplementedException
    def isalpha(self) -> bool: raise AssumedToBeImplementedException
    def isascii(self) -> bool: raise AssumedToBeImplementedException
    def isdigit(self) -> bool: raise AssumedToBeImplementedException
    def islower(self) -> bool: raise AssumedToBeImplementedException
    def isspace(self) -> bool: raise AssumedToBeImplementedException
    def istitle(self) -> bool: raise AssumedToBeImplementedException
    def isupper(self) -> bool: raise AssumedToBeImplementedException
    # def join(self, iterable_of_bytes: Iterable[ReadableBuffer], /) -> bytes: ...
    def join(self, iterable_of_bytes: Iterable[ReadableBuffer], /) -> Self: raise AssumedToBeImplementedException
    # def ljust(self, width: SupportsIndex, fillchar: bytes | bytearray = b" ", /) -> bytes: ...
    def ljust(self, width: SupportsIndex, fillchar: bytes | bytearray = b" ", /) -> Self: raise AssumedToBeImplementedException
    # def lower(self) -> bytes: ...
    def lower(self) -> Self: raise AssumedToBeImplementedException
    # def lstrip(self, bytes: ReadableBuffer | None = None, /) -> bytes: ...
    def lstrip(self, bytes: ReadableBuffer | None = None, /) -> Self: raise AssumedToBeImplementedException
    # def partition(self, sep: ReadableBuffer, /) -> tuple[bytes, bytes, bytes]: ...
    def partition(self, sep: ReadableBuffer, /) -> tuple[Self, Self, Self]: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 15):
        # def replace(self, old: ReadableBuffer, new: ReadableBuffer, /, count: SupportsIndex = -1) -> bytes: ...
        def replace(self, old: ReadableBuffer, new: ReadableBuffer, /, count: SupportsIndex = -1) -> Self: raise AssumedToBeImplementedException
    else:
        # def replace(self, old: ReadableBuffer, new: ReadableBuffer, count: SupportsIndex = -1, /) -> bytes: ...
        def replace(self, old: ReadableBuffer, new: ReadableBuffer, count: SupportsIndex = -1, /) -> Self: raise AssumedToBeImplementedException

    # def removeprefix(self, prefix: ReadableBuffer, /) -> bytes: ...
    def removeprefix(self, prefix: ReadableBuffer, /) -> Self: raise AssumedToBeImplementedException
    # def removesuffix(self, suffix: ReadableBuffer, /) -> bytes: ...
    def removesuffix(self, suffix: ReadableBuffer, /) -> Self: raise AssumedToBeImplementedException
    def rfind(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    def rindex(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    # def rjust(self, width: SupportsIndex, fillchar: bytes | bytearray = b" ", /) -> bytes: ...
    def rjust(self, width: SupportsIndex, fillchar: bytes | bytearray = b' ', /) -> Self: raise AssumedToBeImplementedException
    # def rpartition(self, sep: ReadableBuffer, /) -> tuple[bytes, bytes, bytes]: ...
    def rpartition(self, sep: ReadableBuffer, /) -> tuple[Self, Self, Self]: raise AssumedToBeImplementedException
    # def rsplit(self, sep: ReadableBuffer | None = None, maxsplit: SupportsIndex = -1) -> list[bytes]: ...
    def rsplit(self, sep: ReadableBuffer | None = None, maxsplit: SupportsIndex = -1) -> list[Self]: raise AssumedToBeImplementedException
    # def rstrip(self, bytes: ReadableBuffer | None = None, /) -> bytes: ...
    def rstrip(self, bytes: ReadableBuffer | None = None, /) -> Self: raise AssumedToBeImplementedException
    # def split(self, sep: ReadableBuffer | None = None, maxsplit: SupportsIndex = -1) -> list[bytes]: ...
    def split(self, sep: ReadableBuffer | None = None, maxsplit: SupportsIndex = -1) -> list[Self]: raise AssumedToBeImplementedException
    # def splitlines(self, keepends: bool = False) -> list[bytes]: ...
    def splitlines(self, keepends: bool = False) -> list[Self]: raise AssumedToBeImplementedException
    def startswith(
        self,
        prefix: ReadableBuffer | tuple[ReadableBuffer, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool:
        """Startswith.
        
        Args:
            prefix: (ReadableBuffer | tuple[ReadableBuffer, ...]) Argument passed to ``startswith()``.
            start: (SupportsIndex | None) Argument passed to ``startswith()``.
            end: (SupportsIndex | None) Argument passed to ``startswith()``.
        
        Returns:
            bool: Result produced by ``startswith()``.
        """
        raise AssumedToBeImplementedException
    # def strip(self, bytes: ReadableBuffer | None = None, /) -> bytes: ...
    def strip(self, bytes: ReadableBuffer | None = None, /) -> Self: raise AssumedToBeImplementedException
    # def swapcase(self) -> bytes: ...
    def swapcase(self) -> Self: raise AssumedToBeImplementedException
    # def title(self) -> bytes: ...
    def title(self) -> Self: raise AssumedToBeImplementedException
    # def translate(self, table: ReadableBuffer | None, /, delete: ReadableBuffer = b"") -> bytes: ...
    def translate(self, table: ReadableBuffer | None, /, delete: ReadableBuffer = b'') -> Self: raise AssumedToBeImplementedException
    # def upper(self) -> bytes: ...
    def upper(self) -> Self: raise AssumedToBeImplementedException
    # def zfill(self, width: SupportsIndex, /) -> bytes: ...
    def zfill(self, width: SupportsIndex, /) -> Self: raise AssumedToBeImplementedException

    if sys.version_info >= (3, 14):
        @classmethod
        def fromhex(cls, string: str | ReadableBuffer, /) -> Self: raise AssumedToBeImplementedException
    else:
        @classmethod
        def fromhex(cls, string: str, /) -> Self: raise AssumedToBeImplementedException

    @staticmethod
    def maketrans(frm: ReadableBuffer, to: ReadableBuffer, /) -> bytes: raise AssumedToBeImplementedException
    def __len__(self) -> int: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[int]: raise AssumedToBeImplementedException
    def __hash__(self) -> int: raise AssumedToBeImplementedException

    @overload  # type: ignore[override]
    def __getitem__(self, key: SupportsIndex, /) -> int: raise AssumedToBeImplementedException
    @overload
    # def __getitem__(self, key: slice[SupportsIndex | None], /) -> bytes: ...
    def __getitem__(self, key: slice, /) -> Self: raise AssumedToBeImplementedException
    def __getitem__(self, key: slice | SupportsIndex, /) -> Self | int: raise AssumedToBeImplementedException

    # def __add__(self, value: ReadableBuffer, /) -> bytes: ...
    def __add__(self, value: ReadableBuffer, /) -> Self: raise AssumedToBeImplementedException
    # def __mul__(self, value: SupportsIndex, /) -> bytes: ...
    def __mul__(self, value: SupportsIndex, /) -> Self: raise AssumedToBeImplementedException
    # def __rmul__(self, value: SupportsIndex, /) -> bytes: ...
    def __rmul__(self, value: SupportsIndex, /) -> Self: raise AssumedToBeImplementedException
    # def __mod__(self, value: Any, /) -> bytes: ...
    def __mod__(self, value: Any, /) -> Self: raise AssumedToBeImplementedException
    # Incompatible with Sequence.__contains__
    def __contains__(self, key: SupportsIndex | ReadableBuffer, /) -> bool: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __ne__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __lt__(self, value: bytes, /) -> bool: raise AssumedToBeImplementedException
    def __le__(self, value: bytes, /) -> bool: raise AssumedToBeImplementedException
    def __gt__(self, value: bytes, /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: bytes, /) -> bool: raise AssumedToBeImplementedException
    def __getnewargs__(self) -> tuple[bytes]: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 11):
        def __bytes__(self) -> bytes: raise AssumedToBeImplementedException

    def __buffer__(self, flags: int, /) -> memoryview: raise AssumedToBeImplementedException

# @disjoint_base
# class bytearray(MutableSequence[int]):
class IsByteArray(IsMutableSequence[int], Protocol):
    """Protocol for the subset of built-in ``bytearray`` behavior used by Omnipy typing."""

    # @overload
    # def __init__(self) -> None: ...
    # @overload
    # def __init__(self, ints: Iterable[SupportsIndex] | SupportsIndex | ReadableBuffer, /) -> None: ...
    # @overload
    # def __init__(self, string: str, /, encoding: str, errors: str = 'strict') -> None: ...

    def append(self, item: SupportsIndex, /) -> None: raise AssumedToBeImplementedException
    def capitalize(self) -> bytearray: raise AssumedToBeImplementedException
    def center(self, width: SupportsIndex, fillchar: bytes = b' ', /) -> bytearray: raise AssumedToBeImplementedException
    def count(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    # def copy(self) -> bytearray: raise AssumedToBeImplementedException
    def decode(self, encoding: str = 'utf-8', errors: str = 'strict') -> str: raise AssumedToBeImplementedException
    def endswith(
        self,
        suffix: ReadableBuffer | tuple[ReadableBuffer, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool: raise AssumedToBeImplementedException
    def expandtabs(self, tabsize: SupportsIndex = 8) -> bytearray: raise AssumedToBeImplementedException
    def extend(self, iterable_of_ints: Iterable[SupportsIndex], /) -> None: raise AssumedToBeImplementedException
    def find(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    # def hex(self, sep: str | bytes = ..., bytes_per_sep: SupportsIndex = 1) -> str: ...
    def hex(self, sep: str | bytes = '', bytes_per_sep: SupportsIndex = 1) -> str: raise AssumedToBeImplementedException
    def index(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    def insert(self, index: SupportsIndex, item: SupportsIndex, /) -> None: raise AssumedToBeImplementedException
    def isalnum(self) -> bool: raise AssumedToBeImplementedException
    def isalpha(self) -> bool: raise AssumedToBeImplementedException
    def isascii(self) -> bool: raise AssumedToBeImplementedException
    def isdigit(self) -> bool: raise AssumedToBeImplementedException
    def islower(self) -> bool: raise AssumedToBeImplementedException
    def isspace(self) -> bool: raise AssumedToBeImplementedException
    def istitle(self) -> bool: raise AssumedToBeImplementedException
    def isupper(self) -> bool: raise AssumedToBeImplementedException
    def join(self, iterable_of_bytes: Iterable[ReadableBuffer], /) -> bytearray: raise AssumedToBeImplementedException
    def ljust(self, width: SupportsIndex, fillchar: bytes | bytearray = b' ', /) -> bytearray: raise AssumedToBeImplementedException
    def lower(self) -> bytearray: raise AssumedToBeImplementedException
    def lstrip(self, bytes: ReadableBuffer | None = None, /) -> bytearray: raise AssumedToBeImplementedException
    def partition(self, sep: ReadableBuffer, /) -> tuple[bytearray, bytearray, bytearray]: raise AssumedToBeImplementedException
    def pop(self, index: int = -1, /) -> int: raise AssumedToBeImplementedException
    def remove(self, value: int, /) -> None: raise AssumedToBeImplementedException
    def removeprefix(self, prefix: ReadableBuffer, /) -> bytearray: raise AssumedToBeImplementedException
    def removesuffix(self, suffix: ReadableBuffer, /) -> bytearray: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 15):
        def replace(self, old: ReadableBuffer, new: ReadableBuffer, /, count: SupportsIndex = -1) -> bytearray: raise AssumedToBeImplementedException
    else:
        def replace(self, old: ReadableBuffer, new: ReadableBuffer, count: SupportsIndex = -1, /) -> bytearray: raise AssumedToBeImplementedException

    def rfind(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    def rindex(
        self, sub: ReadableBuffer | SupportsIndex, start: SupportsIndex | None = None, end: SupportsIndex | None = None, /
    ) -> int: raise AssumedToBeImplementedException
    def rjust(self, width: SupportsIndex, fillchar: bytes | bytearray = b" ", /) -> bytearray: raise AssumedToBeImplementedException
    def rpartition(self, sep: ReadableBuffer, /) -> tuple[bytearray, bytearray, bytearray]: raise AssumedToBeImplementedException
    def rsplit(self, sep: ReadableBuffer | None = None, maxsplit: SupportsIndex = -1) -> list[bytearray]: raise AssumedToBeImplementedException
    def rstrip(self, bytes: ReadableBuffer | None = None, /) -> bytearray: raise AssumedToBeImplementedException
    def split(self, sep: ReadableBuffer | None = None, maxsplit: SupportsIndex = -1) -> list[bytearray]: raise AssumedToBeImplementedException
    def splitlines(self, keepends: bool = False) -> list[bytearray]: raise AssumedToBeImplementedException
    def startswith(
        self,
        prefix: ReadableBuffer | tuple[ReadableBuffer, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool: raise AssumedToBeImplementedException
    def strip(self, bytes: ReadableBuffer | None = None, /) -> bytearray: raise AssumedToBeImplementedException
    def swapcase(self) -> bytearray: raise AssumedToBeImplementedException
    def title(self) -> bytearray: raise AssumedToBeImplementedException
    def translate(self, table: ReadableBuffer | None, /, delete: bytes = b'') -> bytearray: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 15):
        def take_bytes(self, n: int | None = None, /) -> bytes: raise AssumedToBeImplementedException

    def upper(self) -> bytearray: raise AssumedToBeImplementedException
    def zfill(self, width: SupportsIndex, /) -> bytearray: raise AssumedToBeImplementedException

    if sys.version_info >= (3, 14):
        @classmethod
        def fromhex(cls, string: str | ReadableBuffer, /) -> Self: raise AssumedToBeImplementedException
    else:
        @classmethod
        def fromhex(cls, string: str, /) -> Self: raise AssumedToBeImplementedException

    @staticmethod
    def maketrans(frm: ReadableBuffer, to: ReadableBuffer, /) -> bytes: raise AssumedToBeImplementedException
    def __len__(self) -> int: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[int]: raise AssumedToBeImplementedException
    # __hash__: ClassVar[None]  # type: ignore[assignment]
    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    @overload  # type: ignore[override]
    def __getitem__(self, key: SupportsIndex, /) -> int: raise AssumedToBeImplementedException
    @overload
    # def __getitem__(self, key: slice[SupportsIndex | None], /) -> bytearray: ...
    def __getitem__(self, key: slice, /) -> bytearray: raise AssumedToBeImplementedException
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
            self, key: slice | SupportsIndex, /) -> bytearray | int: raise AssumedToBeImplementedException

    @overload
    def __setitem__(self, key: SupportsIndex, value: SupportsIndex, /) -> None: raise AssumedToBeImplementedException
    @overload
    # def __setitem__(self, key: slice[SupportsIndex | None], value: Iterable[SupportsIndex] | bytes, /) -> None: ...
    def __setitem__(self, key: slice, value: Iterable[SupportsIndex] | bytes, /) -> None: raise AssumedToBeImplementedException
    def __setitem__(self, key: slice | SupportsIndex, value: Iterable[SupportsIndex] | bytes | SupportsIndex, /) -> None: raise AssumedToBeImplementedException

    # def __delitem__(self, key: SupportsIndex | slice[SupportsIndex | None], /) -> None: ...
    def __delitem__(self, key: SupportsIndex | slice, /) -> None: raise AssumedToBeImplementedException

    def __add__(self, value: ReadableBuffer, /) -> bytearray: raise AssumedToBeImplementedException
    # The superclass wants us to accept Iterable[int], but that fails at runtime.
    def __iadd__(self, value: ReadableBuffer, /) -> Self: raise AssumedToBeImplementedException  # type: ignore[override]
    def __mul__(self, value: SupportsIndex, /) -> bytearray: raise AssumedToBeImplementedException
    def __rmul__(self, value: SupportsIndex, /) -> bytearray: raise AssumedToBeImplementedException
    def __imul__(self, value: SupportsIndex, /) -> Self: raise AssumedToBeImplementedException
    def __mod__(self, value: Any, /) -> bytes: raise AssumedToBeImplementedException
    # Incompatible with Sequence.__contains__
    def __contains__(self, key: SupportsIndex | ReadableBuffer, /) -> bool: raise AssumedToBeImplementedException  # type: ignore[override]
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __ne__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __lt__(self, value: ReadableBuffer, /) -> bool: raise AssumedToBeImplementedException
    def __le__(self, value: ReadableBuffer, /) -> bool: raise AssumedToBeImplementedException
    def __gt__(self, value: ReadableBuffer, /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: ReadableBuffer, /) -> bool: raise AssumedToBeImplementedException
    def __alloc__(self) -> int: raise AssumedToBeImplementedException
    def __buffer__(self, flags: int, /) -> memoryview: raise AssumedToBeImplementedException
    def __release_buffer__(self, buffer: memoryview, /) -> None: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 14):
        def resize(self, size: int, /) -> None: raise AssumedToBeImplementedException

_IntegerFormats: TypeAlias = Literal[
    "b", "B", "@b", "@B", "h", "H", "@h", "@H", "i", "I", "@i", "@I", "l", "L", "@l", "@L", "q", "Q", "@q", "@Q", "P", "@P"
]

# @final
# class memoryview(Sequence[_I]):
#     @property
#     def format(self) -> str: ...
#     @property
#     def itemsize(self) -> int: ...
#     @property
#     def shape(self) -> tuple[int, ...] | None: ...
#     @property
#     def strides(self) -> tuple[int, ...] | None: ...
#     @property
#     def suboffsets(self) -> tuple[int, ...] | None: ...
#     @property
#     def readonly(self) -> bool: ...
#     @property
#     def ndim(self) -> int: ...
#     @property
#     def obj(self) -> ReadableBuffer: ...
#     @property
#     def c_contiguous(self) -> bool: ...
#     @property
#     def f_contiguous(self) -> bool: ...
#     @property
#     def contiguous(self) -> bool: ...
#     @property
#     def nbytes(self) -> int: ...
#     def __new__(cls, obj: ReadableBuffer) -> Self: ...
#     def __enter__(self) -> Self: ...
#     def __exit__(
#         self,
#         exc_type: type[BaseException] | None,  # noqa: PYI036 # This is the module declaring BaseException
#         exc_val: BaseException | None,
#         exc_tb: TracebackType | None,
#         /,
#     ) -> None: ...
#
#     @overload
#     def cast(self, format: Literal["c", "@c"], shape: list[int] | tuple[int, ...] = ...) -> memoryview[bytes]: ...
#     @overload
#     def cast(self, format: Literal["f", "@f", "d", "@d"], shape: list[int] | tuple[int, ...] = ...) -> memoryview[float]: ...
#     @overload
#     def cast(self, format: Literal["?"], shape: list[int] | tuple[int, ...] = ...) -> memoryview[bool]: ...
#     @overload
#     def cast(self, format: _IntegerFormats, shape: list[int] | tuple[int, ...] = ...) -> memoryview: ...
#
#     @overload
#     def __getitem__(self, key: SupportsIndex | tuple[SupportsIndex, ...], /) -> _I: ...
#     @overload
#     def __getitem__(self, key: slice[SupportsIndex | None], /) -> memoryview[_I]: ...
#
#     def __contains__(self, x: object, /) -> bool: ...
#     def __iter__(self) -> Iterator[_I]: ...
#     def __len__(self) -> int: ...
#     def __eq__(self, value: object, /) -> bool: ...
#     def __hash__(self) -> int: ...
#
#     @overload
#     def __setitem__(self, key: slice[SupportsIndex | None], value: ReadableBuffer, /) -> None: ...
#     @overload
#     def __setitem__(self, key: SupportsIndex | tuple[SupportsIndex, ...], value: _I, /) -> None: ...
#
#     def tobytes(self, order: Literal["C", "F", "A"] | None = "C") -> bytes: ...
#     def tolist(self) -> list[int]: ...
#     def toreadonly(self) -> memoryview: ...
#     def release(self) -> None: ...
#     def hex(self, sep: str | bytes = ..., bytes_per_sep: SupportsIndex = 1) -> str: ...
#     def __buffer__(self, flags: int, /) -> memoryview: ...
#     def __release_buffer__(self, buffer: memoryview, /) -> None: ...
#     if sys.version_info >= (3, 14):
#         def index(self, value: object, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize, /) -> int: ...
#         def count(self, value: object, /) -> int: ...
#     else:
#         # These are inherited from the Sequence ABC, but don't actually exist on memoryview.
#         # See https://github.com/python/cpython/issues/125420
#         index: ClassVar[None]  # type: ignore[assignment]
#         count: ClassVar[None]  # type: ignore[assignment]
#
#     if sys.version_info >= (3, 14):
#         def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...

# @final
# class bool(int):
class IsBool(IsInt, Protocol):
    """Define the ``IsBool`` interface.
    """
    # def __new__(cls, o: object = False, /) -> Self: ...

    # The following overloads could be represented more elegantly with a TypeVar("_B", bool, int),
    # however mypy has a bug regarding TypeVar constraints (https://github.com/python/mypy/issues/11880)
    @overload
    def __and__(self, value: bool, /) -> bool: raise AssumedToBeImplementedException
    @overload
    def __and__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __and__(self, value: int | bool, /) -> int | bool: raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: bool, /) -> bool: raise AssumedToBeImplementedException
    @overload
    def __or__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __or__(self, value: int | bool, /) -> int | bool: raise AssumedToBeImplementedException

    @overload
    def __xor__(self, value: bool, /) -> bool: raise AssumedToBeImplementedException
    @overload
    def __xor__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __xor__(self, value: int | bool, /) -> int | bool: raise AssumedToBeImplementedException

    @overload
    def __rand__(self, value: bool, /) -> bool: raise AssumedToBeImplementedException
    @overload
    def __rand__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rand__(self, value: int | bool, /) -> int | bool: raise AssumedToBeImplementedException

    @overload
    def __ror__(self, value: bool, /) -> bool: raise AssumedToBeImplementedException
    @overload
    def __ror__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __ror__(self, value: int | bool, /) -> int | bool: raise AssumedToBeImplementedException

    @overload
    def __rxor__(self, value: bool, /) -> bool: raise AssumedToBeImplementedException
    @overload
    def __rxor__(self, value: int, /) -> int: raise AssumedToBeImplementedException
    def __rxor__(self, value: int | bool, /) -> int | bool: raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[int]: raise AssumedToBeImplementedException
    @deprecated('Will throw an error in Python 3.16. Use `not` for logical negation of bools instead.')
    def __invert__(self) -> int: raise AssumedToBeImplementedException

# @final
# class slice(Generic[_StartT_co, _StopT_co, _StepT_co]):
#     @property
#     def start(self) -> _StartT_co: ...
#     @property
#     def step(self) -> _StepT_co: ...
#     @property
#     def stop(self) -> _StopT_co: ...
#
#     # Note: __new__ overloads map `None` to `Any`, since users expect slice(x, None)
#     #  to be compatible with slice(None, x).
#     # generic slice --------------------------------------------------------------------
#     @overload
#     def __new__(cls, start: None, stop: None = None, step: None = None, /) -> slice[Any, Any, Any]: ...
#     # unary overloads ------------------------------------------------------------------
#     @overload
#     def __new__(cls, stop: _T2, /) -> slice[Any, _T2, Any]: ...
#     # binary overloads -----------------------------------------------------------------
#     @overload
#     def __new__(cls, start: _T1, stop: None, step: None = None, /) -> slice[_T1, Any, Any]: ...
#     @overload
#     def __new__(cls, start: None, stop: _T2, step: None = None, /) -> slice[Any, _T2, Any]: ...
#     @overload
#     def __new__(cls, start: _T1, stop: _T2, step: None = None, /) -> slice[_T1, _T2, Any]: ...
#     # ternary overloads ----------------------------------------------------------------
#     @overload
#     def __new__(cls, start: None, stop: None, step: _T3, /) -> slice[Any, Any, _T3]: ...
#     @overload
#     def __new__(cls, start: _T1, stop: None, step: _T3, /) -> slice[_T1, Any, _T3]: ...
#     @overload
#     def __new__(cls, start: None, stop: _T2, step: _T3, /) -> slice[Any, _T2, _T3]: ...
#     @overload
#     def __new__(cls, start: _T1, stop: _T2, step: _T3, /) -> slice[_T1, _T2, _T3]: ...
#
#     def __eq__(self, value: object, /) -> bool: ...
#     if sys.version_info >= (3, 12):
#         def __hash__(self) -> int: ...
#     else:
#         __hash__: ClassVar[None]  # type: ignore[assignment]
#
#     def indices(self, len: SupportsIndex, /) -> tuple[int, int, int]: ...
#     if sys.version_info >= (3, 15):
#         def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...

# @disjoint_base
# class tuple(Sequence[_T_co]):
class IsTuple(IsItemSequence[_T_co], Protocol[_T_co]):  # type: ignore[misc]
    """Protocol with the same interface as the builtin class `tuple`.
    """
    # def __new__(cls, iterable: Iterable[_T_co] = (), /) -> Self: ...
    def __len__(self) -> int: raise AssumedToBeImplementedException
    def __contains__(self, key: object, /) -> bool: raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, key: SupportsIndex, /) -> _T_co: raise AssumedToBeImplementedException
    @overload
    # def __getitem__(self, key: slice[SupportsIndex | None], /) -> tuple[_T_co, ...]:
    def __getitem__(self, key: slice, /) -> tuple[_T_co, ...]: raise AssumedToBeImplementedException
    def __getitem__(self, key: slice | SupportsIndex, /) -> tuple[_T_co, ...] | _T_co: raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_T_co]: raise AssumedToBeImplementedException
    def __lt__(self, value: tuple[_T_co, ...], /) -> bool: raise AssumedToBeImplementedException
    def __le__(self, value: tuple[_T_co, ...], /) -> bool: raise AssumedToBeImplementedException
    def __gt__(self, value: tuple[_T_co, ...], /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: tuple[_T_co, ...], /) -> bool: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __hash__(self) -> int: raise AssumedToBeImplementedException

    @overload
    def __add__(self, value: tuple[_T_co, ...], /) -> tuple[_T_co, ...]: raise AssumedToBeImplementedException
    @overload
    def __add__(self, value: tuple[_T, ...], /) -> tuple[_T_co | _T, ...]: raise AssumedToBeImplementedException
    def __add__(self, value: tuple[_T, ...] | tuple[_T_co, ...], /) -> tuple[_T_co | _T, ...] | tuple[_T_co, ...]: raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> tuple[_T_co, ...]: raise AssumedToBeImplementedException
    def __rmul__(self, value: SupportsIndex, /) -> tuple[_T_co, ...]: raise AssumedToBeImplementedException
    def count(self, value: Any, /) -> int: raise AssumedToBeImplementedException
    def index(self, value: Any, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize, /) -> int: raise AssumedToBeImplementedException
    # def __class_getitem__(cls, item: Any, /) -> GenericAlias: raise AssumedToBeImplementedException

# # Doesn't exist at runtime, but deleting this breaks mypy and pyright. See:
# # https://github.com/python/typeshed/issues/7580
# # https://github.com/python/mypy/issues/8240
# # Obsolete, use types.FunctionType instead.
# @final
# @type_check_only
# class function:
#     # Make sure this class definition stays roughly in line with `types.FunctionType`
#     @property
#     def __closure__(self) -> tuple[CellType, ...] | None: ...
#     __code__: CodeType
#     __defaults__: tuple[Any, ...] | None
#     __dict__: dict[str, Any]
#     @property
#     def __globals__(self) -> dict[str, Any]: ...
#     __name__: str
#     __qualname__: str
#     __annotations__: dict[str, AnnotationForm]
#     if sys.version_info >= (3, 14):
#         __annotate__: AnnotateFunc | None
#     __kwdefaults__: dict[str, Any] | None
#     @property
#     def __builtins__(self) -> dict[str, Any]: ...
#     if sys.version_info >= (3, 12):
#         __type_params__: tuple[TypeVar | ParamSpec | TypeVarTuple, ...]
#
#     __module__: str
#     if sys.version_info >= (3, 13):
#         def __new__(
#             cls,
#             code: CodeType,
#             globals: dict[str, Any],
#             name: str | None = None,
#             argdefs: tuple[object, ...] | None = None,
#             closure: tuple[CellType, ...] | None = None,
#             kwdefaults: dict[str, object] | None = None,
#         ) -> Self: ...
#     else:
#         def __new__(
#             cls,
#             code: CodeType,
#             globals: dict[str, Any],
#             name: str | None = None,
#             argdefs: tuple[object, ...] | None = None,
#             closure: tuple[CellType, ...] | None = None,
#         ) -> Self: ...
#
#     # mypy uses `builtins.function.__get__` to represent methods, properties, and getset_descriptors so we type the return as Any.
#     def __get__(self, instance: object, owner: type | None = None, /) -> Any: ...

# @disjoint_base
# class list(MutableSequence[_T]):
class IsList(IsMutableSequence[_T], Protocol[_T]):
    """Protocol for the subset of built-in ``list`` behavior used by Omnipy typing."""

    # @overload
    # def __init__(self) -> None: ...
    # @overload
    # def __init__(self, iterable: Iterable[_T], /) -> None: ...

    # def copy(self) -> list[_T]: raise AssumedToBeImplementedException
    def append(self, object: _T, /) -> None: raise AssumedToBeImplementedException
    def extend(self, iterable: Iterable[_T], /) -> None: raise AssumedToBeImplementedException
    def pop(self, index: SupportsIndex = -1, /) -> _T: raise AssumedToBeImplementedException
    # Signature of `list.index` should be kept in line with `collections.UserList.index()`
    # and multiprocessing.managers.ListProxy.index()
    def index(self, value: _T, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize, /) -> int: raise AssumedToBeImplementedException
    def count(self, value: _T, /) -> int: raise AssumedToBeImplementedException
    def insert(self, index: SupportsIndex, object: _T, /) -> None: raise AssumedToBeImplementedException
    def remove(self, value: _T, /) -> None: raise AssumedToBeImplementedException

    # Signature of `list.sort` should be kept inline with `collections.UserList.sort()`
    # and multiprocessing.managers.ListProxy.sort()
    #
    # Use list[SupportsRichComparisonT] for the first overload rather than [SupportsRichComparison]
    # to work around invariance
    @overload
    def sort(self: IsList[SupportsRichComparisonT], *, key: None = None, reverse: bool = False) -> None: raise AssumedToBeImplementedException
    @overload
    def sort(self, *, key: Callable[[_T], SupportsRichComparison], reverse: bool = False) -> None: raise AssumedToBeImplementedException
    def sort(self: IsList[_T] | IsList[SupportsRichComparisonT], *, key: Callable[[_T], SupportsRichComparison] | None = None, reverse: bool = False) -> None: raise AssumedToBeImplementedException

    def __len__(self) -> int: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[_T]: raise AssumedToBeImplementedException
    # __hash__: ClassVar[None]  # type: ignore[assignment]
    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    @overload
    def __getitem__(self, i: SupportsIndex, /) -> _T: raise AssumedToBeImplementedException
    @overload
    # def __getitem__(self, s: slice[SupportsIndex | None], /) -> list[_T]: ...
    def __getitem__(self, s: slice, /) -> list[_T]: raise AssumedToBeImplementedException
    def __getitem__(self, s: slice | SupportsIndex, /) -> list[_T] | _T: raise AssumedToBeImplementedException

    @overload
    def __setitem__(self, key: SupportsIndex, value: _T, /) -> None: raise AssumedToBeImplementedException
    @overload
    # def __setitem__(self, key: slice[SupportsIndex | None], value: Iterable[_T], /) -> None: ...
    def __setitem__(self, key: slice, value: Iterable[_T], /) -> None: raise AssumedToBeImplementedException
    def __setitem__(self, key: slice | SupportsIndex, value: Iterable[_T] | _T, /) -> None: raise AssumedToBeImplementedException

    # def __delitem__(self, key: SupportsIndex | slice[SupportsIndex | None], /) -> None: ...
    def __delitem__(self, key: SupportsIndex | slice, /) -> None: raise AssumedToBeImplementedException

    # Overloading looks unnecessary, but is needed to work around complex mypy problems
    @overload
    def __add__(self, value: list[_T], /) -> list[_T]: raise AssumedToBeImplementedException
    @overload
    def __add__(self, value: list[_S], /) -> list[_S | _T]: raise AssumedToBeImplementedException
    def __add__(self, value: list[Any], /) -> list[Any]: raise AssumedToBeImplementedException

    def __iadd__(self, value: Iterable[_T], /) -> Self: raise AssumedToBeImplementedException
    def __mul__(self, value: SupportsIndex, /) -> list[_T]: raise AssumedToBeImplementedException
    def __rmul__(self, value: SupportsIndex, /) -> list[_T]: raise AssumedToBeImplementedException
    def __imul__(self, value: SupportsIndex, /) -> Self: raise AssumedToBeImplementedException
    def __contains__(self, key: object, /) -> bool: raise AssumedToBeImplementedException
    def __reversed__(self) -> Iterator[_T]: raise AssumedToBeImplementedException
    def __gt__(self, value: list[_T], /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: list[_T], /) -> bool: raise AssumedToBeImplementedException
    def __lt__(self, value: list[_T], /) -> bool: raise AssumedToBeImplementedException
    def __le__(self, value: list[_T], /) -> bool: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    # def __class_getitem__(cls, item: Any, /) -> GenericAlias: raise AssumedToBeImplementedException

# @disjoint_base
# class dict(MutableMapping[_KT, _VT]):
class IsDict(IsMutableMapping[_KT, _VT], Protocol[_KT, _VT]):
    """Define the ``IsDict`` interface.
    """
    # # __init__ should be kept roughly in line with `collections.UserDict.__init__`, which has similar semantics
    # # Also multiprocessing.managers.SyncManager.dict()
    # @overload
    # def __init__(self, /) -> None: ...
    # @overload
    # def __init__(self: dict[str, _VT], /, **kwargs: _VT) -> None: ...  # pyright: ignore[reportInvalidTypeVarUse]  #11780
    # @overload
    # def __init__(self, map: SupportsKeysAndGetItem[_KT, _VT], /) -> None: ...
    # @overload
    # def __init__(
    #     self: dict[str, _VT],  # pyright: ignore[reportInvalidTypeVarUse]  #11780
    #     map: SupportsKeysAndGetItem[str, _VT],
    #     /,
    #     **kwargs: _VT,
    # ) -> None: ...
    # @overload
    # def __init__(self, iterable: Iterable[tuple[_KT, _VT]], /) -> None: ...
    # @overload
    # def __init__(
    #     self: dict[str, _VT],  # pyright: ignore[reportInvalidTypeVarUse]  #11780
    #     iterable: Iterable[tuple[str, _VT]], #     /, #     **kwargs: _VT, # ) -> None: ...
    # # Next two overloads are for dict(string.split(sep) for string in iterable)
    # # Cannot be Iterable[Sequence[_T]] or otherwise dict(["foo", "bar", "baz"]) is not an error
    # @overload
    # def __init__(self: dict[str, str], iterable: Iterable[list[str]], /) -> None: ...
    # @overload
    # def __init__(self: dict[bytes, bytes], iterable: Iterable[list[bytes]], /) -> None: ...

    # def __new__(cls, /, *args: Any, **kwargs: Any) -> Self: ...
    # def copy(self) -> dict[_KT, _VT]: raise AssumedToBeImplementedException
    # def keys(self) -> dict_keys[_KT, _VT]:
    def keys(self) -> IsDictKeys[_KT, _VT]: raise AssumedToBeImplementedException
    # def values(self) -> dict_values[_KT, _VT]:
    def values(self) -> IsDictValues[_KT, _VT]: raise AssumedToBeImplementedException
    # def items(self) -> dict_items[_KT, _VT]:
    def items(self) -> IsDictItems[_KT, _VT]: raise AssumedToBeImplementedException

    # Signature of `dict.fromkeys` should be kept identical to
    # `fromkeys` methods of `OrderedDict`/`ChainMap`/`UserDict` in `collections`
    # TODO: the true signature of `dict.fromkeys` is not expressible in the current type system.
    # See #3800 & https://github.com/python/typing/issues/548#issuecomment-683336963.
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_T], value: None = None, /) -> dict[_T, Any | None]: raise AssumedToBeImplementedException
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_T], value: _S, /) -> dict[_T, _S]: raise AssumedToBeImplementedException
    @classmethod
    def fromkeys(
        cls, iterable: Iterable[_T], value: _S | None = None, /) -> dict[_T, _S] | dict[_T, Any | None]: raise AssumedToBeImplementedException

    # Positional-only in dict, but not in MutableMapping
    @overload
    def get(self, key: _KT, default: None = None, /) -> _VT | None: raise AssumedToBeImplementedException
    @overload
    def get(self, key: _KT, default: _VT, /) -> _VT: raise AssumedToBeImplementedException
    @overload
    def get(self, key: _KT, default: _T, /) -> _VT | _T: raise AssumedToBeImplementedException
    def get(self, key: _KT, default: None | _VT | _T = None, /) -> _VT | _T | None: raise AssumedToBeImplementedException

    @overload
    def pop(self, key: _KT, /) -> _VT: raise AssumedToBeImplementedException
    @overload
    def pop(self, key: _KT, default: _VT, /) -> _VT: raise AssumedToBeImplementedException
    @overload
    def pop(self, key: _KT, default: _T, /) -> _VT | _T: raise AssumedToBeImplementedException
    def pop(self, key: _KT, default: None | _VT | _T = None, /) -> _VT | _T | None: raise AssumedToBeImplementedException

    def __len__(self) -> int: raise AssumedToBeImplementedException
    def __getitem__(self, key: _KT, /) -> _VT: raise AssumedToBeImplementedException
    def __setitem__(self, key: _KT, value: _VT, /) -> None: raise AssumedToBeImplementedException
    def __delitem__(self, key: _KT, /) -> None: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[_KT]: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __reversed__(self) -> Iterator[_KT]: raise AssumedToBeImplementedException
    # __hash__: ClassVar[None]  # type: ignore[assignment]
    __hash__: ClassVar[None] = None  # type: ignore[assignment]
    # def __class_getitem__(cls, item: Any, /) -> GenericAlias: raise AssumedToBeImplementedException
    if sys.version_info >= (3, 15):
        def __or__(self, value: dict[_T1, _T2] | frozendict[_T1, _T2], /) -> dict[_KT | _T1, _VT | _T2]: raise AssumedToBeImplementedException

        @overload
        def __ror__(self, value: dict[_T1, _T2], /) -> dict[_KT | _T1, _VT | _T2]: raise AssumedToBeImplementedException
        @overload
        def __ror__(self, value: frozendict[_T1, _T2], /) -> frozendict[_KT | _T1, _VT | _T2]: raise AssumedToBeImplementedException
        def __ror__(self, value: dict[_T1, _T2] | frozendict[_T1, _T2], /) -> dict[_KT | _T1, _VT | _T2] | frozendict[_KT | _T1, _VT | _T2]: raise AssumedToBeImplementedException
    else:
        def __or__(self, value: dict[_T1, _T2], /) -> dict[_KT | _T1, _VT | _T2]: raise AssumedToBeImplementedException
        def __ror__(self, value: dict[_T1, _T2], /) -> dict[_KT | _T1, _VT | _T2]: raise AssumedToBeImplementedException

    # dict.__ior__ should be kept roughly in line with MutableMapping.update()
    @overload  # type: ignore[misc]
    def __ior__(self, value: SupportsKeysAndGetItem[_KT, _VT], /) -> Self: raise AssumedToBeImplementedException
    @overload
    def __ior__(self, value: Iterable[tuple[_KT, _VT]], /) -> Self: raise AssumedToBeImplementedException
    def __ior__(self, value: SupportsKeysAndGetItem[_KT, _VT] | Iterable[tuple[_KT, _VT]], /) -> Self: raise AssumedToBeImplementedException

if sys.version_info >= (3, 15):
    @disjoint_base
    class frozendict(IsMapping[_KT, _VT]):
        @overload
        def __new__(cls, /) -> frozendict[Any, Any]: ...
        @overload
        def __new__(cls: type[frozendict[str, _VT]], /, **kwargs: _VT) -> frozendict[str, _VT]: ...
        @overload
        def __new__(cls, map: SupportsKeysAndGetItem[_KT, _VT], /) -> frozendict[_KT, _VT]: ...
        @overload
        def __new__(
            cls: type[frozendict[str, _VT]], map: SupportsKeysAndGetItem[str, _VT], /, **kwargs: _VT
        ) -> frozendict[str, _VT]: ...
        @overload
        def __new__(cls, iterable: Iterable[tuple[_KT, _VT]], /) -> frozendict[_KT, _VT]: ...
        @overload
        def __new__(
            cls: type[frozendict[str, _VT]], iterable: Iterable[tuple[str, _VT]], /, **kwargs: _VT
        ) -> frozendict[str, _VT]: ...

        def __init__(self) -> None: ...
        def copy(self) -> frozendict[_KT, _VT]: ...

        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[_T], value: None = None, /) -> frozendict[_T, Any | None]: ...
        @overload
        @classmethod
        def fromkeys(cls, iterable: Iterable[_T], value: _S, /) -> frozendict[_T, _S]: ...

        @overload  # type: ignore[override]
        def get(self, key: _KT, default: None = None, /) -> _VT | None: ...
        @overload
        def get(self, key: _KT, default: _VT, /) -> _VT: ...
        @overload
        def get(self, key: _KT, default: _T, /) -> _VT | _T: ...

        def keys(self) -> dict_keys[_KT, _VT]: ...
        def values(self) -> dict_values[_KT, _VT]: ...
        def items(self) -> dict_items[_KT, _VT]: ...
        def __len__(self) -> int: ...
        def __getitem__(self, key: _KT, /) -> _VT: ...
        def __reversed__(self) -> Iterator[_KT]: ...
        def __iter__(self) -> Iterator[_KT]: ...
        def __hash__(self) -> int: ...
        def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...
        def __or__(self, value: dict[_T1, _T2] | frozendict[_T1, _T2], /) -> frozendict[_KT | _T1, _VT | _T2]: ...

        @overload
        def __ror__(self, value: dict[_T1, _T2], /) -> dict[_KT | _T1, _VT | _T2]: ...
        @overload
        def __ror__(self, value: frozendict[_T1, _T2], /) -> frozendict[_KT | _T1, _VT | _T2]: ...

# @disjoint_base
# class set(MutableSet[_T]):
class IsSet(IsMutableSet[_T], Protocol[_T]):
    """Define the ``IsSet`` interface.
    """
    # @overload
    # def __init__(self) -> None: ...
    #
    # @overload
    # def __init__(self, iterable: Iterable[_T], /) -> None: ...

    def add(self, element: _T, /) -> None: raise AssumedToBeImplementedException
    # def copy(self) -> set[_T]: raise AssumedToBeImplementedException
    def difference(self, *s: Iterable[object]) -> set[_T]: raise AssumedToBeImplementedException
    def difference_update(self, *s: Iterable[object]) -> None: raise AssumedToBeImplementedException
    def discard(self, element: object, /) -> None: raise AssumedToBeImplementedException
    def intersection(self, *s: Iterable[object]) -> set[_T]: raise AssumedToBeImplementedException
    def intersection_update(self, *s: Iterable[object]) -> None: raise AssumedToBeImplementedException
    def isdisjoint(self, s: Iterable[object], /) -> bool: raise AssumedToBeImplementedException
    def issubset(self, s: Iterable[object], /) -> bool: raise AssumedToBeImplementedException
    def issuperset(self, s: Iterable[object], /) -> bool: raise AssumedToBeImplementedException
    def remove(self, element: _T, /) -> None: raise AssumedToBeImplementedException
    def symmetric_difference(self, s: Iterable[_S], /) -> set[_T | _S]: raise AssumedToBeImplementedException
    def symmetric_difference_update(self, s: Iterable[_T], /) -> None: raise AssumedToBeImplementedException
    def union(self, *s: Iterable[_S]) -> set[_T | _S]: raise AssumedToBeImplementedException
    def update(self, *s: Iterable[_T]) -> None: raise AssumedToBeImplementedException
    def __len__(self) -> int: raise AssumedToBeImplementedException
    def __contains__(self, o: object, /) -> bool: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[_T]: raise AssumedToBeImplementedException
    def __and__(self, value: AbstractSet[object], /) -> set[_T]: raise AssumedToBeImplementedException
    def __iand__(self, value: AbstractSet[object], /) -> set[_T]: raise AssumedToBeImplementedException
    def __or__(self, value: AbstractSet[_S], /) -> set[_T | _S]: raise AssumedToBeImplementedException
    def __ior__(self, value: AbstractSet[_T], /) -> Self: raise AssumedToBeImplementedException
    def __sub__(self, value: AbstractSet[object], /) -> set[_T]: raise AssumedToBeImplementedException
    def __isub__(self, value: AbstractSet[object], /) -> Self: raise AssumedToBeImplementedException
    def __xor__(self, value: AbstractSet[_S], /) -> set[_T | _S]: raise AssumedToBeImplementedException
    def __ixor__(self, value: AbstractSet[_T], /) -> Self: raise AssumedToBeImplementedException
    def __le__(self, value: AbstractSet[object], /) -> bool: raise AssumedToBeImplementedException
    def __lt__(self, value: AbstractSet[object], /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: AbstractSet[object], /) -> bool: raise AssumedToBeImplementedException
    def __gt__(self, value: AbstractSet[object], /) -> bool: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    __hash__: ClassVar[None] = None  # type: ignore[assignment]
    # def __class_getitem__(cls, item: Any, /) -> GenericAlias: raise AssumedToBeImplementedException


# @disjoint_base
# class frozenset(IsAbstractSet[_T_co]):
class IsFrozenSet(IsAbstractSet[_T_co], Protocol[_T_co]):  # type: ignore[misc]
    """Define the ``IsFrozenSet`` interface.
    """
    # @overload
    # def __new__(cls) -> Self:
    #     raise AssumedToBeImplementedException
    # @overload
    # def __new__(cls, iterable: Iterable[_T_co], /) -> Self:
    #     raise AssumedToBeImplementedException

    # def copy(self) -> frozenset[_T_co]: raise AssumedToBeImplementedException
    def difference(self, *s: Iterable[object]) -> frozenset[_T_co]: raise AssumedToBeImplementedException
    def intersection(self, *s: Iterable[object]) -> frozenset[_T_co]: raise AssumedToBeImplementedException
    def isdisjoint(self, s: Iterable[object], /) -> bool: raise AssumedToBeImplementedException
    def issubset(self, s: Iterable[object], /) -> bool: raise AssumedToBeImplementedException
    def issuperset(self, s: Iterable[object], /) -> bool: raise AssumedToBeImplementedException
    def symmetric_difference(self, s: Iterable[_S], /) -> frozenset[_T_co | _S]: raise AssumedToBeImplementedException
    def union(self, *s: Iterable[_S]) -> frozenset[_T_co | _S]: raise AssumedToBeImplementedException
    def __len__(self) -> int: raise AssumedToBeImplementedException
    def __contains__(self, o: object, /) -> bool: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[_T_co]: raise AssumedToBeImplementedException
    def __and__(self, value: AbstractSet[object], /) -> frozenset[_T_co]: raise AssumedToBeImplementedException
    def __or__(self, value: AbstractSet[_S], /) -> frozenset[_T_co | _S]: raise AssumedToBeImplementedException
    def __sub__(self, value: AbstractSet[object], /) -> frozenset[_T_co]: raise AssumedToBeImplementedException
    def __xor__(self, value: AbstractSet[_S], /) -> frozenset[_T_co | _S]: raise AssumedToBeImplementedException
    def __le__(self, value: AbstractSet[object], /) -> bool: raise AssumedToBeImplementedException
    def __lt__(self, value: AbstractSet[object], /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, value: AbstractSet[object], /) -> bool: raise AssumedToBeImplementedException
    def __gt__(self, value: AbstractSet[object], /) -> bool: raise AssumedToBeImplementedException
    def __eq__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __hash__(self) -> int: raise AssumedToBeImplementedException
    # def __class_getitem__(cls, item: Any, /) -> GenericAlias: raise AssumedToBeImplementedException
#
# @disjoint_base
# class enumerate(Generic[_T]):
#     def __new__(cls, iterable: Iterable[_T], start: int = 0) -> Self: ...
#     def __iter__(self) -> Self: ...
#     def __next__(self) -> tuple[int, _T]: ...
#     def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...
#
# @final
# class range(Sequence[int]):
#     @property
#     def start(self) -> int: ...
#     @property
#     def stop(self) -> int: ...
#     @property
#     def step(self) -> int: ...
#
#     @overload
#     def __new__(cls, stop: SupportsIndex, /) -> Self: ...
#     @overload
#     def __new__(cls, start: SupportsIndex, stop: SupportsIndex, step: SupportsIndex = 1, /) -> Self: ...
#
#     def count(self, value: int, /) -> int: ...
#     def index(self, value: int, /) -> int: ...  # type: ignore[override]
#     def __len__(self) -> int: ...
#     def __eq__(self, value: object, /) -> bool: ...
#     def __hash__(self) -> int: ...
#     def __contains__(self, key: object, /) -> bool: ...
#     def __iter__(self) -> Iterator[int]: ...
#
#     @overload
#     def __getitem__(self, key: SupportsIndex, /) -> int: ...
#     @overload
#     def __getitem__(self, key: slice[SupportsIndex | None], /) -> range: ...
#
#     def __reversed__(self) -> Iterator[int]: ...
#
# @disjoint_base
# class property:
#     fget: Callable[[Any], Any] | None
#     fset: Callable[[Any, Any], None] | None
#     fdel: Callable[[Any], None] | None
#     __isabstractmethod__: bool
#     if sys.version_info >= (3, 13):
#         __name__: str
#
#     def __init__(
#         self,
#         fget: Callable[[Any], Any] | None = None,
#         fset: Callable[[Any, Any], None] | None = None,
#         fdel: Callable[[Any], None] | None = None,
#         doc: str | None = None,
#     ) -> None: ...
#     def getter(self, fget: Callable[[Any], Any], /) -> property: ...
#     def setter(self, fset: Callable[[Any, Any], None], /) -> property: ...
#     def deleter(self, fdel: Callable[[Any], None], /) -> property: ...
#
#     @overload
#     def __get__(self, instance: None, owner: type, /) -> Self: ...
#     @overload
#     def __get__(self, instance: Any, owner: type | None = None, /) -> Any: ...
#
#     def __set__(self, instance: Any, value: Any, /) -> None: ...
#     def __delete__(self, instance: Any, /) -> None: ...
#
# def abs(x: SupportsAbs[_T], /) -> _T: ...
# def all(iterable: Iterable[object], /) -> bool: ...
# def any(iterable: Iterable[object], /) -> bool: ...
# def ascii(obj: object, /) -> str: ...
#
# if sys.version_info >= (3, 15):
#     def bin(integer: SupportsIndex, /) -> str: ...
#
# else:
#     def bin(number: SupportsIndex, /) -> str: ...
#
# def breakpoint(*args: Any, **kws: Any) -> None: ...
# def callable(obj: object, /) -> TypeIs[Callable[..., object]]: ...
# def chr(i: SupportsIndex, /) -> str: ...
# def aiter(async_iterable: SupportsAiter[_SupportsAnextT_co], /) -> _SupportsAnextT_co: ...
#
# @type_check_only
# class _SupportsSynchronousAnext(Protocol[_AwaitableT_co]):
#     def __anext__(self) -> _AwaitableT_co: ...
#
# @overload
# # `anext` is not, in fact, an async function. When default is not provided
# # `anext` is just a passthrough for `obj.__anext__`
# # See discussion in #7491 and pure-Python implementation of `anext` at https://github.com/python/cpython/blob/ea786a882b9ed4261eafabad6011bc7ef3b5bf94/Lib/test/test_asyncgen.py#L52-L80
# def anext(i: _SupportsSynchronousAnext[_AwaitableT], /) -> _AwaitableT: ...
# @overload
# async def anext(i: SupportsAnext[_T], default: _VT, /) -> _T | _VT: ...
#
# # compile() returns a CodeType, unless the flags argument includes PyCF_ONLY_AST (=1024),
# # in which case it returns ast.AST. We have overloads for flag 0 (the default) and for
# # explicitly passing PyCF_ONLY_AST. We fall back to Any for other values of flags.
# if sys.version_info >= (3, 15):
#     @overload
#     def compile(
#         source: str | ReadableBuffer | _ast.Module | _ast.Expression | _ast.Interactive,
#         filename: str | bytes | PathLike[Any],
#         mode: str,
#         flags: Literal[0],
#         dont_inherit: bool = False,
#         optimize: int = -1,
#         *,
#         module: str | None = None,
#         _feature_version: int = -1,
#     ) -> CodeType: ...
#     @overload
#     def compile(
#         source: str | ReadableBuffer | _ast.Module | _ast.Expression | _ast.Interactive,
#         filename: str | bytes | PathLike[Any],
#         mode: str,
#         *,
#         dont_inherit: bool = False,
#         optimize: int = -1,
#         module: str | None = None,
#         _feature_version: int = -1,
#     ) -> CodeType: ...
#     @overload
#     def compile(
#         source: str | ReadableBuffer | _ast.Module | _ast.Expression | _ast.Interactive,
#         filename: str | bytes | PathLike[Any],
#         mode: str,
#         flags: Literal[1024],
#         dont_inherit: bool = False,
#         optimize: int = -1,
#         *,
#         module: str | None = None,
#         _feature_version: int = -1,
#     ) -> _ast.AST: ...
#     @overload
#     def compile(
#         source: str | ReadableBuffer | _ast.Module | _ast.Expression | _ast.Interactive,
#         filename: str | bytes | PathLike[Any],
#         mode: str,
#         flags: int,
#         dont_inherit: bool = False,
#         optimize: int = -1,
#         *,
#         module: str | None = None,
#         _feature_version: int = -1,
#     ) -> Any: ...
# else:
#     @overload
#     def compile(
#         source: str | ReadableBuffer | _ast.Module | _ast.Expression | _ast.Interactive,
#         filename: str | bytes | PathLike[Any],
#         mode: str,
#         flags: Literal[0],
#         dont_inherit: bool = False,
#         optimize: int = -1,
#         *,
#         _feature_version: int = -1,
#     ) -> CodeType: ...
#     @overload
#     def compile(
#         source: str | ReadableBuffer | _ast.Module | _ast.Expression | _ast.Interactive,
#         filename: str | bytes | PathLike[Any],
#         mode: str,
#         *,
#         dont_inherit: bool = False,
#         optimize: int = -1,
#         _feature_version: int = -1,
#     ) -> CodeType: ...
#     @overload
#     def compile(
#         source: str | ReadableBuffer | _ast.Module | _ast.Expression | _ast.Interactive,
#         filename: str | bytes | PathLike[Any],
#         mode: str,
#         flags: Literal[1024],
#         dont_inherit: bool = False,
#         optimize: int = -1,
#         *,
#         _feature_version: int = -1,
#     ) -> _ast.AST: ...
#     @overload
#     def compile(
#         source: str | ReadableBuffer | _ast.Module | _ast.Expression | _ast.Interactive,
#         filename: str | bytes | PathLike[Any],
#         mode: str,
#         flags: int,
#         dont_inherit: bool = False,
#         optimize: int = -1,
#         *,
#         _feature_version: int = -1,
#     ) -> Any: ...
#
# copyright: _sitebuiltins._Printer
# credits: _sitebuiltins._Printer
#
# def delattr(obj: object, name: str, /) -> None: ...
# def dir(o: object = ..., /) -> list[str]: ...
#
# @overload
# def divmod(x: SupportsDivMod[_T_contra, _T_co], y: _T_contra, /) -> _T_co: ...
# @overload
# def divmod(x: _T_contra, y: SupportsRDivMod[_T_contra, _T_co], /) -> _T_co: ...
#
# # The `globals` argument to `eval` has to be `dict[str, Any]` rather than `dict[str, object]` due to invariance.
# # (The `globals` argument has to be a "real dict", rather than any old mapping, unlike the `locals` argument.)
# if sys.version_info >= (3, 15):
#     def eval(
#         source: str | ReadableBuffer | CodeType,
#         /,
#         globals: dict[str, Any] | frozendict[str, Any] | None = None,
#         locals: Mapping[str, object] | None = None,
#     ) -> Any: ...
#
# elif sys.version_info >= (3, 13):
#     def eval(
#         source: str | ReadableBuffer | CodeType,
#         /,
#         globals: dict[str, Any] | None = None,
#         locals: Mapping[str, object] | None = None,
#     ) -> Any: ...
#
# else:
#     def eval(
#         source: str | ReadableBuffer | CodeType,
#         globals: dict[str, Any] | None = None,
#         locals: Mapping[str, object] | None = None,
#         /,
#     ) -> Any: ...
#
# # Comment above regarding `eval` applies to `exec` as well
# if sys.version_info >= (3, 15):
#     def exec(
#         source: str | ReadableBuffer | CodeType,
#         /,
#         globals: dict[str, Any] | frozendict[str, Any] | None = None,
#         locals: Mapping[str, object] | None = None,
#         *,
#         closure: tuple[CellType, ...] | None = None,
#     ) -> None: ...
#
# elif sys.version_info >= (3, 13):
#     def exec(
#         source: str | ReadableBuffer | CodeType,
#         /,
#         globals: dict[str, Any] | None = None,
#         locals: Mapping[str, object] | None = None,
#         *,
#         closure: tuple[CellType, ...] | None = None,
#     ) -> None: ...
#
# elif sys.version_info >= (3, 11):
#     def exec(
#         source: str | ReadableBuffer | CodeType,
#         globals: dict[str, Any] | None = None,
#         locals: Mapping[str, object] | None = None,
#         /,
#         *,
#         closure: tuple[CellType, ...] | None = None,
#     ) -> None: ...
#
# else:
#     def exec(
#         source: str | ReadableBuffer | CodeType,
#         globals: dict[str, Any] | None = None,
#         locals: Mapping[str, object] | None = None,
#         /,
#     ) -> None: ...
#
# exit: _sitebuiltins.Quitter
#
# @disjoint_base
# class filter(Generic[_T]):
#     @overload
#     def __new__(cls, function: None, iterable: Iterable[_T | None], /) -> Self: ...
#     @overload
#     def __new__(cls, function: Callable[[_S], TypeGuard[_T]], iterable: Iterable[_S], /) -> Self: ...
#     @overload
#     def __new__(cls, function: Callable[[_S], TypeIs[_T]], iterable: Iterable[_S], /) -> Self: ...
#     @overload
#     def __new__(cls, function: Callable[[_T], Any], iterable: Iterable[_T], /) -> Self: ...
#
#     def __iter__(self) -> Self: ...
#     def __next__(self) -> _T: ...
#
# def format(value: object, format_spec: str = "", /) -> str: ...
#
# @overload
# def getattr(o: object, name: str, /) -> Any: ...
#
# # While technically covered by the last overload, spelling out the types for None, bool
# # and basic containers help mypy out in some tricky situations involving type context
# # (aka bidirectional inference)
# @overload
# def getattr(o: object, name: str, default: None, /) -> Any | None: ...
# @overload
# def getattr(o: object, name: str, default: bool, /) -> Any | bool: ...
# @overload
# def getattr(o: object, name: str, default: list[Any], /) -> Any | list[Any]: ...
# @overload
# def getattr(o: object, name: str, default: dict[Any, Any], /) -> Any | dict[Any, Any]: ...
# @overload
# def getattr(o: object, name: str, default: _T, /) -> Any | _T: ...
#
# def globals() -> dict[str, Any]: ...
# def hasattr(obj: object, name: str, /) -> bool: ...
# def hash(obj: object, /) -> int: ...
#
# help: _sitebuiltins._Helper
#
# if sys.version_info >= (3, 15):
#     def hex(integer: SupportsIndex, /) -> str: ...
#
# else:
#     def hex(number: SupportsIndex, /) -> str: ...
#
# def id(obj: object, /) -> int: ...
# def input(prompt: object = "", /) -> str: ...
#
# @type_check_only
# class _GetItemIterable(Protocol[_T_co]):
#     def __getitem__(self, i: int, /) -> _T_co: ...
#
# @overload
# def iter(object: SupportsIter[_SupportsNextT_co], /) -> _SupportsNextT_co: ...
# @overload
# def iter(object: _GetItemIterable[_T], /) -> Iterator[_T]: ...
# @overload
# def iter(object: Callable[[], _T | None], sentinel: None, /) -> Iterator[_T]: ...
# @overload
# def iter(object: Callable[[], _T], sentinel: object, /) -> Iterator[_T]: ...
#
# _ClassInfo: TypeAlias = type | types.UnionType | tuple[_ClassInfo, ...]
#
# def isinstance(obj: object, class_or_tuple: _ClassInfo, /) -> bool: ...
# def issubclass(cls: type, class_or_tuple: _ClassInfo, /) -> bool: ...
# def len(obj: Sized, /) -> int: ...
#
# license: _sitebuiltins._Printer
#
# def locals() -> dict[str, Any]: ...
#
# @disjoint_base
# class map(Generic[_S]):
#     # 3.14 adds `strict` argument.
#     if sys.version_info >= (3, 14):
#         @overload
#         def __new__(cls, func: Callable[[_T1], _S], iterable: Iterable[_T1], /, *, strict: bool = False) -> Self: ...
#         @overload
#         def __new__(
#             cls, func: Callable[[_T1, _T2], _S], iterable: Iterable[_T1], iter2: Iterable[_T2], /, *, strict: bool = False
#         ) -> Self: ...
#         @overload
#         def __new__(
#             cls,
#             func: Callable[[_T1, _T2, _T3], _S],
#             iterable: Iterable[_T1],
#             iter2: Iterable[_T2],
#             iter3: Iterable[_T3],
#             /,
#             *,
#             strict: bool = False,
#         ) -> Self: ...
#         @overload
#         def __new__(
#             cls,
#             func: Callable[[_T1, _T2, _T3, _T4], _S],
#             iterable: Iterable[_T1],
#             iter2: Iterable[_T2],
#             iter3: Iterable[_T3],
#             iter4: Iterable[_T4],
#             /,
#             *,
#             strict: bool = False,
#         ) -> Self: ...
#         @overload
#         def __new__(
#             cls,
#             func: Callable[[_T1, _T2, _T3, _T4, _T5], _S],
#             iterable: Iterable[_T1],
#             iter2: Iterable[_T2],
#             iter3: Iterable[_T3],
#             iter4: Iterable[_T4],
#             iter5: Iterable[_T5],
#             /,
#             *,
#             strict: bool = False,
#         ) -> Self: ...
#         @overload
#         def __new__(
#             cls,
#             func: Callable[..., _S],
#             iterable: Iterable[Any],
#             iter2: Iterable[Any],
#             iter3: Iterable[Any],
#             iter4: Iterable[Any],
#             iter5: Iterable[Any],
#             iter6: Iterable[Any],
#             /,
#             *iterables: Iterable[Any],
#             strict: bool = False,
#         ) -> Self: ...
#     else:
#         @overload
#         def __new__(cls, func: Callable[[_T1], _S], iterable: Iterable[_T1], /) -> Self: ...
#         @overload
#         def __new__(cls, func: Callable[[_T1, _T2], _S], iterable: Iterable[_T1], iter2: Iterable[_T2], /) -> Self: ...
#         @overload
#         def __new__(
#             cls, func: Callable[[_T1, _T2, _T3], _S], iterable: Iterable[_T1], iter2: Iterable[_T2], iter3: Iterable[_T3], /
#         ) -> Self: ...
#         @overload
#         def __new__(
#             cls,
#             func: Callable[[_T1, _T2, _T3, _T4], _S],
#             iterable: Iterable[_T1],
#             iter2: Iterable[_T2],
#             iter3: Iterable[_T3],
#             iter4: Iterable[_T4],
#             /,
#         ) -> Self: ...
#         @overload
#         def __new__(
#             cls,
#             func: Callable[[_T1, _T2, _T3, _T4, _T5], _S],
#             iterable: Iterable[_T1],
#             iter2: Iterable[_T2],
#             iter3: Iterable[_T3],
#             iter4: Iterable[_T4],
#             iter5: Iterable[_T5],
#             /,
#         ) -> Self: ...
#         @overload
#         def __new__(
#             cls,
#             func: Callable[..., _S],
#             iterable: Iterable[Any],
#             iter2: Iterable[Any],
#             iter3: Iterable[Any],
#             iter4: Iterable[Any],
#             iter5: Iterable[Any],
#             iter6: Iterable[Any],
#             /,
#             *iterables: Iterable[Any],
#         ) -> Self: ...
#
#     def __iter__(self) -> Self: ...
#     def __next__(self) -> _S: ...
#
# @overload
# def max(
#     arg1: SupportsRichComparisonT, arg2: SupportsRichComparisonT, /, *_args: SupportsRichComparisonT, key: None = None
# ) -> SupportsRichComparisonT: ...
# @overload
# def max(arg1: _T, arg2: _T, /, *_args: _T, key: Callable[[_T], SupportsRichComparison]) -> _T: ...
# @overload
# def max(iterable: Iterable[SupportsRichComparisonT], /, *, key: None = None) -> SupportsRichComparisonT: ...
# @overload
# def max(iterable: Iterable[_T], /, *, key: Callable[[_T], SupportsRichComparison]) -> _T: ...
# @overload
# def max(iterable: Iterable[SupportsRichComparisonT], /, *, key: None = None, default: _T) -> SupportsRichComparisonT | _T: ...
# @overload
# def max(iterable: Iterable[_T1], /, *, key: Callable[[_T1], SupportsRichComparison], default: _T2) -> _T1 | _T2: ...
#
# @overload
# def min(
#     arg1: SupportsRichComparisonT, arg2: SupportsRichComparisonT, /, *_args: SupportsRichComparisonT, key: None = None
# ) -> SupportsRichComparisonT: ...
# @overload
# def min(arg1: _T, arg2: _T, /, *_args: _T, key: Callable[[_T], SupportsRichComparison]) -> _T: ...
# @overload
# def min(iterable: Iterable[SupportsRichComparisonT], /, *, key: None = None) -> SupportsRichComparisonT: ...
# @overload
# def min(iterable: Iterable[_T], /, *, key: Callable[[_T], SupportsRichComparison]) -> _T: ...
# @overload
# def min(iterable: Iterable[SupportsRichComparisonT], /, *, key: None = None, default: _T) -> SupportsRichComparisonT | _T: ...
# @overload
# def min(iterable: Iterable[_T1], /, *, key: Callable[[_T1], SupportsRichComparison], default: _T2) -> _T1 | _T2: ...
#
# @overload
# def next(i: SupportsNext[_T], /) -> _T: ...
# @overload
# def next(i: SupportsNext[_T], default: _VT, /) -> _T | _VT: ...
#
# if sys.version_info >= (3, 15):
#     def oct(integer: SupportsIndex, /) -> str: ...
#
# else:
#     def oct(number: SupportsIndex, /) -> str: ...
#
# _Opener: TypeAlias = Callable[[str, int], int]
#
# # Text mode: always returns a TextIOWrapper
# @overload
# def open(
#     file: FileDescriptorOrPath,
#     mode: OpenTextMode = "r",
#     buffering: int = -1,
#     encoding: str | None = None,
#     errors: str | None = None,
#     newline: str | None = None,
#     closefd: bool = True,
#     opener: _Opener | None = None,
# ) -> TextIOWrapper: ...
#
# # Unbuffered binary mode: returns a FileIO
# @overload
# def open(
#     file: FileDescriptorOrPath,
#     mode: OpenBinaryMode,
#     buffering: Literal[0],
#     encoding: None = None,
#     errors: None = None,
#     newline: None = None,
#     closefd: bool = True,
#     opener: _Opener | None = None,
# ) -> FileIO: ...
#
# # Buffering is on: return BufferedRandom, BufferedReader, or BufferedWriter
# @overload
# def open(
#     file: FileDescriptorOrPath,
#     mode: OpenBinaryModeUpdating,
#     buffering: Literal[-1, 1] = -1,
#     encoding: None = None,
#     errors: None = None,
#     newline: None = None,
#     closefd: bool = True,
#     opener: _Opener | None = None,
# ) -> BufferedRandom: ...
# @overload
# def open(
#     file: FileDescriptorOrPath,
#     mode: OpenBinaryModeWriting,
#     buffering: Literal[-1, 1] = -1,
#     encoding: None = None,
#     errors: None = None,
#     newline: None = None,
#     closefd: bool = True,
#     opener: _Opener | None = None,
# ) -> BufferedWriter: ...
# @overload
# def open(
#     file: FileDescriptorOrPath,
#     mode: OpenBinaryModeReading,
#     buffering: Literal[-1, 1] = -1,
#     encoding: None = None,
#     errors: None = None,
#     newline: None = None,
#     closefd: bool = True,
#     opener: _Opener | None = None,
# ) -> BufferedReader: ...
#
# # Buffering cannot be determined: fall back to BinaryIO
# @overload
# def open(
#     file: FileDescriptorOrPath,
#     mode: OpenBinaryMode,
#     buffering: int = -1,
#     encoding: None = None,
#     errors: None = None,
#     newline: None = None,
#     closefd: bool = True,
#     opener: _Opener | None = None,
# ) -> BinaryIO: ...
#
# # Fallback if mode is not specified
# @overload
# def open(
#     file: FileDescriptorOrPath,
#     mode: str,
#     buffering: int = -1,
#     encoding: str | None = None,
#     errors: str | None = None,
#     newline: str | None = None,
#     closefd: bool = True,
#     opener: _Opener | None = None,
# ) -> IO[Any]: ...
#
# def ord(c: str | bytes | bytearray, /) -> int: ...
#
# @type_check_only
# class _SupportsWriteAndFlush(SupportsWrite[_T_contra], SupportsFlush, Protocol[_T_contra]): ...
#
# @overload
# def print(
#     *values: object,
#     sep: str | None = " ",
#     end: str | None = "\n",
#     file: SupportsWrite[str] | None = None,
#     flush: Literal[False] = False,
# ) -> None: ...
# @overload
# def print(
#     *values: object, sep: str | None = " ", end: str | None = "\n", file: _SupportsWriteAndFlush[str] | None = None, flush: bool
# ) -> None: ...
#
# _E_contra = TypeVar("_E_contra", contravariant=True)
# _M_contra = TypeVar("_M_contra", contravariant=True)
#
# @type_check_only
# class _SupportsPow2(Protocol[_E_contra, _T_co]):
#     def __pow__(self, other: _E_contra, /) -> _T_co: ...
#
# @type_check_only
# class _SupportsPow3NoneOnly(Protocol[_E_contra, _T_co]):
#     def __pow__(self, other: _E_contra, modulo: None = None, /) -> _T_co: ...
#
# @type_check_only
# class _SupportsPow3(Protocol[_E_contra, _M_contra, _T_co]):
#     def __pow__(self, other: _E_contra, modulo: _M_contra, /) -> _T_co: ...
#
# _SupportsSomeKindOfPow = (  # noqa: Y026  # TODO: Use TypeAlias once mypy bugs are fixed
#     _SupportsPow2[Any, Any] | _SupportsPow3NoneOnly[Any, Any] | _SupportsPow3[Any, Any, Any]
# )
#
# # TODO: `pow(int, int, Literal[0])` fails at runtime,
# # but adding a `NoReturn` overload isn't a good solution for expressing that (see #8566).
# @overload
# def pow(base: int, exp: int, mod: int) -> int: ...
# @overload
# def pow(base: int, exp: Literal[0], mod: None = None) -> Literal[1]: ...
# @overload
# def pow(base: int, exp: _PositiveInteger, mod: None = None) -> int: ...
# @overload
# def pow(base: int, exp: _NegativeInteger, mod: None = None) -> float: ...
#
# # int base & positive-int exp -> int; int base & negative-int exp -> float
# # return type must be Any as `int | float` causes too many false-positive errors
# @overload
# def pow(base: int, exp: int, mod: None = None) -> Any: ...
# @overload
# def pow(base: _PositiveInteger, exp: float, mod: None = None) -> float: ...
# @overload
# def pow(base: _NegativeInteger, exp: float, mod: None = None) -> complex: ...
# @overload
# def pow(base: float, exp: int, mod: None = None) -> float: ...
#
# # float base & float exp could return float or complex
# # return type must be Any (same as complex base, complex exp),
# # as `float | complex` causes too many false-positive errors
# @overload
# def pow(base: float, exp: complex | _SupportsSomeKindOfPow, mod: None = None) -> Any: ...
# @overload
# def pow(base: complex, exp: complex | _SupportsSomeKindOfPow, mod: None = None) -> complex: ...
# @overload
# def pow(base: _SupportsPow2[_E_contra, _T_co], exp: _E_contra, mod: None = None) -> _T_co: ...  # type: ignore[overload-overlap]
# @overload
# def pow(base: _SupportsPow3NoneOnly[_E_contra, _T_co], exp: _E_contra, mod: None = None) -> _T_co: ...  # type: ignore[overload-overlap]
# @overload
# def pow(base: _SupportsPow3[_E_contra, _M_contra, _T_co], exp: _E_contra, mod: _M_contra) -> _T_co: ...
# @overload
# def pow(base: _SupportsSomeKindOfPow, exp: float, mod: None = None) -> Any: ...
# @overload
# def pow(base: _SupportsSomeKindOfPow, exp: complex, mod: None = None) -> complex: ...
#
# quit: _sitebuiltins.Quitter
#
# @disjoint_base
# class reversed(Generic[_T]):
#     @overload
#     def __new__(cls, sequence: Reversible[_T], /) -> Iterator[_T]: ...  # type: ignore[misc]
#     @overload
#     def __new__(cls, sequence: SupportsLenAndGetItem[_T], /) -> Iterator[_T]: ...  # type: ignore[misc]
#
#     def __iter__(self) -> Self: ...
#     def __next__(self) -> _T: ...
#     def __length_hint__(self) -> int: ...
#
# def repr(obj: object, /) -> str: ...
#
# # See https://github.com/python/typeshed/pull/9141
# # and https://github.com/python/typeshed/pull/9151
# # on why we don't use `SupportsRound` from `typing.pyi`
#
# @type_check_only
# class _SupportsRound1(Protocol[_T_co]):
#     def __round__(self) -> _T_co: ...
#
# @type_check_only
# class _SupportsRound2(Protocol[_T_co]):
#     def __round__(self, ndigits: int, /) -> _T_co: ...
#
# @overload
# def round(number: _SupportsRound1[_T], ndigits: None = None) -> _T: ...
# @overload
# def round(number: _SupportsRound2[_T], ndigits: SupportsIndex) -> _T: ...
#
# # See https://github.com/python/typeshed/pull/6292#discussion_r748875189
# # for why arg 3 of `setattr` should be annotated with `Any` and not `object`
# def setattr(obj: object, name: str, value: Any, /) -> None: ...
#
# if sys.version_info >= (3, 15):
#     @final
#     class sentinel:
#         __name__: str
#         __module__: str
#         def __new__(cls, name: str, /) -> Self: ...
#         def __copy__(self, /) -> Self: ...
#         def __deepcopy__(self, memo: Any, /) -> Self: ...
#         def __or__(self, other: Any, /) -> Any: ...
#         def __ror__(self, other: Any, /) -> Any: ...
#
# @overload
# def sorted(
#     iterable: Iterable[SupportsRichComparisonT], /, *, key: None = None, reverse: bool = False
# ) -> list[SupportsRichComparisonT]: ...
# @overload
# def sorted(iterable: Iterable[_T], /, *, key: Callable[[_T], SupportsRichComparison], reverse: bool = False) -> list[_T]: ...
#
# _AddableT1 = TypeVar("_AddableT1", bound=SupportsAdd[Any, Any])
# _AddableT2 = TypeVar("_AddableT2", bound=SupportsAdd[Any, Any])
#
# @type_check_only
# class _SupportsSumWithNoDefaultGiven(SupportsAdd[Any, Any], SupportsRAdd[int, Any], Protocol): ...
#
# _SupportsSumNoDefaultT = TypeVar("_SupportsSumNoDefaultT", bound=_SupportsSumWithNoDefaultGiven)
#
# # In general, the return type of `x + x` is *not* guaranteed to be the same type as x.
# # However, we can't express that in the stub for `sum()`
# # without creating many false-positive errors (see #7578).
# # Instead, we special-case the most common examples of this: bool and literal integers.
# @overload
# def sum(iterable: Iterable[bool | _LiteralInteger], /, start: int = 0) -> int: ...
# @overload
# def sum(iterable: Iterable[_SupportsSumNoDefaultT], /) -> _SupportsSumNoDefaultT | Literal[0]: ...
# @overload
# def sum(iterable: Iterable[_AddableT1], /, start: _AddableT2) -> _AddableT1 | _AddableT2: ...
#
# # The argument to `vars()` has to have a `__dict__` attribute, so the second overload can't be annotated with `object`
# # (A "SupportsDunderDict" protocol doesn't work)
# @overload
# def vars(object: type, /) -> types.MappingProxyType[str, Any]: ...
# @overload
# def vars(object: Any = ..., /) -> dict[str, Any]: ...
#
# @disjoint_base
# class zip(Generic[_T_co]):
#     @overload
#     def __new__(cls, *, strict: bool = False) -> zip[Any]: ...
#     @overload
#     def __new__(cls, iter1: Iterable[_T1], /, *, strict: bool = False) -> zip[tuple[_T1]]: ...
#     @overload
#     def __new__(cls, iter1: Iterable[_T1], iter2: Iterable[_T2], /, *, strict: bool = False) -> zip[tuple[_T1, _T2]]: ...
#     @overload
#     def __new__(
#         cls, iter1: Iterable[_T1], iter2: Iterable[_T2], iter3: Iterable[_T3], /, *, strict: bool = False
#     ) -> zip[tuple[_T1, _T2, _T3]]: ...
#     @overload
#     def __new__(
#         cls, iter1: Iterable[_T1], iter2: Iterable[_T2], iter3: Iterable[_T3], iter4: Iterable[_T4], /, *, strict: bool = False
#     ) -> zip[tuple[_T1, _T2, _T3, _T4]]: ...
#     @overload
#     def __new__(
#         cls,
#         iter1: Iterable[_T1],
#         iter2: Iterable[_T2],
#         iter3: Iterable[_T3],
#         iter4: Iterable[_T4],
#         iter5: Iterable[_T5],
#         /,
#         *,
#         strict: bool = False,
#     ) -> zip[tuple[_T1, _T2, _T3, _T4, _T5]]: ...
#     @overload
#     def __new__(
#         cls,
#         iter1: Iterable[Any],
#         iter2: Iterable[Any],
#         iter3: Iterable[Any],
#         iter4: Iterable[Any],
#         iter5: Iterable[Any],
#         iter6: Iterable[Any],
#         /,
#         *iterables: Iterable[Any],
#         strict: bool = False,
#     ) -> zip[tuple[Any, ...]]: ...
#
#     def __iter__(self) -> Self: ...
#     def __next__(self) -> _T_co: ...
#
# # Signature of `builtins.__import__` should be kept identical to `importlib.__import__`
# # Return type of `__import__` should be kept the same as return type of `importlib.import_module`
# def __import__(
#     name: str,
#     globals: Mapping[str, object] | None = None,
#     locals: Mapping[str, object] | None = None,
#     fromlist: Sequence[str] | None = (),
#     level: int = 0,
# ) -> types.ModuleType: ...
#
# if sys.version_info >= (3, 15):
#     def __lazy_import__(
#         name: str,
#         globals: Mapping[str, object] | None = None,
#         locals: Mapping[str, object] | None = None,
#         fromlist: Sequence[str] | None = (),
#         level: int = 0,
#     ) -> Any: ...
#
# def __build_class__(func: Callable[[], CellType | Any], name: str, /, *bases: Any, metaclass: Any = ..., **kwds: Any) -> Any: ...
#
# # Backwards compatibility hack for folks who relied on the ellipsis type
# # existing in typeshed in Python 3.9 and earlier.
# ellipsis = EllipsisType
#
# Ellipsis: EllipsisType
# NotImplemented: NotImplementedType
#
# @disjoint_base
# class BaseException:
#     args: tuple[Any, ...]
#     __cause__: BaseException | None
#     __context__: BaseException | None
#     __suppress_context__: bool
#     __traceback__: TracebackType | None
#     def __init__(self, *args: object) -> None: ...
#     def __new__(cls, *args: Any, **kwds: Any) -> Self: ...
#     def __setstate__(self, state: dict[str, Any] | None, /) -> None: ...
#     def with_traceback(self, tb: TracebackType | None, /) -> Self: ...
#     # Necessary for security-focused static analyzers (e.g, pysa)
#     # See https://github.com/python/typeshed/pull/14900
#     def __str__(self) -> str: ...  # noqa: Y029
#     def __repr__(self) -> str: ...  # noqa: Y029
#     if sys.version_info >= (3, 11):
#         # only present after add_note() is called
#         __notes__: list[str]
#         def add_note(self, note: str, /) -> None: ...
#
# class GeneratorExit(BaseException): ...
# class KeyboardInterrupt(BaseException): ...
#
# @disjoint_base
# class SystemExit(BaseException):
#     code: sys._ExitCode
#
# class Exception(BaseException): ...
#
# @disjoint_base
# class StopIteration(Exception):
#     value: Any
#
# @disjoint_base
# class OSError(Exception):
#     errno: int | None
#     strerror: str | None
#     # filename, filename2 are actually str | bytes | None
#     filename: Any
#     filename2: Any
#     if sys.platform == "win32":
#         winerror: int
#
# EnvironmentError = OSError
# IOError = OSError
# if sys.platform == "win32":
#     WindowsError = OSError
#
# class ArithmeticError(Exception): ...
# class AssertionError(Exception): ...
#
# @disjoint_base
# class AttributeError(Exception):
#     def __init__(self, *args: object, name: str | None = None, obj: object = None) -> None: ...
#     name: str | None
#     obj: object
#
# class BufferError(Exception): ...
# class EOFError(Exception): ...
#
# @disjoint_base
# class ImportError(Exception):
#     def __init__(self, *args: object, name: str | None = None, path: str | None = None) -> None: ...
#     name: str | None
#     path: str | None
#     msg: str  # undocumented
#     if sys.version_info >= (3, 12):
#         name_from: str | None  # undocumented
#
# if sys.version_info >= (3, 15):
#     class ImportCycleError(ImportError): ...
#
# class LookupError(Exception): ...
# class MemoryError(Exception): ...
#
# @disjoint_base
# class NameError(Exception):
#     def __init__(self, *args: object, name: str | None = None) -> None: ...
#     name: str | None
#
# class ReferenceError(Exception): ...
# class RuntimeError(Exception): ...
# class StopAsyncIteration(Exception): ...
#
# @disjoint_base
# class SyntaxError(Exception):
#     msg: str
#     filename: str | None
#     lineno: int | None
#     offset: int | None
#     text: str | None
#     # Errors are displayed differently if this attribute exists on the exception.
#     # The value is always None.
#     print_file_and_line: None
#     end_lineno: int | None
#     end_offset: int | None
#
#     @overload
#     def __init__(self) -> None: ...
#     @overload
#     def __init__(self, msg: object, /) -> None: ...
#     # Second argument is the tuple (filename, lineno, offset, text)
#     @overload
#     def __init__(self, msg: str, info: tuple[str | None, int | None, int | None, str | None], /) -> None: ...
#     # end_lineno and end_offset must both be provided if one is.
#     @overload
#     def __init__(
#         self, msg: str, info: tuple[str | None, int | None, int | None, str | None, int | None, int | None], /
#     ) -> None: ...
#     # If you provide more than two arguments, it still creates the SyntaxError, but
#     # the arguments from the info tuple are not parsed. This form is omitted.
#
# class SystemError(Exception): ...
# class TypeError(Exception): ...
# class ValueError(Exception): ...
# class FloatingPointError(ArithmeticError): ...
# class OverflowError(ArithmeticError): ...
# class ZeroDivisionError(ArithmeticError): ...
# class ModuleNotFoundError(ImportError): ...
# class IndexError(LookupError): ...
# class KeyError(LookupError): ...
# class UnboundLocalError(NameError): ...
#
# class BlockingIOError(OSError):
#     characters_written: int
#
# class ChildProcessError(OSError): ...
# class ConnectionError(OSError): ...
# class BrokenPipeError(ConnectionError): ...
# class ConnectionAbortedError(ConnectionError): ...
# class ConnectionRefusedError(ConnectionError): ...
# class ConnectionResetError(ConnectionError): ...
# class FileExistsError(OSError): ...
# class FileNotFoundError(OSError): ...
# class InterruptedError(OSError): ...
# class IsADirectoryError(OSError): ...
# class NotADirectoryError(OSError): ...
# class PermissionError(OSError): ...
# class ProcessLookupError(OSError): ...
# class TimeoutError(OSError): ...
# class NotImplementedError(RuntimeError): ...
# class RecursionError(RuntimeError): ...
# class IndentationError(SyntaxError): ...
# class TabError(IndentationError): ...
# class UnicodeError(ValueError): ...
#
# @disjoint_base
# class UnicodeDecodeError(UnicodeError):
#     encoding: str
#     object: bytes
#     start: int
#     end: int
#     reason: str
#     def __init__(self, encoding: str, object: ReadableBuffer, start: int, end: int, reason: str, /) -> None: ...
#
# @disjoint_base
# class UnicodeEncodeError(UnicodeError):
#     encoding: str
#     object: str
#     start: int
#     end: int
#     reason: str
#     def __init__(self, encoding: str, object: str, start: int, end: int, reason: str, /) -> None: ...
#
# @disjoint_base
# class UnicodeTranslateError(UnicodeError):
#     encoding: None
#     object: str
#     start: int
#     end: int
#     reason: str
#     def __init__(self, object: str, start: int, end: int, reason: str, /) -> None: ...
#
# class Warning(Exception): ...
# class UserWarning(Warning): ...
# class DeprecationWarning(Warning): ...
# class SyntaxWarning(Warning): ...
# class RuntimeWarning(Warning): ...
# class FutureWarning(Warning): ...
# class PendingDeprecationWarning(Warning): ...
# class ImportWarning(Warning): ...
# class UnicodeWarning(Warning): ...
# class BytesWarning(Warning): ...
# class ResourceWarning(Warning): ...
# class EncodingWarning(Warning): ...
#
# if sys.version_info >= (3, 11):
#     _BaseExceptionT_co = TypeVar("_BaseExceptionT_co", bound=BaseException, covariant=True, default=BaseException)
#     _BaseExceptionT = TypeVar("_BaseExceptionT", bound=BaseException)
#     _ExceptionT_co = TypeVar("_ExceptionT_co", bound=Exception, covariant=True, default=Exception)
#     _ExceptionT = TypeVar("_ExceptionT", bound=Exception)
#
#     # See `check_exception_group.py` for use-cases and comments.
#     @disjoint_base
#     class BaseExceptionGroup(BaseException, Generic[_BaseExceptionT_co]):
#         def __new__(cls, message: str, exceptions: Sequence[_BaseExceptionT_co], /) -> Self: ...
#         def __init__(self, message: str, exceptions: Sequence[_BaseExceptionT_co], /) -> None: ...
#         @property
#         def message(self) -> str: ...
#         @property
#         def exceptions(self) -> tuple[_BaseExceptionT_co | BaseExceptionGroup[_BaseExceptionT_co], ...]: ...
#
#         @overload
#         def subgroup(
#             self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...], /
#         ) -> ExceptionGroup[_ExceptionT] | None: ...
#         @overload
#         def subgroup(
#             self, matcher_value: type[_BaseExceptionT] | tuple[type[_BaseExceptionT], ...], /
#         ) -> BaseExceptionGroup[_BaseExceptionT] | None: ...
#         @overload
#         def subgroup(
#             self, matcher_value: Callable[[_BaseExceptionT_co | Self], bool], /
#         ) -> BaseExceptionGroup[_BaseExceptionT_co] | None: ...
#
#         @overload
#         def split(
#             self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...], /
#         ) -> tuple[ExceptionGroup[_ExceptionT] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...
#         @overload
#         def split(
#             self, matcher_value: type[_BaseExceptionT] | tuple[type[_BaseExceptionT], ...], /
#         ) -> tuple[BaseExceptionGroup[_BaseExceptionT] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...
#         @overload
#         def split(
#             self, matcher_value: Callable[[_BaseExceptionT_co | Self], bool], /
#         ) -> tuple[BaseExceptionGroup[_BaseExceptionT_co] | None, BaseExceptionGroup[_BaseExceptionT_co] | None]: ...
#
#         # In reality it is `NonEmptySequence`:
#         @overload
#         def derive(self, excs: Sequence[_ExceptionT], /) -> ExceptionGroup[_ExceptionT]: ...
#         @overload
#         def derive(self, excs: Sequence[_BaseExceptionT], /) -> BaseExceptionGroup[_BaseExceptionT]: ...
#
#         def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...
#
#     class ExceptionGroup(BaseExceptionGroup[_ExceptionT_co], Exception):
#         def __new__(cls, message: str, exceptions: Sequence[_ExceptionT_co], /) -> Self: ...
#         def __init__(self, message: str, exceptions: Sequence[_ExceptionT_co], /) -> None: ...
#         @property
#         def exceptions(self) -> tuple[_ExceptionT_co | ExceptionGroup[_ExceptionT_co], ...]: ...
#
#         # We accept a narrower type, but that's OK.
#         @overload  # type: ignore[override]
#         def subgroup(
#             self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...], /
#         ) -> ExceptionGroup[_ExceptionT] | None: ...
#         @overload
#         def subgroup(
#             self, matcher_value: Callable[[_ExceptionT_co | Self], bool], /
#         ) -> ExceptionGroup[_ExceptionT_co] | None: ...
#
#         @overload  # type: ignore[override]
#         def split(
#             self, matcher_value: type[_ExceptionT] | tuple[type[_ExceptionT], ...], /
#         ) -> tuple[ExceptionGroup[_ExceptionT] | None, ExceptionGroup[_ExceptionT_co] | None]: ...
#         @overload
#         def split(
#             self, matcher_value: Callable[[_ExceptionT_co | Self], bool], /
#         ) -> tuple[ExceptionGroup[_ExceptionT_co] | None, ExceptionGroup[_ExceptionT_co] | None]: ...
#
# if sys.version_info >= (3, 13):
#     class PythonFinalizationError(RuntimeError): ...
