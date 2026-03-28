# Modified from the "builtins.py.imported" file in the same directory,
# which was imported from the Typeshed (https://github.com/python/typeshed).
#
# The Typeshed is licensed under the Apache License, Version 2.0 and the
# MIT License. See the LICENSE file in the root of the repository for
# details (https://github.com/python/typeshed/blob/main/LICENSE).
#
# See "builtins.py.imported" for more details.

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
import sys
from typing import (AbstractSet,
                    Any,
                    ClassVar,
                    overload,
                    Protocol,
                    SupportsBytes,
                    SupportsComplex,
                    SupportsFloat,
                    SupportsIndex)

from typing_extensions import deprecated, Literal, LiteralString, Self, TypeAlias, TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols._collections_abc import IsDictItems, IsDictKeys, IsDictValues
from omnipy.shared.protocols._typeshed import (ReadableBuffer,
                                               SupportsKeysAndGetItem,
                                               SupportsRichComparison,
                                               SupportsRichComparisonT)
from omnipy.shared.protocols.typing import (IsAbstractSet,
                                            IsMutableMapping,
                                            IsMutableSequence,
                                            IsMutableSet,
                                            IsSequenceNotStrBytes)

_T = TypeVar('_T')
_T_co = TypeVar('_T_co', covariant=True)
_KT = TypeVar('_KT')
_VT = TypeVar('_VT')
_S = TypeVar('_S')
_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')

_PositiveInteger: TypeAlias = Literal[1,
                                      2,
                                      3,
                                      4,
                                      5,
                                      6,
                                      7,
                                      8,
                                      9,
                                      10,
                                      11,
                                      12,
                                      13,
                                      14,
                                      15,
                                      16,
                                      17,
                                      18,
                                      19,
                                      20,
                                      21,
                                      22,
                                      23,
                                      24,
                                      25]
_NegativeInteger: TypeAlias = Literal[-1,
                                      -2,
                                      -3,
                                      -4,
                                      -5,
                                      -6,
                                      -7,
                                      -8,
                                      -9,
                                      -10,
                                      -11,
                                      -12,
                                      -13,
                                      -14,
                                      -15,
                                      -16,
                                      -17,
                                      -18,
                                      -19,
                                      -20]

# _LiteralInteger = _PositiveInteger | _NegativeInteger | Literal[
#     0]  # noqa: Y026  # FIXME: Use TypeAlias once mypy bugs are fixed


# @disjoint_base
# class int:
class IsInt(Protocol):
    """Protocol with the same interface as the builtin class `int`.
    """

    # @overload
    # def __new__(cls, x: ConvertibleToInt = 0, /) -> Self:
    #     ...
    #
    # @overload
    # def __new__(cls, x: str | bytes | bytearray, /, base: SupportsIndex) -> Self:
    #     ...

    def as_integer_ratio(self) -> tuple[int, Literal[1]]:
        raise AssumedToBeImplementedException

    @property
    def real(self) -> int:
        raise AssumedToBeImplementedException

    @property
    def imag(self) -> Literal[0]:
        raise AssumedToBeImplementedException

    @property
    def numerator(self) -> int:
        raise AssumedToBeImplementedException

    @property
    def denominator(self) -> Literal[1]:
        raise AssumedToBeImplementedException

    def conjugate(self) -> int:
        raise AssumedToBeImplementedException

    def bit_length(self) -> int:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 10):

        def bit_count(self) -> int:
            raise AssumedToBeImplementedException

    if sys.version_info >= (3, 11):

        def to_bytes(self,
                     length: SupportsIndex = 1,
                     byteorder: Literal['little', 'big'] = 'big',
                     *,
                     signed: bool = False) -> bytes:
            raise AssumedToBeImplementedException

        @classmethod
        def from_bytes(
            cls,
            bytes: Iterable[SupportsIndex] | SupportsBytes | ReadableBuffer,
            byteorder: Literal['little', 'big'] = 'big',
            *,
            signed: bool = False,
        ) -> Self:
            raise AssumedToBeImplementedException
    else:

        def to_bytes(self,
                     length: SupportsIndex,
                     byteorder: Literal['little', 'big'],
                     *,
                     signed: bool = False) -> bytes:
            raise AssumedToBeImplementedException

        @classmethod
        def from_bytes(
            cls,
            bytes: Iterable[SupportsIndex] | SupportsBytes | ReadableBuffer,
            byteorder: Literal['little', 'big'],
            *,
            signed: bool = False,
        ) -> Self:
            raise AssumedToBeImplementedException

    if sys.version_info >= (3, 12):

        def is_integer(self) -> Literal[True]:
            raise AssumedToBeImplementedException

    def __add__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __sub__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __mul__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __floordiv__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __truediv__(self, value: int, /) -> float:
        raise AssumedToBeImplementedException

    def __mod__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __divmod__(self, value: int, /) -> tuple[int, int]:
        raise AssumedToBeImplementedException

    def __radd__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rsub__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rfloordiv__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rtruediv__(self, value: int, /) -> float:
        raise AssumedToBeImplementedException

    def __rmod__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rdivmod__(self, value: int, /) -> tuple[int, int]:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, x: Literal[0], /) -> Literal[1]:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: Literal[0], mod: None, /) -> Literal[1]:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: _PositiveInteger, mod: None = None, /) -> int:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: _NegativeInteger, mod: None = None, /) -> float:
        raise AssumedToBeImplementedException

    # positive __value -> int; negative __value -> float
    # return type must be Any as `int | float` causes too many false-positive errors
    @overload
    def __pow__(self, value: int, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: int, mod: int, /) -> int:
        raise AssumedToBeImplementedException

    def __pow__(self, value: int, mod: int | None = None, /) -> int | float:
        raise AssumedToBeImplementedException

    def __rpow__(self, value: int, mod: int | None = None, /) -> Any:
        raise AssumedToBeImplementedException

    def __and__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __or__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __xor__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __lshift__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rshift__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rand__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __ror__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rxor__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rlshift__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rrshift__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __neg__(self) -> int:
        raise AssumedToBeImplementedException

    def __pos__(self) -> int:
        raise AssumedToBeImplementedException

    def __invert__(self) -> int:
        raise AssumedToBeImplementedException

    def __trunc__(self) -> int:
        raise AssumedToBeImplementedException

    def __ceil__(self) -> int:
        raise AssumedToBeImplementedException

    def __floor__(self) -> int:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 14):

        def __round__(self, ndigits: SupportsIndex | None = None, /) -> int:
            raise AssumedToBeImplementedException

    else:

        # def __round__(self, ndigits: SupportsIndex = ..., /) -> int:
        def __round__(self, ndigits: SupportsIndex = 0, /) -> int:
            raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[int]:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __ne__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, value: int, /) -> bool:
        raise AssumedToBeImplementedException

    def __le__(self, value: int, /) -> bool:
        raise AssumedToBeImplementedException

    def __gt__(self, value: int, /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: int, /) -> bool:
        raise AssumedToBeImplementedException

    def __float__(self) -> float:
        raise AssumedToBeImplementedException

    def __int__(self) -> int:
        raise AssumedToBeImplementedException

    def __abs__(self) -> int:
        raise AssumedToBeImplementedException

    def __hash__(self) -> int:
        raise AssumedToBeImplementedException

    def __bool__(self) -> bool:
        raise AssumedToBeImplementedException

    def __index__(self) -> int:
        raise AssumedToBeImplementedException

    def __format__(self, format_spec: str, /) -> str:
        raise AssumedToBeImplementedException


# @disjoint_base
# class float:
class IsFloat(Protocol):
    """Protocol with the same interface as the builtin class `float`.
    """

    # def __new__(cls, x: ConvertibleToFloat = 0, /) -> Self:
    #     ...

    def as_integer_ratio(self) -> tuple[int, int]:
        raise AssumedToBeImplementedException

    def hex(self) -> str:
        raise AssumedToBeImplementedException

    def is_integer(self) -> bool:
        raise AssumedToBeImplementedException

    @classmethod
    def fromhex(cls, string: str, /) -> Self:
        raise AssumedToBeImplementedException

    @property
    def real(self) -> float:
        raise AssumedToBeImplementedException

    @property
    def imag(self) -> float:
        raise AssumedToBeImplementedException

    def conjugate(self) -> float:
        raise AssumedToBeImplementedException

    def __add__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __sub__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __mul__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __floordiv__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __truediv__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __mod__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __divmod__(self, value: float, /) -> tuple[float, float]:
        raise AssumedToBeImplementedException

    @overload
    def __pow__(self, value: int, mod: None = None, /) -> float:
        raise AssumedToBeImplementedException

    # positive __value -> float; negative __value -> complex
    # return type must be Any as `float | complex` causes too many false-positive errors
    @overload
    def __pow__(self, value: float, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException

    def __pow__(self, value: int | float, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException

    def __radd__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __rsub__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __rfloordiv__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __rtruediv__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __rmod__(self, value: float, /) -> float:
        raise AssumedToBeImplementedException

    def __rdivmod__(self, value: float, /) -> tuple[float, float]:
        raise AssumedToBeImplementedException

    @overload
    def __rpow__(self, value: _PositiveInteger, mod: None = None, /) -> float:
        raise AssumedToBeImplementedException

    @overload
    def __rpow__(self, value: _NegativeInteger, mod: None = None, /) -> complex:
        raise AssumedToBeImplementedException

    # Returning `complex` for the general case gives too many false-positive errors.
    @overload
    def __rpow__(self, value: float, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException

    def __rpow__(self, value: int | float, mod: None = None, /) -> Any:
        raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[float]:
        raise AssumedToBeImplementedException

    def __trunc__(self) -> int:
        raise AssumedToBeImplementedException

    def __ceil__(self) -> int:
        raise AssumedToBeImplementedException

    def __floor__(self) -> int:
        raise AssumedToBeImplementedException

    @overload
    def __round__(self, ndigits: None = None, /) -> int:
        raise AssumedToBeImplementedException

    @overload
    def __round__(self, ndigits: SupportsIndex, /) -> float:
        raise AssumedToBeImplementedException

    def __round__(self, ndigits: SupportsIndex | None = None, /) -> float | int:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __ne__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, value: float, /) -> bool:
        raise AssumedToBeImplementedException

    def __le__(self, value: float, /) -> bool:
        raise AssumedToBeImplementedException

    def __gt__(self, value: float, /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: float, /) -> bool:
        raise AssumedToBeImplementedException

    def __neg__(self) -> float:
        raise AssumedToBeImplementedException

    def __pos__(self) -> float:
        raise AssumedToBeImplementedException

    def __int__(self) -> int:
        raise AssumedToBeImplementedException

    def __float__(self) -> float:
        raise AssumedToBeImplementedException

    def __abs__(self) -> float:
        raise AssumedToBeImplementedException

    def __hash__(self) -> int:
        raise AssumedToBeImplementedException

    def __bool__(self) -> bool:
        raise AssumedToBeImplementedException

    def __format__(self, format_spec: str, /) -> str:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 14):

        @classmethod
        def from_number(cls, number: float | SupportsIndex | SupportsFloat, /) -> Self:
            raise AssumedToBeImplementedException


# @disjoint_base
# class complex:
class IsComplex(Protocol):
    """Protocol with the same interface as the builtin class `complex`.
    """
    # # Python doesn't currently accept SupportsComplex for the second argument
    # @overload
    # def __new__(
    #     cls,
    #     real: complex | SupportsComplex | SupportsFloat | SupportsIndex = 0,
    #     imag: complex | SupportsFloat | SupportsIndex = 0,
    # ) -> Self:
    #     ...
    #
    # @overload
    # def __new__(
    #     cls, real: (str | SupportsComplex | SupportsFloat | SupportsIndex | complex)) -> Self:
    #     ...

    @property
    def real(self) -> float:
        raise AssumedToBeImplementedException

    @property
    def imag(self) -> float:
        raise AssumedToBeImplementedException

    def conjugate(self) -> complex:
        raise AssumedToBeImplementedException

    def __add__(self, value: complex, /) -> complex:
        raise AssumedToBeImplementedException

    def __sub__(self, value: complex, /) -> complex:
        raise AssumedToBeImplementedException

    def __mul__(self, value: complex, /) -> complex:
        raise AssumedToBeImplementedException

    def __pow__(self, value: complex, mod: None = None, /) -> complex:
        raise AssumedToBeImplementedException

    def __truediv__(self, value: complex, /) -> complex:
        raise AssumedToBeImplementedException

    def __radd__(self, value: complex, /) -> complex:
        raise AssumedToBeImplementedException

    def __rsub__(self, value: complex, /) -> complex:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: complex, /) -> complex:
        raise AssumedToBeImplementedException

    def __rpow__(self, value: complex, mod: None = None, /) -> complex:
        raise AssumedToBeImplementedException

    def __rtruediv__(self, value: complex, /) -> complex:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __ne__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __neg__(self) -> complex:
        raise AssumedToBeImplementedException

    def __pos__(self) -> complex:
        raise AssumedToBeImplementedException

    def __abs__(self) -> float:
        raise AssumedToBeImplementedException

    def __hash__(self) -> int:
        raise AssumedToBeImplementedException

    def __bool__(self) -> bool:
        raise AssumedToBeImplementedException

    def __format__(self, format_spec: str, /) -> str:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 11):

        def __complex__(self) -> complex:
            raise AssumedToBeImplementedException

    if sys.version_info >= (3, 14):

        @classmethod
        def from_number(cls, number: complex | SupportsComplex | SupportsFloat | SupportsIndex,
                        /) -> Self:
            raise AssumedToBeImplementedException


# @type_check_only
class _FormatMapMapping(Protocol):
    def __getitem__(self, key: str, /) -> Any:
        raise AssumedToBeImplementedException


# @type_check_only
class _TranslateTable(Protocol):
    def __getitem__(self, key: int, /) -> str | int | None:
        raise AssumedToBeImplementedException


# @disjoint_base
# class str(Sequence[str]):
class IsStr(IsSequenceNotStrBytes[str], Protocol):
    """Protocol with the same interface as the builtin class `str`.
    """
    # @overload
    # def __new__(cls, object: object = '') -> Self:
    #     ...
    #
    # @overload
    # def __new__(cls,
    #             object: ReadableBuffer,
    #             encoding: str = 'utf-8',
    #             errors: str = 'strict') -> Self:
    #     ...

    @overload
    def capitalize(self: LiteralString) -> LiteralString:  # type: ignore [misc]
        raise AssumedToBeImplementedException

    @overload
    def capitalize(self) -> Self:
        raise AssumedToBeImplementedException

    def capitalize(self) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def casefold(self: LiteralString) -> LiteralString:  # type: ignore [misc]
        raise AssumedToBeImplementedException

    @overload
    def casefold(self) -> Self:
        raise AssumedToBeImplementedException

    def casefold(self) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def center(  # type: ignore [misc]
            self: LiteralString,
            width: SupportsIndex,
            fillchar: LiteralString = ' ',
            /) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def center(self, width: SupportsIndex, fillchar: str = ' ', /) -> Self:
        raise AssumedToBeImplementedException

    def center(self,
               width: SupportsIndex,
               fillchar: str | LiteralString = ' ',
               /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    def count(self,
              sub: str,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    def encode(self, encoding: str = 'utf-8', errors: str = 'strict') -> bytes:
        raise AssumedToBeImplementedException

    def endswith(self,
                 suffix: str | tuple[str, ...],
                 start: SupportsIndex | None = None,
                 end: SupportsIndex | None = None,
                 /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def expandtabs(  # type: ignore [misc]
            self: LiteralString,
            tabsize: SupportsIndex = 8,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def expandtabs(self, tabsize: SupportsIndex = 8) -> Self:
        raise AssumedToBeImplementedException

    def expandtabs(self, tabsize: SupportsIndex = 8) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    def find(self,
             sub: str,
             start: SupportsIndex | None = None,
             end: SupportsIndex | None = None,
             /) -> int:
        raise AssumedToBeImplementedException

    @overload
    def format(  # type: ignore [misc]
        self: LiteralString,
        *args: LiteralString,
        **kwargs: LiteralString,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def format(self, *args: object, **kwargs: object) -> Self:
        raise AssumedToBeImplementedException

    def format(self, *args: object | LiteralString,
               **kwargs: object | LiteralString) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    def format_map(self, mapping: _FormatMapMapping, /) -> Self:
        raise AssumedToBeImplementedException

    def index(self,
              sub: str,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    def isalnum(self) -> bool:
        raise AssumedToBeImplementedException

    def isalpha(self) -> bool:
        raise AssumedToBeImplementedException

    def isascii(self) -> bool:
        raise AssumedToBeImplementedException

    def isdecimal(self) -> bool:
        raise AssumedToBeImplementedException

    def isdigit(self) -> bool:
        raise AssumedToBeImplementedException

    def isidentifier(self) -> bool:
        raise AssumedToBeImplementedException

    def islower(self) -> bool:
        raise AssumedToBeImplementedException

    def isnumeric(self) -> bool:
        raise AssumedToBeImplementedException

    def isprintable(self) -> bool:
        raise AssumedToBeImplementedException

    def isspace(self) -> bool:
        raise AssumedToBeImplementedException

    def istitle(self) -> bool:
        raise AssumedToBeImplementedException

    def isupper(self) -> bool:
        raise AssumedToBeImplementedException

    @overload
    # def join(self: LiteralString, iterable: Iterable[LiteralString], /) -> LiteralString:
    def join(  # type: ignore[misc]
        self: LiteralString,
        iterable: Iterable[LiteralString],
        /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    # def join(self, iterable: Iterable[str], /) -> str:
    def join(self, iterable: Iterable[str], /) -> Self:
        raise AssumedToBeImplementedException

    def join(self, iterable: Iterable[str] | Iterable[LiteralString], /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def ljust(  # type: ignore[misc]
            self: LiteralString,
            width: SupportsIndex,
            fillchar: LiteralString = ' ',
            /) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def ljust(self, width: SupportsIndex, fillchar: str = ' ', /) -> Self:
        raise AssumedToBeImplementedException

    def ljust(self,
              width: SupportsIndex,
              fillchar: str | LiteralString = ' ',
              /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def lower(self: LiteralString) -> LiteralString:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    @overload
    def lower(self) -> Self:
        raise AssumedToBeImplementedException

    def lower(self) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def lstrip(  # type: ignore[misc]
        self: LiteralString,
        chars: LiteralString | None = None,
        /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def lstrip(self, chars: str | None = None, /) -> Self:
        raise AssumedToBeImplementedException

    def lstrip(self, chars: str | LiteralString | None = None, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def partition(  # type: ignore[misc]
            self: LiteralString, sep: LiteralString,
            /) -> tuple[LiteralString, LiteralString, LiteralString]:
        raise AssumedToBeImplementedException

    @overload
    def partition(self, sep: str, /) -> tuple[str, str, str]:
        raise AssumedToBeImplementedException

    def partition(self, sep: str | LiteralString,
                  /) -> tuple[LiteralString, LiteralString, LiteralString] | tuple[str, str, str]:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 13):

        @overload
        def replace(
                self: LiteralString,  # type: ignore[misc]
                old: LiteralString,
                new: LiteralString,
                /,
                count: SupportsIndex = -1) -> LiteralString:
            raise AssumedToBeImplementedException

        @overload
        def replace(self, old: str, new: str, /, count: SupportsIndex = -1) -> Self:
            raise AssumedToBeImplementedException  # type: ignore[misc]

        def replace(self, old: str | LiteralString, new: Self | LiteralString,
                    /) -> str | LiteralString:
            raise AssumedToBeImplementedException
    else:

        @overload
        def replace(  # type: ignore[misc]
                self: LiteralString,
                old: LiteralString,
                new: LiteralString,
                count: SupportsIndex = -1,
                /) -> LiteralString:
            raise AssumedToBeImplementedException

        @overload
        def replace(self, old: str, new: str, count: SupportsIndex = -1, /) -> Self:
            raise AssumedToBeImplementedException

        def replace(self,
                    old: str | LiteralString,
                    new: str | LiteralString,
                    count: SupportsIndex = -1,
                    /) -> Self | LiteralString:
            raise AssumedToBeImplementedException

    @overload
    def removeprefix(  # type: ignore[misc]
            self: LiteralString,
            prefix: LiteralString,
            /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def removeprefix(self, prefix: str, /) -> Self:
        raise AssumedToBeImplementedException

    def removeprefix(self, prefix: str | LiteralString, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def removesuffix(  # type: ignore[misc]
            self: LiteralString,
            suffix: LiteralString,
            /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def removesuffix(self, suffix: str, /) -> Self:
        raise AssumedToBeImplementedException

    def removesuffix(self, suffix: str | LiteralString, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    def rfind(self,
              sub: str,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    def rindex(self,
               sub: str,
               start: SupportsIndex | None = None,
               end: SupportsIndex | None = None,
               /) -> int:
        raise AssumedToBeImplementedException

    def rjust(self, width: SupportsIndex, fillchar: str = ' ', /) -> Self:
        raise AssumedToBeImplementedException

    def rpartition(self, sep: str, /) -> tuple[str, str, str]:
        raise AssumedToBeImplementedException

    def rsplit(self, sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str]:
        raise AssumedToBeImplementedException

    def rstrip(self, chars: str | None = None, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def split(  # type: ignore[misc]
            self: LiteralString,
            sep: LiteralString | None = None,
            maxsplit: SupportsIndex = -1) -> list[LiteralString]:
        raise AssumedToBeImplementedException

    @overload
    def split(self, sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str]:
        raise AssumedToBeImplementedException

    def split(self,
              sep: str | LiteralString | None = None,
              maxsplit: SupportsIndex = -1) -> list[str] | list[LiteralString]:
        raise AssumedToBeImplementedException

    @overload
    def splitlines(  # type: ignore[misc]
            self: LiteralString,
            keepends: bool = False,
    ) -> list[LiteralString]:
        raise AssumedToBeImplementedException

    @overload
    def splitlines(self, keepends: bool = False) -> list[str]:
        raise AssumedToBeImplementedException

    def splitlines(self, keepends: bool = False) -> list[str] | list[LiteralString]:
        raise AssumedToBeImplementedException

    def startswith(self,
                   prefix: str | tuple[str, ...],
                   start: SupportsIndex | None = None,
                   end: SupportsIndex | None = None,
                   /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def strip(  # type: ignore[misc]
        self: LiteralString,
        chars: LiteralString | None = None,
        /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def strip(self, chars: str | None = None, /) -> Self:
        raise AssumedToBeImplementedException

    def strip(self, chars: str | LiteralString | None = None, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def swapcase(self: LiteralString) -> LiteralString:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    @overload
    def swapcase(self) -> Self:
        raise AssumedToBeImplementedException

    def swapcase(self) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def title(self: LiteralString) -> LiteralString:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    @overload
    def title(self) -> Self:
        raise AssumedToBeImplementedException

    def title(self) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    def translate(self, table: _TranslateTable, /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def upper(self: LiteralString) -> LiteralString:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    @overload
    def upper(self) -> Self:
        raise AssumedToBeImplementedException

    def upper(self) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def zfill(self: LiteralString, width: SupportsIndex, /) -> LiteralString:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    @overload
    def zfill(self, width: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def zfill(self, width: SupportsIndex, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @staticmethod
    @overload
    def maketrans(x: dict[int, _T] | dict[str, _T] | dict[str | int, _T], /) -> dict[int, _T]:
        raise AssumedToBeImplementedException

    @staticmethod
    @overload
    def maketrans(x: str, y: str, /) -> dict[int, int]:
        raise AssumedToBeImplementedException

    @staticmethod
    @overload
    def maketrans(x: str, y: str, z: str, /) -> dict[int, int | None]:
        raise AssumedToBeImplementedException

    @staticmethod
    def maketrans(
        x: str | dict[int, _T] | dict[str, _T] | dict[str | int, _T],
        y: str | None = None,
        z: str | None = None,
        /,
    ) -> dict[int, _T] | dict[int, int] | dict[int, int | None]:
        raise AssumedToBeImplementedException

    @overload
    def __add__(  # type: ignore[misc]
            self: LiteralString,
            value: LiteralString,
            /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def __add__(self, value: str, /) -> Self:
        raise AssumedToBeImplementedException

    def __add__(self, value: str | LiteralString, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    # Incompatible with Sequence.__contains__
    def __contains__(self, key: str, /) -> bool:  # type: ignore[override]
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: str, /) -> bool:
        raise AssumedToBeImplementedException

    @overload  # type: ignore[override]
    # def __getitem__(self: LiteralString, key: SupportsIndex | slice[SupportsIndex | None],
    def __getitem__(  # type: ignore[misc]
            self: LiteralString,
            key: SupportsIndex | slice,
            /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    # def __getitem__(self, key: SupportsIndex | slice[SupportsIndex | None], /) -> str:
    def __getitem__(self, key: SupportsIndex | slice, /) -> Self:
        raise AssumedToBeImplementedException

    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        key: SupportsIndex | slice,
        /,
    ) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    def __gt__(self, value: str, /) -> bool:
        raise AssumedToBeImplementedException

    def __hash__(self) -> int:
        raise AssumedToBeImplementedException

    @overload
    def __iter__(self: LiteralString) -> Iterator[LiteralString]:  # type: ignore[misc]
        ...

    @overload
    def __iter__(self) -> Iterator[str]:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[str] | Iterator[LiteralString]:
        raise AssumedToBeImplementedException

    def __le__(self, value: str, /) -> bool:
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __lt__(self, value: str, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __mod__(  # type: ignore[misc]
        self: LiteralString,
        value: LiteralString | tuple[LiteralString, ...],
        /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def __mod__(self, value: Any, /) -> Self:
        raise AssumedToBeImplementedException

    def __mod__(self, value: Any, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def __mul__(  # type: ignore[misc]
            self: LiteralString,
            value: SupportsIndex,
            /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def __mul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    def __ne__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __rmul__(  # type: ignore[misc]
            self: LiteralString,
            value: SupportsIndex,
            /,
    ) -> LiteralString:
        raise AssumedToBeImplementedException

    @overload
    def __rmul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: SupportsIndex, /) -> Self | LiteralString:
        raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[str]:
        raise AssumedToBeImplementedException

    def __format__(self, format_spec: str, /) -> Self:  # type: ignore [override]
        raise AssumedToBeImplementedException


# @disjoint_base
# class bytes(Sequence[int]):
class IsBytes(IsSequenceNotStrBytes[int], Protocol):
    """Protocol with the same interface as the builtin class `bytes`.
    """

    # @overload
    # def __new__(cls, o: Iterable[SupportsIndex] | SupportsIndex | SupportsBytes | ReadableBuffer,
    #             /) -> Self:
    #     ...
    #
    # @overload
    # def __new__(cls, string: str, /, encoding: str, errors: str = 'strict') -> Self:
    #     ...
    #
    # @overload
    # def __new__(cls) -> Self:
    #     ...

    def capitalize(self) -> Self:
        raise AssumedToBeImplementedException

    def center(self, width: SupportsIndex, fillchar: bytes = b' ', /) -> Self:
        raise AssumedToBeImplementedException

    def count(self,
              sub: ReadableBuffer | SupportsIndex,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    def decode(self, encoding: str = 'utf-8', errors: str = 'strict') -> str:
        raise AssumedToBeImplementedException

    def endswith(
        self,
        suffix: ReadableBuffer | tuple[ReadableBuffer, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool:
        raise AssumedToBeImplementedException

    def expandtabs(self, tabsize: SupportsIndex = 8) -> Self:
        raise AssumedToBeImplementedException

    def find(self,
             sub: ReadableBuffer | SupportsIndex,
             start: SupportsIndex | None = None,
             end: SupportsIndex | None = None,
             /) -> int:
        raise AssumedToBeImplementedException

    # def hex(self, sep: str | bytes = ..., bytes_per_sep: SupportsIndex = 1) -> str:
    def hex(self, sep: str | bytes = '', bytes_per_sep: SupportsIndex = 1) -> str:
        raise AssumedToBeImplementedException

    def index(self,
              sub: ReadableBuffer | SupportsIndex,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    def isalnum(self) -> bool:
        raise AssumedToBeImplementedException

    def isalpha(self) -> bool:
        raise AssumedToBeImplementedException

    def isascii(self) -> bool:
        raise AssumedToBeImplementedException

    def isdigit(self) -> bool:
        raise AssumedToBeImplementedException

    def islower(self) -> bool:
        raise AssumedToBeImplementedException

    def isspace(self) -> bool:
        raise AssumedToBeImplementedException

    def istitle(self) -> bool:
        raise AssumedToBeImplementedException

    def isupper(self) -> bool:
        raise AssumedToBeImplementedException

    def join(self, iterable_of_bytes: Iterable[ReadableBuffer], /) -> Self:
        raise AssumedToBeImplementedException

    def ljust(self, width: SupportsIndex, fillchar: bytes | bytearray = b' ', /) -> Self:
        raise AssumedToBeImplementedException

    def lower(self) -> Self:
        raise AssumedToBeImplementedException

    def lstrip(self, bytes: ReadableBuffer | None = None, /) -> Self:
        raise AssumedToBeImplementedException

    def partition(self, sep: ReadableBuffer, /) -> tuple[bytes, bytes, bytes]:
        raise AssumedToBeImplementedException

    def replace(self,
                old: ReadableBuffer,
                new: ReadableBuffer,
                count: SupportsIndex = -1,
                /) -> Self:
        raise AssumedToBeImplementedException

    def removeprefix(self, prefix: ReadableBuffer, /) -> Self:
        raise AssumedToBeImplementedException

    def removesuffix(self, suffix: ReadableBuffer, /) -> Self:
        raise AssumedToBeImplementedException

    def rfind(self,
              sub: ReadableBuffer | SupportsIndex,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    def rindex(self,
               sub: ReadableBuffer | SupportsIndex,
               start: SupportsIndex | None = None,
               end: SupportsIndex | None = None,
               /) -> int:
        raise AssumedToBeImplementedException

    def rjust(self, width: SupportsIndex, fillchar: bytes | bytearray = b' ', /) -> Self:
        raise AssumedToBeImplementedException

    def rpartition(self, sep: ReadableBuffer, /) -> tuple[bytes, bytes, bytes]:
        raise AssumedToBeImplementedException

    def rsplit(self,
               sep: ReadableBuffer | None = None,
               maxsplit: SupportsIndex = -1) -> list[bytes]:
        raise AssumedToBeImplementedException

    def rstrip(self, bytes: ReadableBuffer | None = None, /) -> Self:
        raise AssumedToBeImplementedException

    def split(self, sep: ReadableBuffer | None = None, maxsplit: SupportsIndex = -1) -> list[bytes]:
        raise AssumedToBeImplementedException

    def splitlines(self, keepends: bool = False) -> list[bytes]:
        raise AssumedToBeImplementedException

    def startswith(
        self,
        prefix: ReadableBuffer | tuple[ReadableBuffer, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool:
        raise AssumedToBeImplementedException

    def strip(self, bytes: ReadableBuffer | None = None, /) -> Self:
        raise AssumedToBeImplementedException

    def swapcase(self) -> Self:
        raise AssumedToBeImplementedException

    def title(self) -> Self:
        raise AssumedToBeImplementedException

    def translate(self, table: ReadableBuffer | None, /, delete: ReadableBuffer = b'') -> Self:
        raise AssumedToBeImplementedException

    def upper(self) -> Self:
        raise AssumedToBeImplementedException

    def zfill(self, width: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 14):

        @classmethod
        def fromhex(cls, string: str | ReadableBuffer, /) -> Self:
            raise AssumedToBeImplementedException
    else:

        @classmethod
        def fromhex(cls, string: str, /) -> Self:
            raise AssumedToBeImplementedException

    @staticmethod
    def maketrans(frm: ReadableBuffer, to: ReadableBuffer, /) -> Self:
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[int]:
        raise AssumedToBeImplementedException

    def __hash__(self) -> int:
        raise AssumedToBeImplementedException

    @overload  # type: ignore[override]
    def __getitem__(self, key: SupportsIndex, /) -> int:
        raise AssumedToBeImplementedException

    @overload
    # def __getitem__(self, key: slice[SupportsIndex | None], /) -> bytes:
    def __getitem__(self, key: slice, /) -> Self:
        raise AssumedToBeImplementedException

    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
            self, key: slice | SupportsIndex, /) -> Self | int:
        raise AssumedToBeImplementedException

    def __add__(self, value: ReadableBuffer, /) -> Self:
        raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def __mod__(self, value: Any, /) -> Self:
        raise AssumedToBeImplementedException

    # Incompatible with Sequence.__contains__
    def __contains__(  # type: ignore[override]
            self, key: SupportsIndex | ReadableBuffer, /) -> bool:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __ne__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, value: bytes, /) -> bool:
        raise AssumedToBeImplementedException

    def __le__(self, value: bytes, /) -> bool:
        raise AssumedToBeImplementedException

    def __gt__(self, value: bytes, /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: bytes, /) -> bool:
        raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[bytes]:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 11):

        def __bytes__(self) -> bytes:
            raise AssumedToBeImplementedException

    def __buffer__(self, flags: int, /) -> memoryview:
        raise AssumedToBeImplementedException


# @disjoint_base
# class bytearray(MutableSequence[int]):
class IsByteArray(IsMutableSequence[int], Protocol):
    """Protocol with the same interface as the builtin class `bytearray`.
    """

    # @overload
    # def __init__(self) -> None:
    #     ...
    #
    # @overload
    # def __init__(self, ints: Iterable[SupportsIndex] | SupportsIndex | ReadableBuffer, /) -> None:
    #     ...
    #
    # @overload
    # def __init__(self, string: str, /, encoding: str, errors: str = 'strict') -> None:
    #     ...

    def append(self, item: SupportsIndex, /) -> None:
        raise AssumedToBeImplementedException

    def capitalize(self) -> bytearray:
        raise AssumedToBeImplementedException

    def center(self, width: SupportsIndex, fillchar: bytes = b' ', /) -> bytearray:
        raise AssumedToBeImplementedException

    def count(self,
              sub: ReadableBuffer | SupportsIndex,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    # def copy(self) -> bytearray:
    #     raise AssumedToBeImplementedException

    def decode(self, encoding: str = 'utf-8', errors: str = 'strict') -> str:
        raise AssumedToBeImplementedException

    def endswith(
        self,
        suffix: ReadableBuffer | tuple[ReadableBuffer, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool:
        raise AssumedToBeImplementedException

    def expandtabs(self, tabsize: SupportsIndex = 8) -> bytearray:
        raise AssumedToBeImplementedException

    def extend(self, iterable_of_ints: Iterable[SupportsIndex], /) -> None:
        raise AssumedToBeImplementedException

    def find(self,
             sub: ReadableBuffer | SupportsIndex,
             start: SupportsIndex | None = None,
             end: SupportsIndex | None = None,
             /) -> int:
        raise AssumedToBeImplementedException

    # def hex(self, sep: str | bytes = ..., bytes_per_sep: SupportsIndex = 1) -> str:
    def hex(self, sep: str | bytes = '', bytes_per_sep: SupportsIndex = 1) -> str:
        raise AssumedToBeImplementedException

    def index(self,
              sub: ReadableBuffer | SupportsIndex,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    def insert(self, index: SupportsIndex, item: SupportsIndex, /) -> None:
        raise AssumedToBeImplementedException

    def isalnum(self) -> bool:
        raise AssumedToBeImplementedException

    def isalpha(self) -> bool:
        raise AssumedToBeImplementedException

    def isascii(self) -> bool:
        raise AssumedToBeImplementedException

    def isdigit(self) -> bool:
        raise AssumedToBeImplementedException

    def islower(self) -> bool:
        raise AssumedToBeImplementedException

    def isspace(self) -> bool:
        raise AssumedToBeImplementedException

    def istitle(self) -> bool:
        raise AssumedToBeImplementedException

    def isupper(self) -> bool:
        raise AssumedToBeImplementedException

    def join(self, iterable_of_bytes: Iterable[ReadableBuffer], /) -> bytearray:
        raise AssumedToBeImplementedException

    def ljust(self, width: SupportsIndex, fillchar: bytes | bytearray = b' ', /) -> bytearray:
        raise AssumedToBeImplementedException

    def lower(self) -> bytearray:
        raise AssumedToBeImplementedException

    def lstrip(self, bytes: ReadableBuffer | None = None, /) -> bytearray:
        raise AssumedToBeImplementedException

    def partition(self, sep: ReadableBuffer, /) -> tuple[bytearray, bytearray, bytearray]:
        raise AssumedToBeImplementedException

    def pop(self, index: int = -1, /) -> int:
        raise AssumedToBeImplementedException

    def remove(self, value: int, /) -> None:
        raise AssumedToBeImplementedException

    def removeprefix(self, prefix: ReadableBuffer, /) -> bytearray:
        raise AssumedToBeImplementedException

    def removesuffix(self, suffix: ReadableBuffer, /) -> bytearray:
        raise AssumedToBeImplementedException

    def replace(self,
                old: ReadableBuffer,
                new: ReadableBuffer,
                count: SupportsIndex = -1,
                /) -> bytearray:
        raise AssumedToBeImplementedException

    def rfind(self,
              sub: ReadableBuffer | SupportsIndex,
              start: SupportsIndex | None = None,
              end: SupportsIndex | None = None,
              /) -> int:
        raise AssumedToBeImplementedException

    def rindex(self,
               sub: ReadableBuffer | SupportsIndex,
               start: SupportsIndex | None = None,
               end: SupportsIndex | None = None,
               /) -> int:
        raise AssumedToBeImplementedException

    def rjust(self, width: SupportsIndex, fillchar: bytes | bytearray = b' ', /) -> bytearray:
        raise AssumedToBeImplementedException

    def rpartition(self, sep: ReadableBuffer, /) -> tuple[bytearray, bytearray, bytearray]:
        raise AssumedToBeImplementedException

    def rsplit(self,
               sep: ReadableBuffer | None = None,
               maxsplit: SupportsIndex = -1) -> list[bytearray]:
        raise AssumedToBeImplementedException

    def rstrip(self, bytes: ReadableBuffer | None = None, /) -> bytearray:
        raise AssumedToBeImplementedException

    def split(self,
              sep: ReadableBuffer | None = None,
              maxsplit: SupportsIndex = -1) -> list[bytearray]:
        raise AssumedToBeImplementedException

    def splitlines(self, keepends: bool = False) -> list[bytearray]:
        raise AssumedToBeImplementedException

    def startswith(
        self,
        prefix: ReadableBuffer | tuple[ReadableBuffer, ...],
        start: SupportsIndex | None = None,
        end: SupportsIndex | None = None,
        /,
    ) -> bool:
        raise AssumedToBeImplementedException

    def strip(self, bytes: ReadableBuffer | None = None, /) -> bytearray:
        raise AssumedToBeImplementedException

    def swapcase(self) -> bytearray:
        raise AssumedToBeImplementedException

    def title(self) -> bytearray:
        raise AssumedToBeImplementedException

    def translate(self, table: ReadableBuffer | None, /, delete: bytes = b'') -> bytearray:
        raise AssumedToBeImplementedException

    def upper(self) -> bytearray:
        raise AssumedToBeImplementedException

    def zfill(self, width: SupportsIndex, /) -> bytearray:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 14):

        @classmethod
        def fromhex(cls, string: str | ReadableBuffer, /) -> Self:
            raise AssumedToBeImplementedException
    else:

        @classmethod
        def fromhex(cls, string: str, /) -> Self:
            raise AssumedToBeImplementedException

    @staticmethod
    def maketrans(frm: ReadableBuffer, to: ReadableBuffer, /) -> bytes:
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[int]:
        raise AssumedToBeImplementedException

    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    @overload  # type: ignore[override]
    def __getitem__(self, key: SupportsIndex, /) -> int:
        raise AssumedToBeImplementedException

    @overload
    # def __getitem__(self, key: slice[SupportsIndex | None], /) -> bytearray:
    def __getitem__(self, key: slice, /) -> bytearray:
        raise AssumedToBeImplementedException

    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
            self, key: slice | SupportsIndex, /) -> bytearray | int:
        raise AssumedToBeImplementedException

    @overload
    def __setitem__(self, key: SupportsIndex, value: SupportsIndex, /) -> None:
        raise AssumedToBeImplementedException

    @overload
    # def __setitem__(self,
    #                 key: slice[SupportsIndex | None],
    #                 value: Iterable[SupportsIndex] | bytes,
    #                 /) -> None:
    def __setitem__(self, key: slice, value: Iterable[SupportsIndex] | bytes, /) -> None:
        raise AssumedToBeImplementedException

    def __setitem__(self,
                    key: slice | SupportsIndex,
                    value: Iterable[SupportsIndex] | bytes | SupportsIndex,
                    /) -> None:
        raise AssumedToBeImplementedException

    def __delitem__(self, key: SupportsIndex | slice, /) -> None:
        raise AssumedToBeImplementedException

    def __add__(self, value: ReadableBuffer, /) -> bytearray:
        raise AssumedToBeImplementedException

    # The superclass wants us to accept Iterable[int], but that fails at runtime.
    def __iadd__(self, value: ReadableBuffer, /) -> Self:  # type: ignore[override]
        raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> bytearray:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: SupportsIndex, /) -> bytearray:
        raise AssumedToBeImplementedException

    def __imul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def __mod__(self, value: Any, /) -> bytes:
        raise AssumedToBeImplementedException

    # Incompatible with Sequence.__contains__
    def __contains__(  # type: ignore[override]
            self, key: SupportsIndex | ReadableBuffer, /) -> bool:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __ne__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, value: ReadableBuffer, /) -> bool:
        raise AssumedToBeImplementedException

    def __le__(self, value: ReadableBuffer, /) -> bool:
        raise AssumedToBeImplementedException

    def __gt__(self, value: ReadableBuffer, /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: ReadableBuffer, /) -> bool:
        raise AssumedToBeImplementedException

    def __alloc__(self) -> int:
        raise AssumedToBeImplementedException

    def __buffer__(self, flags: int, /) -> memoryview:
        raise AssumedToBeImplementedException

    def __release_buffer__(self, buffer: memoryview, /) -> None:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 14):

        def resize(self, size: int, /) -> None:
            raise AssumedToBeImplementedException


_IntegerFormats: TypeAlias = Literal['b',
                                     'B',
                                     '@b',
                                     '@B',
                                     'h',
                                     'H',
                                     '@h',
                                     '@H',
                                     'i',
                                     'I',
                                     '@i',
                                     '@I',
                                     'l',
                                     'L',
                                     '@l',
                                     '@L',
                                     'q',
                                     'Q',
                                     '@q',
                                     '@Q',
                                     'P',
                                     '@P']

# @final
# class memoryview(Sequence[_I]):
#     @property
#     def format(self) -> str:
#         raise AssumedToBeImplementedException
#
#     @property
#     def itemsize(self) -> int:
#         raise AssumedToBeImplementedException
#
#     @property
#     def shape(self) -> tuple[int, ...] | None:
#         raise AssumedToBeImplementedException
#
#     @property
#     def strides(self) -> tuple[int, ...] | None:
#         raise AssumedToBeImplementedException
#
#     @property
#     def suboffsets(self) -> tuple[int, ...] | None:
#         raise AssumedToBeImplementedException
#
#     @property
#     def readonly(self) -> bool:
#         raise AssumedToBeImplementedException
#
#     @property
#     def ndim(self) -> int:
#         raise AssumedToBeImplementedException
#
#     @property
#     def obj(self) -> ReadableBuffer:
#         raise AssumedToBeImplementedException
#
#     @property
#     def c_contiguous(self) -> bool:
#         raise AssumedToBeImplementedException
#
#     @property
#     def f_contiguous(self) -> bool:
#         raise AssumedToBeImplementedException
#
#     @property
#     def contiguous(self) -> bool:
#         raise AssumedToBeImplementedException
#
#     @property
#     def nbytes(self) -> int:
#         raise AssumedToBeImplementedException
#
#     def __new__(cls, obj: ReadableBuffer) -> Self:
#         ...
#
#     def __enter__(self) -> Self:
#         raise AssumedToBeImplementedException
#
#     def __exit__(
#         self,
#         exc_type: type[BaseException]
#         | None,  # noqa: PYI036 # This is the module declaring BaseException
#         exc_val: BaseException | None,
#         exc_tb: TracebackType | None,
#         /,
#     ) -> None:
#         raise AssumedToBeImplementedException
#
#     @overload
#     def cast(self,
#              format: Literal['c', '@c'],
#              shape: list[int] | tuple[int, ...] = ...) -> memoryview[bytes]:
#         raise AssumedToBeImplementedException
#
#     @overload
#     def cast(self,
#              format: Literal['f', '@f', 'd', '@d'],
#              shape: list[int] | tuple[int, ...] = ...) -> memoryview[float]:
#         raise AssumedToBeImplementedException
#
#     @overload
#     def cast(self,
#              format: Literal['?'],
#              shape: list[int] | tuple[int, ...] = ...) -> memoryview[bool]:
#         raise AssumedToBeImplementedException
#
#
#     @overload
#     def cast(
#         self,
#         format: _IntegerFormats,
#         shape: list[int] | tuple[int, ...] = ...,
#     ) -> memoryview:
#         raise AssumedToBeImplementedException
#
#
#
#     @overload  # type: ignore[override]
#     def __getitem__(self, key: SupportsIndex | tuple[SupportsIndex, ...], /) -> _I:
#         raise AssumedToBeImplementedException
#
#     @overload
#     def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
#             self,
#             key: slice,
#             /,
#     ) -> memoryview[_I]:
#         raise AssumedToBeImplementedException
#
#     def __contains__(self, x: object, /) -> bool:
#         raise AssumedToBeImplementedException
#
#     def __iter__(self) -> Iterator[_I]:
#         raise AssumedToBeImplementedException
#
#     def __len__(self) -> int:
#         raise AssumedToBeImplementedException
#
#     def __eq__(self, value: object, /) -> bool:
#         raise AssumedToBeImplementedException
#
#     def __hash__(self) -> int:
#         raise AssumedToBeImplementedException
#
#     @overload
#     def __setitem__(self, key: slice, value: ReadableBuffer, /) -> None:
#         raise AssumedToBeImplementedException
#
#     @overload
#     def __setitem__(self, key: SupportsIndex | tuple[SupportsIndex, ...], value: _I, /) -> None:
#         raise AssumedToBeImplementedException
#
#     if sys.version_info >= (3, 10):
#
#         def tobytes(self, order: Literal['C', 'F', 'A'] | None = 'C') -> bytes:
#             raise AssumedToBeImplementedException
#     else:
#
#         def tobytes(self, order: Literal['C', 'F', 'A'] | None = None) -> bytes:
#             raise AssumedToBeImplementedException
#
#     def tolist(self) -> list[int]:
#         raise AssumedToBeImplementedException
#
#     def toreadonly(self) -> memoryview:
#         raise AssumedToBeImplementedException
#
#     def release(self) -> None:
#         raise AssumedToBeImplementedException
#
#     def hex(self, sep: str | bytes = ..., bytes_per_sep: SupportsIndex = 1) -> str:
#         raise AssumedToBeImplementedException
#
#     def __buffer__(self, flags: int, /) -> memoryview:
#         raise AssumedToBeImplementedException
#
#     def __release_buffer__(self, buffer: memoryview, /) -> None:
#         raise AssumedToBeImplementedException
#
#     if sys.version_info >= (3, 14):
#
#         def index(self,
#                   value: object,
#                   start: SupportsIndex = 0,
#                   stop: SupportsIndex = sys.maxsize,
#                   /) -> int:
#             ...
#
#         def count(self, value: object, /) -> int:
#             ...
#     else:
#         # These are inherited from the Sequence ABC, but don't actually exist on memoryview.
#         # See https://github.com/python/cpython/issues/125420
#         index: ClassVar[None] = None  # type: ignore[assignment]
#         count: ClassVar[None] = None  # type: ignore[assignment]
#
#     if sys.version_info >= (3, 14):
#
#         def __class_getitem__(cls, item: Any, /) -> GenericAlias:
#             raise AssumedToBeImplementedException
#


# @final
# class bool(int):
class IsBool(IsInt, Protocol):
    """Protocol with the same interface as the builtin class `bool`.
    """
    # def __new__(cls, o: object = False, /) -> Self:
    #     ...
    # The following overloads could be represented more elegantly with a
    # TypeVar('_B', bool, int), however mypy has a bug regarding TypeVar
    # constraints (https://github.com/python/mypy/issues/11880).
    @overload
    def __and__(self, value: bool, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __and__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __and__(self, value: int | bool, /) -> int | bool:
        raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: bool, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __or__(self, value: int | bool, /) -> int | bool:
        raise AssumedToBeImplementedException

    @overload
    def __xor__(self, value: bool, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __xor__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __xor__(self, value: int | bool, /) -> int | bool:
        raise AssumedToBeImplementedException

    @overload
    def __rand__(self, value: bool, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __rand__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rand__(self, value: int | bool, /) -> int | bool:
        raise AssumedToBeImplementedException

    @overload
    def __ror__(self, value: bool, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __ror__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __ror__(self, value: int | bool, /) -> int | bool:
        raise AssumedToBeImplementedException

    @overload
    def __rxor__(self, value: bool, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __rxor__(self, value: int, /) -> int:
        raise AssumedToBeImplementedException

    def __rxor__(self, value: int | bool, /) -> int | bool:
        raise AssumedToBeImplementedException

    def __getnewargs__(self) -> tuple[int]:
        raise AssumedToBeImplementedException

    @deprecated(
        'Will throw an error in Python 3.16. Use `not` for logical negation of bools instead.')
    def __invert__(self) -> int:
        raise AssumedToBeImplementedException


# @disjoint_base
# class tuple(Sequence[_T_co]):
class IsTuple(IsSequenceNotStrBytes[_T_co], Protocol[_T_co]):  # type: ignore[misc]
    """Protocol with the same interface as the builtin class `tuple`.
    """

    # def __new__(cls, iterable: Iterable[_T_co] = (), /) -> Self:
    #     ...

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __contains__(self, key: object, /) -> bool:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, key: SupportsIndex, /) -> _T_co:
        raise AssumedToBeImplementedException

    @overload
    # def __getitem__(self, key: slice[SupportsIndex | None], /) -> tuple[_T_co, ...]:
    def __getitem__(self, key: slice, /) -> tuple[_T_co, ...]:
        raise AssumedToBeImplementedException

    def __getitem__(self, key: slice | SupportsIndex, /) -> tuple[_T_co, ...] | _T_co:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_T_co]:
        raise AssumedToBeImplementedException

    def __lt__(self, value: tuple[_T_co, ...], /) -> bool:
        raise AssumedToBeImplementedException

    def __le__(self, value: tuple[_T_co, ...], /) -> bool:
        raise AssumedToBeImplementedException

    def __gt__(self, value: tuple[_T_co, ...], /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: tuple[_T_co, ...], /) -> bool:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __hash__(self) -> int:
        raise AssumedToBeImplementedException

    @overload
    def __add__(self, value: tuple[_T_co, ...], /) -> tuple[_T_co, ...]:
        raise AssumedToBeImplementedException

    @overload
    def __add__(self, value: tuple[_T, ...], /) -> tuple[_T_co | _T, ...]:
        raise AssumedToBeImplementedException

    def __add__(self, value: tuple[_T, ...] | tuple[_T_co, ...],
                /) -> tuple[_T_co | _T, ...] | tuple[_T_co, ...]:
        raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> tuple[_T_co, ...]:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: SupportsIndex, /) -> tuple[_T_co, ...]:
        raise AssumedToBeImplementedException

    def count(self, value: Any, /) -> int:
        raise AssumedToBeImplementedException

    def index(self,
              value: Any,
              start: SupportsIndex = 0,
              stop: SupportsIndex = sys.maxsize,
              /) -> int:
        raise AssumedToBeImplementedException

    # def __class_getitem__(cls, item: Any, /) -> GenericAlias:
    #     raise AssumedToBeImplementedException


# @disjoint_base
# class list(MutableSequence[_T]):
class IsList(IsMutableSequence[_T], Protocol[_T]):
    """Protocol with the same interface as the builtin class `list`.
    """

    # @overload
    # def __init__(self) -> None:
    #     ...
    #
    # @overload
    # def __init__(self, iterable: Iterable[_T], /) -> None:
    #     ...

    # def copy(self) -> list[_T]:
    #     raise AssumedToBeImplementedException

    def append(self, object: _T, /) -> None:
        raise AssumedToBeImplementedException

    def extend(self, iterable: Iterable[_T], /) -> None:
        raise AssumedToBeImplementedException

    def pop(self, index: SupportsIndex = -1, /) -> _T:
        raise AssumedToBeImplementedException

    # Signature of `list.index` should be kept in line with `collections.UserList.index()`
    # and multiprocessing.managers.ListProxy.index()
    def index(self,
              value: _T,
              start: SupportsIndex = 0,
              stop: SupportsIndex = sys.maxsize,
              /) -> int:
        raise AssumedToBeImplementedException

    def count(self, value: _T, /) -> int:
        raise AssumedToBeImplementedException

    def insert(self, index: SupportsIndex, object: _T, /) -> None:
        raise AssumedToBeImplementedException

    def remove(self, value: _T, /) -> None:
        raise AssumedToBeImplementedException

    # Signature of `list.sort` should be kept inline with `collections.UserList.sort()`
    # and multiprocessing.managers.ListProxy.sort()
    #
    # Use list[SupportsRichComparisonT] for the first overload rather than [SupportsRichComparison]
    # to work around invariance
    @overload
    def sort(self: IsList[SupportsRichComparisonT],
             *,
             key: None = None,
             reverse: bool = False) -> None:
        raise AssumedToBeImplementedException

    @overload
    def sort(self, *, key: Callable[[_T], SupportsRichComparison], reverse: bool = False) -> None:
        raise AssumedToBeImplementedException

    def sort(self: IsList[_T] | IsList[SupportsRichComparisonT],
             *,
             key: Callable[[_T], SupportsRichComparison] | None = None,
             reverse: bool = False) -> None:
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_T]:
        raise AssumedToBeImplementedException

    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    @overload
    def __getitem__(self, i: SupportsIndex, /) -> _T:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, s: slice, /) -> list[_T]:
        raise AssumedToBeImplementedException

    # @overload
    def __getitem__(self, s: slice | SupportsIndex, /) -> list[_T] | _T:
        raise AssumedToBeImplementedException

    #
    # def __getitem__(self, index: SupportsIndex | slice, /) -> _T | list[_T]:
    #     raise AssumedToBeImplementedException

    @overload
    def __setitem__(self, key: SupportsIndex, value: _T, /) -> None:
        raise AssumedToBeImplementedException

    @overload
    def __setitem__(self, key: slice, value: Iterable[_T], /) -> None:
        raise AssumedToBeImplementedException

    def __setitem__(self, key: slice | SupportsIndex, value: Iterable[_T] | _T, /) -> None:
        raise AssumedToBeImplementedException

    def __delitem__(self, key: SupportsIndex | slice, /) -> None:
        raise AssumedToBeImplementedException

    # Overloading looks unnecessary, but is needed to work around complex mypy problems
    @overload
    def __add__(self, value: list[_T], /) -> list[_T]:
        raise AssumedToBeImplementedException

    @overload
    def __add__(self, value: list[_S], /) -> list[_S | _T]:
        raise AssumedToBeImplementedException

    def __add__(self, value: list[Any], /) -> list[Any]:
        raise AssumedToBeImplementedException

    def __iadd__(self, value: Iterable[_T], /) -> Self:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    def __mul__(self, value: SupportsIndex, /) -> list[_T]:
        raise AssumedToBeImplementedException

    def __rmul__(self, value: SupportsIndex, /) -> list[_T]:
        raise AssumedToBeImplementedException

    def __imul__(self, value: SupportsIndex, /) -> Self:
        raise AssumedToBeImplementedException

    def __contains__(self, key: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __reversed__(self) -> Iterator[_T]:
        raise AssumedToBeImplementedException

    def __gt__(self, value: list[_T], /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: list[_T], /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, value: list[_T], /) -> bool:
        raise AssumedToBeImplementedException

    def __le__(self, value: list[_T], /) -> bool:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    # def __class_getitem__(cls, item: Any, /) -> GenericAlias:
    #     raise AssumedToBeImplementedException


# @disjoint_base
# class dict(MutableMapping[_KT, _VT]):
class IsDict(IsMutableMapping[_KT, _VT], Protocol[_KT, _VT]):
    """Protocol with the same interface as the builtin class `dict`.
    """

    # __init__ should be kept roughly in line with
    # `collections.UserDict.__init__`, which has similar semantics Also
    # multiprocessing.managers.SyncManager.dict()
    # @overload
    # def __init__(self, /) -> None:
    #     ...
    #
    # @overload
    # def __init__(self: dict[str, _VT], /, **kwargs: _VT) -> None:
    #     ...  # pyright: ignore[reportInvalidTypeVarUse]  #11780
    #
    # @overload
    # def __init__(self, map: SupportsKeysAndGetItem[_KT, _VT], /) -> None:
    #     ...
    #
    # @overload
    # def __init__(
    #     self: dict[str, _VT],  # pyright: ignore[reportInvalidTypeVarUse]  #11780
    #     map: SupportsKeysAndGetItem[str, _VT],
    #     /,
    #     **kwargs: _VT,
    # ) -> None:
    #     ...
    #
    # @overload
    # def __init__(self, iterable: Iterable[tuple[_KT, _VT]], /) -> None:
    #     ...
    #
    # @overload
    # def __init__(
    #     self: dict[str, _VT],  # pyright: ignore[reportInvalidTypeVarUse]  #11780
    #     iterable: Iterable[tuple[str, _VT]],
    #     /,
    #     **kwargs: _VT,
    # ) -> None:
    #     ...
    #
    # # Next two overloads are for dict(string.split(sep) for string in iterable)
    # # Cannot be Iterable[Sequence[_T]] or otherwise dict(['foo', 'bar', 'baz']) is not an error
    # @overload
    # def __init__(self: dict[str, str], iterable: Iterable[list[str]], /) -> None:
    #     ...
    #
    # @overload
    # def __init__(self: dict[bytes, bytes], iterable: Iterable[list[bytes]], /) -> None:
    #     ...
    #
    # def __new__(cls, /, *args: Any, **kwargs: Any) -> Self:
    #     ...

    # def copy(self) -> dict[_KT, _VT]:
    #     raise AssumedToBeImplementedException

    # def keys(self) -> dict_keys[_KT, _VT]:
    def keys(self) -> IsDictKeys[_KT, _VT]:
        raise AssumedToBeImplementedException

    # def values(self) -> dict_values[_KT, _VT]:
    def values(self) -> IsDictValues[_KT, _VT]:
        raise AssumedToBeImplementedException

    # def items(self) -> dict_items[_KT, _VT]:
    def items(self) -> IsDictItems[_KT, _VT]:
        raise AssumedToBeImplementedException

    # Signature of `dict.fromkeys` should be kept identical to
    # `fromkeys` methods of `OrderedDict`/`ChainMap`/`UserDict` in `collections`
    # FIXME: the true signature of `dict.fromkeys` is not expressible in the current type system.
    # See #3800 & https://github.com/python/typing/issues/548#issuecomment-683336963.
    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_T], value: None = None, /) -> dict[_T, Any | None]:
        raise AssumedToBeImplementedException

    @classmethod
    @overload
    def fromkeys(cls, iterable: Iterable[_T], value: _S, /) -> dict[_T, _S]:
        raise AssumedToBeImplementedException

    @classmethod
    def fromkeys(
        cls,
        iterable: Iterable[_T],
        value: _S | None = None,
        /,
    ) -> dict[_T, _S] | dict[_T, Any | None]:
        raise AssumedToBeImplementedException

    # Positional-only in dict, but not in IsMutableMapping
    @overload
    def get(self, key: _KT, default: None = None, /) -> _VT | None:
        raise AssumedToBeImplementedException

    @overload
    def get(self, key: _KT, default: _VT, /) -> _VT:
        raise AssumedToBeImplementedException

    @overload
    def get(self, key: _KT, default: _T, /) -> _VT | _T:
        raise AssumedToBeImplementedException

    def get(self, key: _KT, default: None | _VT | _T = None, /) -> _VT | _T | None:
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
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __getitem__(self, key: _KT, /) -> _VT:
        raise AssumedToBeImplementedException

    def __setitem__(self, key: _KT, value: _VT, /) -> None:
        raise AssumedToBeImplementedException

    def __delitem__(self, key: _KT, /) -> None:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_KT]:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __reversed__(self) -> Iterator[_KT]:
        raise AssumedToBeImplementedException

    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    # def __class_getitem__(cls, item: Any, /) -> GenericAlias:
    #     raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: dict[_KT, _VT], /) -> dict[_KT, _VT]:
        raise AssumedToBeImplementedException

    @overload
    def __or__(self, value: dict[_T1, _T2], /) -> dict[_KT | _T1, _VT | _T2]:
        raise AssumedToBeImplementedException

    def __or__(self, value: dict[Any, Any], /) -> dict[Any, Any]:
        raise AssumedToBeImplementedException

    @overload
    def __ror__(self, value: dict[_KT, _VT], /) -> dict[_KT, _VT]:
        raise AssumedToBeImplementedException

    @overload
    def __ror__(self, value: dict[_T1, _T2], /) -> dict[_KT | _T1, _VT | _T2]:
        raise AssumedToBeImplementedException

    def __ror__(self, value: dict[Any, Any], /) -> dict[Any, Any]:
        raise AssumedToBeImplementedException

    # dict.__ior__ should be kept roughly in line with IsMutableMapping.update()
    @overload  # type: ignore[misc]
    def __ior__(self, value: SupportsKeysAndGetItem[_KT, _VT], /) -> Self:
        raise AssumedToBeImplementedException

    @overload
    def __ior__(self, value: Iterable[tuple[_KT, _VT]], /) -> Self:
        raise AssumedToBeImplementedException

    def __ior__(  # type: ignore[misc]
        self,
        value: SupportsKeysAndGetItem[_KT, _VT] | Iterable[tuple[_KT, _VT]],
        /,
    ) -> Self:
        raise AssumedToBeImplementedException


# @disjoint_base
# class set(MutableSet[_T]):
class IsSet(IsMutableSet[_T], Protocol[_T]):
    """Protocol with the same interface as the builtin class `set`.
    """

    # @overload
    # def __init__(self) -> None:
    #     ...
    #
    # @overload
    # def __init__(self, iterable: Iterable[_T], /) -> None:
    #     ...

    def add(self, element: _T, /) -> None:
        raise AssumedToBeImplementedException

    # def copy(self) -> set[_T]:
    #     raise AssumedToBeImplementedException

    def difference(self, *s: Iterable[Any]) -> set[_T]:
        raise AssumedToBeImplementedException

    def difference_update(self, *s: Iterable[Any]) -> None:
        raise AssumedToBeImplementedException

    def discard(self, element: _T, /) -> None:
        raise AssumedToBeImplementedException

    def intersection(self, *s: Iterable[Any]) -> set[_T]:
        raise AssumedToBeImplementedException

    def intersection_update(self, *s: Iterable[Any]) -> None:
        raise AssumedToBeImplementedException

    def isdisjoint(self, s: Iterable[Any], /) -> bool:
        raise AssumedToBeImplementedException

    def issubset(self, s: Iterable[Any], /) -> bool:
        raise AssumedToBeImplementedException

    def issuperset(self, s: Iterable[Any], /) -> bool:
        raise AssumedToBeImplementedException

    def remove(self, element: _T, /) -> None:
        raise AssumedToBeImplementedException

    def symmetric_difference(self, s: Iterable[_T], /) -> set[_T]:
        raise AssumedToBeImplementedException

    def symmetric_difference_update(self, s: Iterable[_T], /) -> None:
        raise AssumedToBeImplementedException

    def union(self, *s: Iterable[_S]) -> set[_T | _S]:
        raise AssumedToBeImplementedException

    def update(self, *s: Iterable[_T]) -> None:
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __contains__(self, o: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_T]:
        raise AssumedToBeImplementedException

    def __and__(self, value: AbstractSet[object], /) -> set[_T]:
        raise AssumedToBeImplementedException

    def __iand__(self, value: AbstractSet[object], /) -> set[_T]:
        raise AssumedToBeImplementedException

    def __or__(self, value: AbstractSet[_S], /) -> set[_T | _S]:
        raise AssumedToBeImplementedException

    def __ior__(self, value: AbstractSet[_T], /) -> set[_T]:  # type: ignore[override,misc]
        raise AssumedToBeImplementedException

    def __sub__(self, value: AbstractSet[_T | None], /) -> set[_T]:
        raise AssumedToBeImplementedException

    def __isub__(self, value: AbstractSet[object], /) -> set[_T]:
        raise AssumedToBeImplementedException

    def __xor__(self, value: AbstractSet[_S], /) -> set[_T | _S]:
        raise AssumedToBeImplementedException

    def __ixor__(self, value: AbstractSet[_T], /) -> set[_T]:  # type: ignore[override,misc]
        raise AssumedToBeImplementedException

    def __le__(self, value: AbstractSet[object], /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, value: AbstractSet[object], /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: AbstractSet[object], /) -> bool:
        raise AssumedToBeImplementedException

    def __gt__(self, value: AbstractSet[object], /) -> bool:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    # def __class_getitem__(cls, item: Any, /) -> GenericAlias:
    #     raise AssumedToBeImplementedException


# @disjoint_base
# class frozenset(IsAbstractSet[_T_co]):
class IsFrozenSet(IsAbstractSet[_T_co], Protocol[_T_co]):  # type: ignore[misc]
    """Protocol with the same interface as the builtin class `frozenset`.
    """

    # @overload
    # def __new__(cls) -> Self:
    #     raise AssumedToBeImplementedException
    #
    # @overload
    # def __new__(cls, iterable: Iterable[_T_co], /) -> Self:
    #     raise AssumedToBeImplementedException

    # def copy(self) -> frozenset[_T_co]:
    #     raise AssumedToBeImplementedException

    def difference(self, *s: Iterable[object]) -> frozenset[_T_co]:
        raise AssumedToBeImplementedException

    def intersection(self, *s: Iterable[object]) -> frozenset[_T_co]:
        raise AssumedToBeImplementedException

    def isdisjoint(self, s: Iterable[_T_co], /) -> bool:
        raise AssumedToBeImplementedException

    def issubset(self, s: Iterable[object], /) -> bool:
        raise AssumedToBeImplementedException

    def issuperset(self, s: Iterable[object], /) -> bool:
        raise AssumedToBeImplementedException

    def symmetric_difference(self, s: Iterable[_T_co], /) -> frozenset[_T_co]:
        raise AssumedToBeImplementedException

    def union(self, *s: Iterable[_S]) -> frozenset[_T_co | _S]:
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __contains__(self, o: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_T_co]:
        raise AssumedToBeImplementedException

    def __and__(self, value: AbstractSet[_T_co], /) -> frozenset[_T_co]:
        raise AssumedToBeImplementedException

    def __or__(self, value: AbstractSet[_S], /) -> frozenset[_T_co | _S]:
        raise AssumedToBeImplementedException

    def __sub__(self, value: AbstractSet[_T_co], /) -> frozenset[_T_co]:
        raise AssumedToBeImplementedException

    def __xor__(self, value: AbstractSet[_S], /) -> frozenset[_T_co | _S]:
        raise AssumedToBeImplementedException

    def __le__(self, value: AbstractSet[object], /) -> bool:
        raise AssumedToBeImplementedException

    def __lt__(self, value: AbstractSet[object], /) -> bool:
        raise AssumedToBeImplementedException

    def __ge__(self, value: AbstractSet[object], /) -> bool:
        raise AssumedToBeImplementedException

    def __gt__(self, value: AbstractSet[object], /) -> bool:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __hash__(self) -> int:
        raise AssumedToBeImplementedException

    # def __class_getitem__(cls, item: Any, /) -> GenericAlias:
    # def __class_getitem__(cls, item: Any, /) -> GenericAlias:
    #     raise AssumedToBeImplementedException
