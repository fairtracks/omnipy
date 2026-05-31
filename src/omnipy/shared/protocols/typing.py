# Modified from the "typing.pyi" file in the `_typeshed_import` directory,
# which was imported from the Typeshed (https://github.com/python/typeshed).
#
# The Typeshed is licensed under the Apache License, Version 2.0 and the
# MIT License. See the LICENSE file in the root of the repository for
# details (https://github.com/python/typeshed/blob/main/LICENSE).
#
# See "typing.pyi" for more details.

# flake8: noqa
# isort: skip_file

"""Typing-inspired protocol definitions shared across Omnipy."""

from __future__ import annotations

# import collections  # noqa: F401  # pyright: ignore[reportUnusedImport]
import sys
# import typing_extensions
# from _collections_abc import dict_items, dict_keys, dict_values
from collections.abc import Collection, Iterable, Iterator, Reversible
# from _typeshed import IdentityFunction, ReadableBuffer, SupportsGetItem, SupportsGetItemViewable, SupportsKeysAndGetItem, Viewable
# from abc import ABCMeta, abstractmethod
# from re import Match as Match, Pattern as Pattern
from types import (
    # BuiltinFunctionType,
    # CodeType,
    # FunctionType,
    # GenericAlias,
    # MethodDescriptorType,
    # MethodType,
    # MethodWrapperType,
    # ModuleType,
    TracebackType,
    # UnionType,
    # WrapperDescriptorType,
)
from typing import AbstractSet, Any, AnyStr, overload, Protocol, runtime_checkable
# from typing_extensions import Never as _Never, deprecated
from typing_extensions import Self, TypeVar

# if sys.version_info >= (3, 14):
#     from _typeshed import EvaluateFunc
#
#     from annotationlib import Format


from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols._typeshed import (ReadableBuffer,
                                               SupportsGetItem,
                                               SupportsKeysAndGetItem)

# Note: importing SupportsKeysAndGetItem from _typeshed instead of the
#       local copy causes basedpyright to enter an infinite loop.
#       This seems to be connected to the resolution of
#       IsMutableMapping.update, and might be a bug in basedpyright.
#       Hence, we instead maintain a local copy of the elements used
#       from _typeshed.

# __all__ = [
#     "AbstractSet",
#     "Annotated",
#     "Any",
#     "AnyStr",
#     "AsyncContextManager",
#     "AsyncGenerator",
#     "AsyncIterable",
#     "AsyncIterator",
#     "Awaitable",
#     "BinaryIO",
#     "Callable",
#     "ChainMap",
#     "ClassVar",
#     "Collection",
#     "Concatenate",
#     "Container",
#     "ContextManager",
#     "Coroutine",
#     "Counter",
#     "DefaultDict",
#     "Deque",
#     "Dict",
#     "Final",
#     "ForwardRef",
#     "FrozenSet",
#     "Generator",
#     "Generic",
#     "Hashable",
#     "IO",
#     "ItemsView",
#     "Iterable",
#     "Iterator",
#     "KeysView",
#     "List",
#     "Literal",
#     "Mapping",
#     "MappingView",
#     "Match",
#     "MutableMapping",
#     "MutableSequence",
#     "MutableSet",
#     "NamedTuple",
#     "NewType",
#     "NoReturn",
#     "Optional",
#     "OrderedDict",
#     "ParamSpec",
#     "ParamSpecArgs",
#     "ParamSpecKwargs",
#     "Pattern",
#     "Protocol",
#     "Reversible",
#     "Sequence",
#     "Set",
#     "Sized",
#     "SupportsAbs",
#     "SupportsBytes",
#     "SupportsComplex",
#     "SupportsFloat",
#     "SupportsIndex",
#     "SupportsInt",
#     "SupportsRound",
#     "Text",
#     "TextIO",
#     "Tuple",
#     "Type",
#     "TypeAlias",
#     "TypeGuard",
#     "TypeVar",
#     "TypedDict",
#     "Union",
#     "ValuesView",
#     "TYPE_CHECKING",
#     "cast",
#     "final",
#     "get_args",
#     "get_origin",
#     "get_type_hints",
#     "is_typeddict",
#     "no_type_check",
#     "overload",
#     "runtime_checkable",
# ]
#
# if sys.version_info < (3, 15):
#     __all__ += ["ByteString", "no_type_check_decorator"]
#
# if sys.version_info >= (3, 14):
#     __all__ += ["evaluate_forward_ref"]
#
# if sys.version_info >= (3, 15):
#     __all__ += ["NoExtraItems", "TypeForm", "disjoint_base"]
#
# if sys.version_info >= (3, 11):
#     __all__ += [
#         "LiteralString",
#         "Never",
#         "NotRequired",
#         "Required",
#         "Self",
#         "TypeVarTuple",
#         "Unpack",
#         "assert_never",
#         "assert_type",
#         "clear_overloads",
#         "dataclass_transform",
#         "get_overloads",
#         "reveal_type",
#     ]
#
# if sys.version_info >= (3, 12):
#     __all__ += ["TypeAliasType", "override"]
#
# if sys.version_info >= (3, 13):
#     __all__ += ["get_protocol_members", "is_protocol", "NoDefault", "TypeIs", "ReadOnly"]

# # We can't use this name here because it leads to issues with mypy, likely
# # due to an import cycle. Below instead we use Any with a comment.
# # from _typeshed import AnnotationForm
#
# class Any: ...
#
# class _Final:
#     __slots__ = ("__weakref__",)
#
# def final(f: _T) -> _T: ...
#
# @final
# class TypeVar:
#     @property
#     def __name__(self) -> str: ...
#     @property
#     def __bound__(self) -> Any | None: ...  # AnnotationForm
#     @property
#     def __constraints__(self) -> tuple[Any, ...]: ...  # AnnotationForm
#     @property
#     def __covariant__(self) -> bool: ...
#     @property
#     def __contravariant__(self) -> bool: ...
#     if sys.version_info >= (3, 12):
#         @property
#         def __infer_variance__(self) -> bool: ...
#     if sys.version_info >= (3, 13):
#         @property
#         def __default__(self) -> Any: ...  # AnnotationForm
#     if sys.version_info >= (3, 13):
#         def __new__(
#             cls,
#             name: str,
#             *constraints: Any,  # AnnotationForm
#             bound: Any | None = None,  # AnnotationForm
#             contravariant: bool = False,
#             covariant: bool = False,
#             infer_variance: bool = False,
#             default: Any = ...,  # AnnotationForm
#         ) -> Self: ...
#     elif sys.version_info >= (3, 12):
#         def __new__(
#             cls,
#             name: str,
#             *constraints: Any,  # AnnotationForm
#             bound: Any | None = None,  # AnnotationForm
#             covariant: bool = False,
#             contravariant: bool = False,
#             infer_variance: bool = False,
#         ) -> Self: ...
#     elif sys.version_info >= (3, 11):
#         def __new__(
#             cls,
#             name: str,
#             *constraints: Any,  # AnnotationForm
#             bound: Any | None = None,  # AnnotationForm
#             covariant: bool = False,
#             contravariant: bool = False,
#         ) -> Self: ...
#     else:
#         def __init__(
#             self,
#             name: str,
#             *constraints: Any,  # AnnotationForm
#             bound: Any | None = None,  # AnnotationForm
#             covariant: bool = False,
#             contravariant: bool = False,
#         ) -> None: ...
#
#     def __or__(self, right: Any, /) -> _SpecialForm: ...  # AnnotationForm
#     def __ror__(self, left: Any, /) -> _SpecialForm: ...  # AnnotationForm
#     if sys.version_info >= (3, 11):
#         def __typing_subst__(self, arg: Any, /) -> Any: ...
#     if sys.version_info >= (3, 13):
#         def __typing_prepare_subst__(self, alias: Any, args: Any, /) -> tuple[Any, ...]: ...
#         def has_default(self) -> bool: ...
#     if sys.version_info >= (3, 14):
#         @property
#         def evaluate_bound(self) -> EvaluateFunc | None: ...
#         @property
#         def evaluate_constraints(self) -> EvaluateFunc | None: ...
#         @property
#         def evaluate_default(self) -> EvaluateFunc | None: ...
#
# # N.B. Keep this definition in sync with typing_extensions._SpecialForm
# @final
# class _SpecialForm(_Final):
#     __slots__ = ("_name", "__doc__", "_getitem")
#     def __getitem__(self, parameters: Any) -> object: ...
#     def __or__(self, other: Any) -> _SpecialForm: ...
#     def __ror__(self, other: Any) -> _SpecialForm: ...
#
# Union: _SpecialForm
# Protocol: _SpecialForm
# Callable: _SpecialForm
# Type: _SpecialForm
# NoReturn: _SpecialForm
# ClassVar: _SpecialForm
#
# Optional: _SpecialForm
# Tuple: _SpecialForm
# Final: _SpecialForm
#
# Literal: _SpecialForm
# TypedDict: _SpecialForm
#
# if sys.version_info >= (3, 11):
#     Self: _SpecialForm
#     Never: _SpecialForm
#     Unpack: _SpecialForm
#     Required: _SpecialForm
#     NotRequired: _SpecialForm
#     LiteralString: _SpecialForm
#
#     @final
#     class TypeVarTuple:
#         @property
#         def __name__(self) -> str: ...
#         if sys.version_info >= (3, 15):
#             @property
#             def __bound__(self) -> Any | None: ...  # AnnotationForm
#             @property
#             def __covariant__(self) -> bool: ...
#             @property
#             def __contravariant__(self) -> bool: ...
#             @property
#             def __infer_variance__(self) -> bool: ...
#         if sys.version_info >= (3, 13):
#             @property
#             def __default__(self) -> Any: ...  # AnnotationForm
#             def has_default(self) -> bool: ...
#         if sys.version_info >= (3, 15):
#             def __new__(
#                 cls,
#                 name: str,
#                 *,
#                 bound: Any | None = None,  # AnnotationForm
#                 covariant: bool = False,
#                 contravariant: bool = False,
#                 default: Any = ...,  # AnnotationForm
#                 infer_variance: bool = False,
#             ) -> Self: ...
#         elif sys.version_info >= (3, 13):
#             def __new__(cls, name: str, *, default: Any = ...) -> Self: ...  # AnnotationForm
#         elif sys.version_info >= (3, 12):
#             def __new__(cls, name: str) -> Self: ...
#         else:
#             def __init__(self, name: str) -> None: ...
#
#         def __iter__(self) -> Any: ...
#         def __typing_subst__(self, arg: Never, /) -> Never: ...
#         def __typing_prepare_subst__(self, alias: Any, args: Any, /) -> tuple[Any, ...]: ...
#         if sys.version_info >= (3, 14):
#             @property
#             def evaluate_default(self) -> EvaluateFunc | None: ...
#
# @final
# class ParamSpecArgs:
#     @property
#     def __origin__(self) -> ParamSpec: ...
#     if sys.version_info >= (3, 12):
#         def __new__(cls, origin: ParamSpec) -> Self: ...
#     else:
#         def __init__(self, origin: ParamSpec) -> None: ...
#
#     def __eq__(self, other: object, /) -> bool: ...
#     __hash__: ClassVar[None]  # type: ignore[assignment]
#
# @final
# class ParamSpecKwargs:
#     @property
#     def __origin__(self) -> ParamSpec: ...
#     if sys.version_info >= (3, 12):
#         def __new__(cls, origin: ParamSpec) -> Self: ...
#     else:
#         def __init__(self, origin: ParamSpec) -> None: ...
#
#     def __eq__(self, other: object, /) -> bool: ...
#     __hash__: ClassVar[None]  # type: ignore[assignment]
#
# @final
# class ParamSpec:
#     @property
#     def __name__(self) -> str: ...
#     @property
#     def __bound__(self) -> Any | None: ...  # AnnotationForm
#     @property
#     def __covariant__(self) -> bool: ...
#     @property
#     def __contravariant__(self) -> bool: ...
#     if sys.version_info >= (3, 12):
#         @property
#         def __infer_variance__(self) -> bool: ...
#     if sys.version_info >= (3, 13):
#         @property
#         def __default__(self) -> Any: ...  # AnnotationForm
#     if sys.version_info >= (3, 13):
#         def __new__(
#             cls,
#             name: str,
#             *,
#             bound: Any | None = None,  # AnnotationForm
#             contravariant: bool = False,
#             covariant: bool = False,
#             infer_variance: bool = False,
#             default: Any = ...,  # AnnotationForm
#         ) -> Self: ...
#     elif sys.version_info >= (3, 12):
#         def __new__(
#             cls,
#             name: str,
#             *,
#             bound: Any | None = None,  # AnnotationForm
#             contravariant: bool = False,
#             covariant: bool = False,
#             infer_variance: bool = False,
#         ) -> Self: ...
#     elif sys.version_info >= (3, 11):
#         def __new__(
#             cls, name: str, *, bound: Any | None = None, contravariant: bool = False, covariant: bool = False  # AnnotationForm
#         ) -> Self: ...
#     else:
#         def __init__(
#             self, name: str, *, bound: Any | None = None, contravariant: bool = False, covariant: bool = False  # AnnotationForm
#         ) -> None: ...
#
#     @property
#     def args(self) -> ParamSpecArgs: ...
#     @property
#     def kwargs(self) -> ParamSpecKwargs: ...
#     if sys.version_info >= (3, 11):
#         def __typing_subst__(self, arg: Any, /) -> Any: ...
#         def __typing_prepare_subst__(self, alias: Any, args: Any, /) -> tuple[Any, ...]: ...
#
#     def __or__(self, right: Any, /) -> _SpecialForm: ...
#     def __ror__(self, left: Any, /) -> _SpecialForm: ...
#     if sys.version_info >= (3, 13):
#         def has_default(self) -> bool: ...
#     if sys.version_info >= (3, 14):
#         @property
#         def evaluate_default(self) -> EvaluateFunc | None: ...
#
# Concatenate: _SpecialForm
# TypeAlias: _SpecialForm
# TypeGuard: _SpecialForm
#
# class NewType:
#     def __init__(self, name: str, tp: Any) -> None: ...  # AnnotationForm
#     if sys.version_info >= (3, 11):
#         @staticmethod
#         def __call__(x: _T, /) -> _T: ...
#     else:
#         def __call__(self, x: _T) -> _T: ...
#
#     def __or__(self, other: Any) -> _SpecialForm: ...
#     def __ror__(self, other: Any) -> _SpecialForm: ...
#     __supertype__: type | NewType
#     __name__: str

# _F = TypeVar("_F", bound=Callable[..., Any])
# _P = ParamSpec("_P")
_T = TypeVar("_T")

# _FT = TypeVar("_FT", bound=Callable[..., Any] | type)

# These type variables are used by the container types.
# _S = TypeVar("_S")
_KT = TypeVar("_KT")  # Key type.
_VT = TypeVar("_VT")  # Value type.
_T_co = TypeVar("_T_co", covariant=True)  # Any type covariant containers.
_KT_co = TypeVar("_KT_co", covariant=True)  # Key type covariant containers.
_VT_co = TypeVar("_VT_co", covariant=True)  # Value type covariant containers.
# _TC = TypeVar("_TC", bound=type[object])

# def overload(func: _F) -> _F: ...
# def no_type_check(arg: _F) -> _F: ...
#
# if sys.version_info < (3, 15):
#     @deprecated("Deprecated since Python 3.13; removed in Python 3.15.")
#     def no_type_check_decorator(decorator: Callable[_P, _T]) -> Callable[_P, _T]: ...
#
# if sys.version_info >= (3, 15):
#     def disjoint_base(cls: _TC) -> _TC: ...
#
# # This itself is only available during type checking
# def type_check_only(func_or_cls: _FT) -> _FT: ...
#
# # Type aliases and type constructors
#
# @type_check_only
# class _Alias:
#     # Class for defining generic aliases for library types.
#     def __getitem__(self, typeargs: Any) -> Any: ...
#
# List = _Alias()
# Dict = _Alias()
# DefaultDict = _Alias()
# Set = _Alias()
# FrozenSet = _Alias()
# Counter = _Alias()
# Deque = _Alias()
# ChainMap = _Alias()
#
# OrderedDict = _Alias()
#
# Annotated: _SpecialForm
# if sys.version_info >= (3, 15):
#     @type_check_only
#     class _NoExtraItemsType: ...
#
#     NoExtraItems: _NoExtraItemsType
#
#     TypeForm: _SpecialForm
#
# # Predefined type variables.
# AnyStr = TypeVar("AnyStr", str, bytes)  # noqa: Y001
#
# @type_check_only
# class _Generic:
#     if sys.version_info < (3, 12):
#         __slots__ = ()
#
#     @classmethod
#     def __class_getitem__(cls, args: TypeVar | ParamSpec | tuple[TypeVar | ParamSpec, ...]) -> _Final: ...
#
# Generic: type[_Generic]
#
# class _ProtocolMeta(ABCMeta):
#     if sys.version_info >= (3, 12):
#         def __init__(cls, *args: Any, **kwargs: Any) -> None: ...
#
# # Abstract base classes.
#
# def runtime_checkable(cls: _TC) -> _TC: ...
#
# @runtime_checkable
# class SupportsInt(Protocol, metaclass=ABCMeta):
#     __slots__ = ()
#     @abstractmethod
#     def __int__(self) -> int: ...
#
# @runtime_checkable
# class SupportsFloat(Protocol, metaclass=ABCMeta):
#     __slots__ = ()
#     @abstractmethod
#     def __float__(self) -> float: ...
#
# @runtime_checkable
# class SupportsComplex(Protocol, metaclass=ABCMeta):
#     __slots__ = ()
#     @abstractmethod
#     def __complex__(self) -> complex: ...
#
# @runtime_checkable
# class SupportsBytes(Protocol, metaclass=ABCMeta):
#     __slots__ = ()
#     @abstractmethod
#     def __bytes__(self) -> bytes: ...
#
# @runtime_checkable
# class SupportsIndex(Protocol, metaclass=ABCMeta):
#     __slots__ = ()
#     @abstractmethod
#     def __index__(self) -> int: ...
#
# @runtime_checkable
# class SupportsAbs(Protocol[_T_co]):
#     __slots__ = ()
#     @abstractmethod
#     def __abs__(self) -> _T_co: ...
#
# @runtime_checkable
# class SupportsRound(Protocol[_T_co]):
#     __slots__ = ()
#
#     @overload
#     @abstractmethod
#     def __round__(self) -> int: ...
#     @overload
#     @abstractmethod
#     def __round__(self, ndigits: int, /) -> _T_co: ...
#
# @runtime_checkable
# class Sized(Protocol, metaclass=ABCMeta):
#     @abstractmethod
#     def __len__(self) -> int: ...

@runtime_checkable
# class Hashable(Protocol, metaclass=ABCMeta):
class IsHashable(Protocol):
    # TODO: This is special, in that a subclass of a hashable class may not be hashable
    #   (for example, list vs. object). It's not obvious how to represent this. This class
    #   is currently mostly useless for static checking.
    # @abstractmethod
    def __hash__(self) -> int: raise AssumedToBeImplementedException

# @runtime_checkable
# class Iterable(Protocol[_T_co]):
#     @abstractmethod
#     def __iter__(self) -> Iterator[_T_co]: ...
#
# @runtime_checkable
# class Iterator(Iterable[_T_co], Protocol[_T_co]):
#     @abstractmethod
#     def __next__(self) -> _T_co: ...
#     def __iter__(self) -> Iterator[_T_co]: ...
#
# @runtime_checkable
# class Reversible(Iterable[_T_co], Protocol[_T_co]):
#     @abstractmethod
#     def __reversed__(self) -> Iterator[_T_co]: ...
#
# _YieldT_co = TypeVar("_YieldT_co", covariant=True)
# _SendT_contra = TypeVar("_SendT_contra", contravariant=True, default=None)
# _ReturnT_co = TypeVar("_ReturnT_co", covariant=True, default=None)
#
# @runtime_checkable
# class Generator(Iterator[_YieldT_co], Protocol[_YieldT_co, _SendT_contra, _ReturnT_co]):
#     def __next__(self) -> _YieldT_co: ...
#     @abstractmethod
#     def send(self, value: _SendT_contra, /) -> _YieldT_co: ...
#
#     @overload
#     @abstractmethod
#     def throw(
#         self, typ: type[BaseException], val: BaseException | object = None, tb: TracebackType | None = None, /
#     ) -> _YieldT_co: ...
#     @overload
#     @abstractmethod
#     def throw(self, typ: BaseException, val: None = None, tb: TracebackType | None = None, /) -> _YieldT_co: ...
#
#     if sys.version_info >= (3, 13):
#         def close(self) -> _ReturnT_co | None: ...
#     else:
#         def close(self) -> None: ...
#
#     def __iter__(self) -> Generator[_YieldT_co, _SendT_contra, _ReturnT_co]: ...
#
# # NOTE: Prior to Python 3.13 these aliases are lacking the second _ExitT_co parameter
# if sys.version_info >= (3, 13):
#     from contextlib import AbstractAsyncContextManager as AsyncContextManager, AbstractContextManager as ContextManager
# else:
#     from contextlib import AbstractAsyncContextManager, AbstractContextManager
#
#     @runtime_checkable
#     class ContextManager(AbstractContextManager[_T_co, bool | None], Protocol[_T_co]): ...
#
#     @runtime_checkable
#     class AsyncContextManager(AbstractAsyncContextManager[_T_co, bool | None], Protocol[_T_co]): ...
#
# @runtime_checkable
# class Awaitable(Protocol[_T_co]):
#     @abstractmethod
#     def __await__(self) -> Generator[Any, Any, _T_co]: ...
#
# # Non-default variations to accommodate coroutines, and `AwaitableGenerator` having a 4th type parameter.
# _SendT_nd_contra = TypeVar("_SendT_nd_contra", contravariant=True)
# _ReturnT_nd_co = TypeVar("_ReturnT_nd_co", covariant=True)
#
# class Coroutine(Awaitable[_ReturnT_nd_co], Generic[_YieldT_co, _SendT_nd_contra, _ReturnT_nd_co]):
#     __name__: str
#     __qualname__: str
#
#     @abstractmethod
#     def send(self, value: _SendT_nd_contra, /) -> _YieldT_co: ...
#
#     @overload
#     @abstractmethod
#     def throw(
#         self, typ: type[BaseException], val: BaseException | object = None, tb: TracebackType | None = None, /
#     ) -> _YieldT_co: ...
#     @overload
#     @abstractmethod
#     def throw(self, typ: BaseException, val: None = None, tb: TracebackType | None = None, /) -> _YieldT_co: ...
#
#     @abstractmethod
#     def close(self) -> None: ...
#
# # NOTE: This type does not exist in typing.py or PEP 484 but mypy needs it to exist.
# # The parameters correspond to Generator, but the 4th is the original type.
# # Obsolete, use _typeshed._type_checker_internals.AwaitableGenerator instead.
# @type_check_only
# class AwaitableGenerator(
#     Awaitable[_ReturnT_nd_co],
#     Generator[_YieldT_co, _SendT_nd_contra, _ReturnT_nd_co],
#     Generic[_YieldT_co, _SendT_nd_contra, _ReturnT_nd_co, _S],
#     metaclass=ABCMeta,
# ): ...
#
# @runtime_checkable
# class AsyncIterable(Protocol[_T_co]):
#     @abstractmethod
#     def __aiter__(self) -> AsyncIterator[_T_co]: ...
#
# @runtime_checkable
# class AsyncIterator(AsyncIterable[_T_co], Protocol[_T_co]):
#     @abstractmethod
#     def __anext__(self) -> Awaitable[_T_co]: ...
#     def __aiter__(self) -> AsyncIterator[_T_co]: ...
#
# @runtime_checkable
# class AsyncGenerator(AsyncIterator[_YieldT_co], Protocol[_YieldT_co, _SendT_contra]):
#     def __anext__(self) -> Coroutine[Any, Any, _YieldT_co]: ...
#     @abstractmethod
#     def asend(self, value: _SendT_contra, /) -> Coroutine[Any, Any, _YieldT_co]: ...
#
#     @overload
#     @abstractmethod
#     def athrow(
#         self, typ: type[BaseException], val: BaseException | object = None, tb: TracebackType | None = None, /
#     ) -> Coroutine[Any, Any, _YieldT_co]: ...
#     @overload
#     @abstractmethod
#     def athrow(
#         self, typ: BaseException, val: None = None, tb: TracebackType | None = None, /
#     ) -> Coroutine[Any, Any, _YieldT_co]: ...
#
#     def aclose(self) -> Coroutine[Any, Any, None]: ...
#
# _ContainerT_contra = TypeVar("_ContainerT_contra", contravariant=True, default=Any)
#
# @runtime_checkable
# class Container(Protocol[_ContainerT_contra]):
#     # This is generic more on vibes than anything else
#     @abstractmethod
#     def __contains__(self, x: _ContainerT_contra, /) -> bool: ...
#
# @runtime_checkable
# class Collection(Iterable[_T_co], Container[Any], Protocol[_T_co]):
#     # Note: need to use Container[Any] instead of Container[_T_co] to ensure covariance.
#     # Implement Sized (but don't have it as a base class).
#     @abstractmethod
#     def __len__(self) -> int: ...


# class Sequence(Reversible[_T_co], Collection[_T_co]):
class IsItemSequence(Reversible[_T_co], Collection[_T_co], Protocol[_T_co]):
    """Protocol with the same interface as the abstract class `typing.Sequence`.

    Note that with no custom handling, as is typically done in a type
    checker, the `string`, `bytes`, and `bytearray` types will not be
    considered Sequences by this protocol, due to differences in the
    `__contains__` method.
    """
    @overload
    # @abstractmethod
    def __getitem__(self, index: int, /) -> _T_co: raise AssumedToBeImplementedException
    @overload
    # @abstractmethod
    # def __getitem__(self, index: slice[int | None], /) -> Sequence[_T_co]:
    def __getitem__(self, index: slice, /) -> IsItemSequence[_T_co]: raise AssumedToBeImplementedException
    def __getitem__(self, index: int | slice, /) -> _T_co | IsItemSequence[_T_co]: raise AssumedToBeImplementedException

    # Mixin methods
    # def index(self, value: Any, start: int = 0, stop: int = ..., /) -> int:
    # Omnipy: start and stop removed to support range as IsItemSequence
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

    def __contains__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[_T_co]: raise AssumedToBeImplementedException
    def __reversed__(self) -> Iterator[_T_co]: raise AssumedToBeImplementedException

# class MutableSequence(Sequence[_T]):
class IsMutableSequence(IsItemSequence[_T], Protocol[_T]):
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
    def __getitem__(self, index: int, /) -> _T: raise AssumedToBeImplementedException
    @overload
    # @abstractmethod
    # def __getitem__(self, index: slice[int | None], /) -> MutableSequence[_T]: ...
    def __getitem__(self, index: slice, /) -> IsMutableSequence[_T]: raise AssumedToBeImplementedException
    def __getitem__(self, index: int | slice, /) -> _T | IsMutableSequence[_T_co]: raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    def __setitem__(self, index: int, value: _T, /) -> None: raise AssumedToBeImplementedException
    @overload
    # @abstractmethod
    # def __setitem__(self, index: slice[int | None], value: Iterable[_T], /) -> None: ...
    def __setitem__(self, index: slice, value: Iterable[_T], /) -> None: raise AssumedToBeImplementedException
    def __setitem__(self, index: int | slice, value: _T | Iterable[_T], /) -> None: raise AssumedToBeImplementedException

    @overload
    # @abstractmethod
    def __delitem__(self, index: int, /) -> None: raise AssumedToBeImplementedException
    @overload
    # @abstractmethod
    # def __delitem__(self, index: slice[int | None], /) -> None: ...
    def __delitem__(self, index: slice, /) -> None: raise AssumedToBeImplementedException
    def __delitem__(self, index: int | slice, /) -> None: raise AssumedToBeImplementedException

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

    def __iadd__(self, values: Iterable[_T], /) -> Self: raise AssumedToBeImplementedException

# class AbstractSet(Collection[_T_co]):
class IsAbstractSet(Collection[_T_co], Protocol[_T_co]):
    """Protocol with the same interface as the abstract class `typing.AbstractSet`.
    """
    # @abstractmethod
    def __contains__(self, x: object, /) -> bool: raise AssumedToBeImplementedException
    def _hash(self) -> int: raise AssumedToBeImplementedException
    # # Mixin methods
    # @classmethod
    # def _from_iterable(cls, it: Iterable[_S], /) -> IsAbstractSet[_S]: raise AssumedToBeImplementedException
    def __le__(self, other: AbstractSet[Any], /) -> bool: raise AssumedToBeImplementedException
    def __lt__(self, other: AbstractSet[Any], /) -> bool: raise AssumedToBeImplementedException
    def __gt__(self, other: AbstractSet[Any], /) -> bool: raise AssumedToBeImplementedException
    def __ge__(self, other: AbstractSet[Any], /) -> bool: raise AssumedToBeImplementedException
    def __and__(self, other: AbstractSet[Any], /) -> AbstractSet[_T_co]: raise AssumedToBeImplementedException
    def __or__(self, other: AbstractSet[_T], /) -> AbstractSet[_T_co | _T]: raise AssumedToBeImplementedException
    def __sub__(self, other: AbstractSet[Any], /) -> AbstractSet[_T_co]: raise AssumedToBeImplementedException
    def __xor__(self, other: AbstractSet[_T], /) -> AbstractSet[_T_co | _T]: raise AssumedToBeImplementedException
    def __eq__(self, other: object, /) -> bool: raise AssumedToBeImplementedException
    def isdisjoint(self, other: Iterable[Any], /) -> bool: raise AssumedToBeImplementedException

# class MutableSet(AbstractSet[_T]):
class IsMutableSet(IsAbstractSet[_T], Protocol[_T]):
    """Protocol with the same interface as the abstract class `typing.MutableSet`.
    """
    # @abstractmethod
    def add(self, value: _T, /) -> None: raise AssumedToBeImplementedException
    # @abstractmethod
    def discard(self, value: _T, /) -> None: raise AssumedToBeImplementedException
    # Mixin methods
    def clear(self) -> None: raise AssumedToBeImplementedException
    def pop(self) -> _T: raise AssumedToBeImplementedException
    def remove(self, value: _T, /) -> None: raise AssumedToBeImplementedException
    def __ior__(self, it: AbstractSet[_T], /) -> Self: raise AssumedToBeImplementedException  # type: ignore[misc, override]
    # def __iand__(self, it: AbstractSet[Any], /) -> typing_extensions.Self: ...
    def __iand__(self, it: AbstractSet[Any], /) -> Self: raise AssumedToBeImplementedException
    def __ixor__(self, it: AbstractSet[_T], /) -> Self: raise AssumedToBeImplementedException  # type: ignore[misc, override]
    # def __isub__(self, it: AbstractSet[Any], /) -> typing_extensions.Self: ...
    def __isub__(self, it: AbstractSet[Any], /) -> Self: raise AssumedToBeImplementedException

# class MappingView(Sized):
class IsMappingView(Protocol):
    """Protocol with the same interface as the abstract class `typing.MappingView`.
    """
    # __slots__ = ("_mapping",)
    # def __init__(self, mapping: Sized) -> None: ...  # undocumented
    def __len__(self) -> int: raise AssumedToBeImplementedException

# class ItemsView(MappingView, AbstractSet[tuple[_KT_co, _VT_co]], Generic[_KT_co, _VT_co]):
class IsItemsView(IsMappingView, IsAbstractSet[tuple[_KT_co, _VT_co]], Protocol[_KT_co, _VT_co]):
    """Protocol with the same interface as the abstract class `typing.ItemsView`.
    """
    # def __init__(self, mapping: SupportsGetItemViewable[_KT_co, _VT_co]) -> None: ...  # undocumented
    # @classmethod
    # def _from_iterable(cls, it: Iterable[_S], /) -> set[_S]: ...
    def __and__(self, other: Iterable[Any], /) -> set[tuple[_KT_co, _VT_co]]: raise AssumedToBeImplementedException
    def __rand__(self, other: Iterable[_T], /) -> set[_T]: raise AssumedToBeImplementedException
    def __contains__(self, item: tuple[object, object], /) -> bool: raise AssumedToBeImplementedException  # type: ignore[override]
    def __iter__(self) -> Iterator[tuple[_KT_co, _VT_co]]: raise AssumedToBeImplementedException
    def __or__(self, other: Iterable[_T], /) -> set[tuple[_KT_co, _VT_co] | _T]: raise AssumedToBeImplementedException
    def __ror__(self, other: Iterable[_T], /) -> set[tuple[_KT_co, _VT_co] | _T]: raise AssumedToBeImplementedException
    def __sub__(self, other: Iterable[Any], /) -> set[tuple[_KT_co, _VT_co]]: raise AssumedToBeImplementedException
    def __rsub__(self, other: Iterable[_T], /) -> set[_T]: raise AssumedToBeImplementedException
    def __xor__(self, other: Iterable[_T], /) -> set[tuple[_KT_co, _VT_co] | _T]: raise AssumedToBeImplementedException
    def __rxor__(self, other: Iterable[_T], /) -> set[tuple[_KT_co, _VT_co] | _T]: raise AssumedToBeImplementedException

# class KeysView(MappingView, AbstractSet[_KT_co]):
class IsKeysView(IsMappingView, IsAbstractSet[_KT_co], Protocol[_KT_co]):  # type: ignore[misc]
    """Protocol with the same interface as the abstract class `typing.KeysView`.
    """
    # def __init__(self, mapping: Viewable[_KT_co]) -> None: ...  # undocumented
    # @classmethod
    # def _from_iterable(cls, it: Iterable[_S], /) -> set[_S]: ...
    def __and__(self, other: Iterable[Any], /) -> set[_KT_co]: raise AssumedToBeImplementedException
    def __rand__(self, other: Iterable[_T], /) -> set[_T]: raise AssumedToBeImplementedException
    def __contains__(self, key: object, /) -> bool: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[_KT_co]: raise AssumedToBeImplementedException
    def __or__(self, other: Iterable[_T], /) -> set[_KT_co | _T]: raise AssumedToBeImplementedException
    def __ror__(self, other: Iterable[_T], /) -> set[_KT_co | _T]: raise AssumedToBeImplementedException
    def __sub__(self, other: Iterable[Any], /) -> set[_KT_co]: raise AssumedToBeImplementedException
    def __rsub__(self, other: Iterable[_T], /) -> set[_T]: raise AssumedToBeImplementedException
    def __xor__(self, other: Iterable[_T], /) -> set[_KT_co | _T]: raise AssumedToBeImplementedException
    def __rxor__(self, other: Iterable[_T], /) -> set[_KT_co | _T]: raise AssumedToBeImplementedException


# class ValuesView(MappingView, Collection[_VT_co]):
class IsValuesView(IsMappingView, Collection[_VT_co], Protocol[_VT_co]):
    """Protocol with the same interface as the abstract class `typing.ValuesView`.
    """
    # def __init__(self, mapping: SupportsGetItemViewable[Any, _VT_co]) -> None: ...  # undocumented
    def __contains__(self, value: object, /) -> bool: raise AssumedToBeImplementedException
    def __iter__(self) -> Iterator[_VT_co]: raise AssumedToBeImplementedException


# note for Mapping.get and MutableMapping.pop and MutableMapping.setdefault
# In _collections_abc.py the parameters are positional-or-keyword,
# but dict and types.MappingProxyType (the vast majority of Mapping types)
# don't allow keyword arguments.


# class Mapping(Collection[_KT], Generic[_KT, _VT_co]):
@runtime_checkable
class IsMapping(Collection[_KT], Protocol[_KT, _VT_co]):  # type: ignore[misc]
    """Protocol with the same interface as the abstract class `typing.Mapping`.

    IsMapping is the protocol of a generic container for associating
    key/value pairs.
    """

    # TODO: We wish the key type could also be covariant, but that doesn't work,
    # see discussion in https://github.com/python/typing/pull/273.
    # @abstractmethod
    def __getitem__(self, key: _KT, /) -> _VT_co: raise AssumedToBeImplementedException

    # Mixin methods
    @overload
    def get(self, key: _KT, /) -> _VT_co | None: raise AssumedToBeImplementedException
    @overload
    def get(self, key: _KT, default: _VT_co, /) -> _VT_co: raise AssumedToBeImplementedException  # type: ignore[misc]
    @overload
    def get(self, key: _KT, default: _T, /) -> _VT_co | _T: raise AssumedToBeImplementedException
    def get(self, key: _KT, default: None | _VT_co | _T = None, /) -> _VT_co | _T | None:
        """
        D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        """
        raise AssumedToBeImplementedException

    # # def items(self) -> ItemsView[_KT, _VT_co]: ...
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

    def __contains__(self, key: object, /) -> bool: raise AssumedToBeImplementedException
    def __eq__(self, other: object, /) -> bool: raise AssumedToBeImplementedException

# class MutableMapping(Mapping[_KT, _VT]):
class IsMutableMapping(IsMapping[_KT, _VT], Protocol[_KT, _VT]):
    """Protocol with the same interface as the abstract class `typing.MutableMapping`.

    IsMutableMapping is the protocol of a generic mutable container for
    associating key/value pairs.
    """

    # @abstractmethod
    def __setitem__(self, key: _KT, value: _VT, /) -> None: raise AssumedToBeImplementedException
    # @abstractmethod
    def __delitem__(self, key: _KT, /) -> None: raise AssumedToBeImplementedException

    def clear(self) -> None:
        """
        D.clear() -> None.  Remove all items from D.
        """
        raise AssumedToBeImplementedException

    @overload
    def pop(self, key: _KT, /) -> _VT: raise AssumedToBeImplementedException
    @overload
    def pop(self, key: _KT, default: _VT, /) -> _VT: raise AssumedToBeImplementedException
    @overload
    def pop(self, key: _KT, default: _T, /) -> _VT | _T: raise AssumedToBeImplementedException
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
    # Keep the following methods in line with MutableMapping.setdefault, modulo positional-only differences:
    # -- collections.OrderedDict.setdefault
    # -- collections.ChainMap.setdefault
    # -- weakref.WeakKeyDictionary.setdefault
    # @overload
    # def setdefault(self: MutableMapping[_KT, _T | None], key: _KT, default: None = None, /) -> _T | None: ...
    # @overload
    def setdefault(self, key: _KT, default: _VT, /) -> _VT:
        """
        D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D
        """
        raise AssumedToBeImplementedException
    # def setdefault(self: IsMutableMapping[_KT, _VT] | IsMutableMapping[_KT, _T | None], key: _KT, default: _VT | None = None, /) -> _VT | _T | None: raise AssumedToBeImplementedException

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
    # Various mapping classes have __ior__ methods that should be kept roughly in line with .update():
    # -- dict.__ior__
    # -- os._Environ.__ior__
    # -- collections.UserDict.__ior__
    # -- collections.ChainMap.__ior__
    # -- peewee.attrdict.__add__
    # -- peewee.attrdict.__iadd__
    # -- weakref.WeakValueDictionary.__ior__
    # -- weakref.WeakKeyDictionary.__ior__
    @overload
    def update(self, m: SupportsKeysAndGetItem[_KT, _VT], /) -> None: raise AssumedToBeImplementedException
    @overload
    def update(self: SupportsGetItem[str, _VT], m: SupportsKeysAndGetItem[str, _VT], /, **kwargs: _VT) -> None:  raise AssumedToBeImplementedException
    @overload
    def update(self, m: Iterable[tuple[_KT, _VT]], /) -> None: raise AssumedToBeImplementedException
    @overload
    def update(self: SupportsGetItem[str, _VT], m: Iterable[tuple[str, _VT]], /, **kwargs: _VT) -> None: raise AssumedToBeImplementedException
    @overload
    def update(self: SupportsGetItem[str, _VT], /, **kwargs: _VT) -> None: raise AssumedToBeImplementedException
    def update(
        self,
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

# Text = str
#
# TYPE_CHECKING: Final[bool]

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
    def mode(self) -> str: raise AssumedToBeImplementedException
    # Usually str, but may be bytes if a bytes path was passed to open(). See #10737.
    # If PEP 696 becomes available, we may want to use a defaulted TypeVar here.
    @property
    def name(self) -> str | Any: raise AssumedToBeImplementedException
    # @abstractmethod
    def close(self) -> None: raise AssumedToBeImplementedException
    @property
    def closed(self) -> bool: raise AssumedToBeImplementedException
    # @abstractmethod
    def fileno(self) -> int: raise AssumedToBeImplementedException
    # @abstractmethod
    def flush(self) -> None: raise AssumedToBeImplementedException
    # @abstractmethod
    def isatty(self) -> bool: raise AssumedToBeImplementedException
    # @abstractmethod
    def read(self, n: int = -1, /) -> AnyStr: raise AssumedToBeImplementedException
    # @abstractmethod
    def readable(self) -> bool: raise AssumedToBeImplementedException
    # @abstractmethod
    def readline(self, limit: int = -1, /) -> AnyStr: raise AssumedToBeImplementedException
    # @abstractmethod
    def readlines(self, hint: int = -1, /) -> list[AnyStr]: raise AssumedToBeImplementedException
    # @abstractmethod
    def seek(self, offset: int, whence: int = 0, /) -> int: raise AssumedToBeImplementedException
    # @abstractmethod
    def seekable(self) -> bool: raise AssumedToBeImplementedException
    # @abstractmethod
    def tell(self) -> int: raise AssumedToBeImplementedException
    # @abstractmethod
    def truncate(self, size: int | None = None, /) -> int: raise AssumedToBeImplementedException
    # @abstractmethod
    def writable(self) -> bool: raise AssumedToBeImplementedException

    # @abstractmethod
    @overload
    # def write(self: IO[bytes], s: ReadableBuffer, /) -> int: ...
    def write(self: IsIO[bytes], s: ReadableBuffer, /) -> int: raise AssumedToBeImplementedException
    # @abstractmethod
    @overload
    def write(self, s: AnyStr, /) -> int: raise AssumedToBeImplementedException
    def write(self, s: AnyStr | ReadableBuffer, /) -> int: raise AssumedToBeImplementedException

    # @abstractmethod
    @overload
    # def writelines(self: IO[bytes], lines: Iterable[ReadableBuffer], /) -> None: ...
    def writelines(self: IsIO[bytes], lines: Iterable[ReadableBuffer], /) -> None: raise AssumedToBeImplementedException
    # @abstractmethod
    @overload
    def writelines(self, lines: Iterable[AnyStr], /) -> None: raise AssumedToBeImplementedException
    def writelines(
        self,
        lines: Iterable[AnyStr] | Iterable[ReadableBuffer],
        /,
    ) -> None: raise AssumedToBeImplementedException

    # @abstractmethod
    def __next__(self) -> AnyStr: raise AssumedToBeImplementedException
    # @abstractmethod
    def __iter__(self) -> Iterator[AnyStr]: raise AssumedToBeImplementedException
    # @abstractmethod
    # def __enter__(self) -> IO[AnyStr]: ...
    def __enter__(self) -> IsIO[AnyStr]: raise AssumedToBeImplementedException
    # @abstractmethod
    def __exit__(
        self, type: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None, /
    ) -> None: raise AssumedToBeImplementedException

# class BinaryIO(IO[bytes]):
class IsBinaryIO(IsIO[bytes], Protocol):
    """Protocol with the same interface as the abstract class `typing.BinaryIO`.
    """
    # __slots__ = ()
    # @abstractmethod
    # def __enter__(self) -> BinaryIO: ...
    def __enter__(self) -> IsBinaryIO: raise AssumedToBeImplementedException

# class TextIO(IO[str]):
class IsTextIO(IsIO[str], Protocol):
    """Protocol with the same interface as the abstract class `typing.TextIO`."""

    # See comment regarding the @properties in the `IO` class
    # __slots__ = ()
    @property
    # def buffer(self) -> BinaryIO: ...
    def buffer(self) -> IsBinaryIO: raise AssumedToBeImplementedException
    @property
    def encoding(self) -> str: raise AssumedToBeImplementedException
    @property
    def errors(self) -> str | None: raise AssumedToBeImplementedException
    @property
    def line_buffering(self) -> int: raise AssumedToBeImplementedException  # int on PyPy, bool on CPython
    @property
    def newlines(self) -> Any: raise AssumedToBeImplementedException  # None, str or tuple
    # @abstractmethod
    # def __enter__(self) -> TextIO: ...
    def __enter__(self) -> IsTextIO: raise AssumedToBeImplementedException

# ByteString: typing_extensions.TypeAlias = bytes | bytearray | memoryview
#
# # Functions
#
# _get_type_hints_obj_allowed_types: typing_extensions.TypeAlias = (  # noqa: Y042
#     object
#     | Callable[..., Any]
#     | FunctionType
#     | BuiltinFunctionType
#     | MethodType
#     | ModuleType
#     | WrapperDescriptorType
#     | MethodWrapperType
#     | MethodDescriptorType
# )
#
# if sys.version_info >= (3, 14):
#     def get_type_hints(
#         obj: _get_type_hints_obj_allowed_types,
#         globalns: dict[str, Any] | None = None,
#         localns: Mapping[str, Any] | None = None,
#         include_extras: bool = False,
#         *,
#         format: Format | None = None,  # Default: Format.VALUE
#     ) -> dict[str, Any]: ...  # AnnotationForm
#
# else:
#     def get_type_hints(
#         obj: _get_type_hints_obj_allowed_types,
#         globalns: dict[str, Any] | None = None,
#         localns: Mapping[str, Any] | None = None,
#         include_extras: bool = False,
#     ) -> dict[str, Any]: ...  # AnnotationForm
#
# def get_args(tp: Any) -> tuple[Any, ...]: ...  # AnnotationForm
#
# @overload
# def get_origin(tp: ParamSpecArgs | ParamSpecKwargs) -> ParamSpec: ...
# @overload
# def get_origin(tp: UnionType) -> type[UnionType]: ...
# @overload
# def get_origin(tp: GenericAlias) -> type: ...
# @overload
# def get_origin(tp: Any) -> Any | None: ...  # AnnotationForm
#
# @overload
# def cast(typ: type[_T], val: Any) -> _T: ...
# @overload
# def cast(typ: str, val: Any) -> Any: ...
# @overload
# def cast(typ: object, val: Any) -> Any: ...
#
# if sys.version_info >= (3, 11):
#     def reveal_type(obj: _T, /) -> _T: ...
#     def assert_never(arg: Never, /) -> Never: ...
#     def assert_type(val: _T, typ: Any, /) -> _T: ...  # AnnotationForm
#     def clear_overloads() -> None: ...
#     def get_overloads(func: Callable[..., object]) -> Sequence[Callable[..., object]]: ...
#     def dataclass_transform(
#         *,
#         eq_default: bool = True,
#         order_default: bool = False,
#         kw_only_default: bool = False,
#         frozen_default: bool = False,  # on 3.11, runtime accepts it as part of kwargs
#         field_specifiers: tuple[type[Any] | Callable[..., Any], ...] = (),
#         **kwargs: Any,
#     ) -> IdentityFunction: ...
#
# # Type constructors
#
# # Obsolete, will be changed to a function. Use _typeshed._type_checker_internals.NamedTupleFallback instead.
# class NamedTuple(tuple[Any, ...]):
#     _field_defaults: ClassVar[dict[str, Any]]
#     _fields: ClassVar[tuple[str, ...]]
#     # __orig_bases__ sometimes exists on <3.12, but not consistently
#     # So we only add it to the stub on 3.12+.
#     if sys.version_info >= (3, 12):
#         __orig_bases__: ClassVar[tuple[Any, ...]]
#
#     @overload
#     def __init__(self, typename: str, fields: Iterable[tuple[str, Any]], /) -> None: ...
#     @overload
#     @deprecated("Creating a typing.NamedTuple using keyword arguments is deprecated and support will be removed in Python 3.15")
#     def __init__(self, typename: str, fields: None = None, /, **kwargs: Any) -> None: ...
#
#     @classmethod
#     def _make(cls, iterable: Iterable[Any]) -> typing_extensions.Self: ...
#     def _asdict(self) -> dict[str, Any]: ...
#     def _replace(self, **kwargs: Any) -> typing_extensions.Self: ...
#     if sys.version_info >= (3, 13):
#         def __replace__(self, **kwargs: Any) -> typing_extensions.Self: ...
#
# # Internal mypy fallback type for all typed dicts (does not exist at runtime)
# # N.B. Keep this mostly in sync with typing_extensions._TypedDict/mypy_extensions._TypedDict
# # Obsolete, use _typeshed._type_checker_internals.TypedDictFallback instead.
# @type_check_only
# class _TypedDict(Mapping[str, object], metaclass=ABCMeta):
#     __total__: ClassVar[bool]
#     __required_keys__: ClassVar[frozenset[str]]
#     __optional_keys__: ClassVar[frozenset[str]]
#     # __orig_bases__ sometimes exists on <3.12, but not consistently,
#     # so we only add it to the stub on 3.12+
#     if sys.version_info >= (3, 12):
#         __orig_bases__: ClassVar[tuple[Any, ...]]
#     if sys.version_info >= (3, 13):
#         __readonly_keys__: ClassVar[frozenset[str]]
#         __mutable_keys__: ClassVar[frozenset[str]]
#
#     def copy(self) -> typing_extensions.Self: ...
#     # Using Never so that only calls using mypy plugin hook that specialize the signature
#     # can go through.
#     def setdefault(self, k: _Never, default: object) -> object: ...
#     # Mypy plugin hook for 'pop' expects that 'default' has a type variable type.
#     def pop(self, k: _Never, default: _T = ...) -> object: ...  # pyright: ignore[reportInvalidTypeVarUse]
#     def update(self, m: typing_extensions.Self, /) -> None: ...
#     def __delitem__(self, k: _Never) -> None: ...
#     def items(self) -> dict_items[str, object]: ...
#     def keys(self) -> dict_keys[str, object]: ...
#     def values(self) -> dict_values[str, object]: ...
#
#     @overload
#     def __or__(self, value: typing_extensions.Self, /) -> typing_extensions.Self: ...
#     @overload
#     def __or__(self, value: dict[str, Any], /) -> dict[str, object]: ...
#
#     @overload
#     def __ror__(self, value: typing_extensions.Self, /) -> typing_extensions.Self: ...
#     @overload
#     def __ror__(self, value: dict[str, Any], /) -> dict[str, object]: ...
#
#     # supposedly incompatible definitions of __or__ and __ior__
#     def __ior__(self, value: typing_extensions.Self, /) -> typing_extensions.Self: ...  # type: ignore[misc]
#
# if sys.version_info >= (3, 14):
#     from annotationlib import ForwardRef as ForwardRef
#
#     def evaluate_forward_ref(
#         forward_ref: ForwardRef,
#         *,
#         owner: object = None,
#         globals: dict[str, Any] | None = None,
#         locals: Mapping[str, Any] | None = None,
#         type_params: tuple[TypeVar, ParamSpec, TypeVarTuple] | None = None,
#         format: Format | None = None,
#     ) -> Any: ...  # AnnotationForm
#
# else:
#     @final
#     class ForwardRef(_Final):
#         __slots__ = (
#             "__forward_arg__",
#             "__forward_code__",
#             "__forward_evaluated__",
#             "__forward_value__",
#             "__forward_is_argument__",
#             "__forward_is_class__",
#             "__forward_module__",
#         )
#         __forward_arg__: str
#         __forward_code__: CodeType
#         __forward_evaluated__: bool
#         __forward_value__: Any | None  # AnnotationForm
#         __forward_is_argument__: bool
#         __forward_is_class__: bool
#         __forward_module__: Any | None
#
#         def __init__(self, arg: str, is_argument: bool = True, module: Any | None = None, *, is_class: bool = False) -> None: ...
#
#         if sys.version_info >= (3, 13):
#             @overload
#             @deprecated(
#                 "Failing to pass a value to the 'type_params' parameter of ForwardRef._evaluate() is deprecated, "
#                 "as it leads to incorrect behaviour when evaluating a stringified annotation "
#                 "that references a PEP 695 type parameter. It will be disallowed in Python 3.15."
#             )
#             def _evaluate(
#                 self, globalns: dict[str, Any] | None, localns: Mapping[str, Any] | None, *, recursive_guard: frozenset[str]
#             ) -> Any | None: ...  # AnnotationForm
#             @overload
#             def _evaluate(
#                 self,
#                 globalns: dict[str, Any] | None,
#                 localns: Mapping[str, Any] | None,
#                 type_params: tuple[TypeVar | ParamSpec | TypeVarTuple, ...],
#                 *,
#                 recursive_guard: frozenset[str],
#             ) -> Any | None: ...  # AnnotationForm
#         elif sys.version_info >= (3, 12):
#             def _evaluate(
#                 self,
#                 globalns: dict[str, Any] | None,
#                 localns: Mapping[str, Any] | None,
#                 type_params: tuple[TypeVar | ParamSpec | TypeVarTuple, ...] | None = None,
#                 *,
#                 recursive_guard: frozenset[str],
#             ) -> Any | None: ...  # AnnotationForm
#         else:
#             def _evaluate(
#                 self, globalns: dict[str, Any] | None, localns: Mapping[str, Any] | None, recursive_guard: frozenset[str]
#             ) -> Any | None: ...  # AnnotationForm
#
#         def __eq__(self, other: object) -> bool: ...
#         def __hash__(self) -> int: ...
#         if sys.version_info >= (3, 11):
#             def __or__(self, other: Any) -> _SpecialForm: ...
#             def __ror__(self, other: Any) -> _SpecialForm: ...
#
# def is_typeddict(tp: object) -> bool: ...
# def _type_repr(obj: object) -> str: ...
#
# if sys.version_info >= (3, 12):
#     _TypeParameter: typing_extensions.TypeAlias = (
#         TypeVar
#         | typing_extensions.TypeVar
#         | ParamSpec
#         | typing_extensions.ParamSpec
#         | TypeVarTuple
#         | typing_extensions.TypeVarTuple
#     )
#
#     def override(method: _F, /) -> _F: ...
#
#     @final
#     class TypeAliasType:
#         def __new__(cls, name: str, value: Any, *, type_params: tuple[_TypeParameter, ...] = ()) -> Self: ...
#         @property
#         def __value__(self) -> Any: ...  # AnnotationForm
#         @property
#         def __type_params__(self) -> tuple[_TypeParameter, ...]: ...
#         @property
#         def __parameters__(self) -> tuple[Any, ...]: ...  # AnnotationForm
#         @property
#         def __name__(self) -> str: ...
#         if sys.version_info >= (3, 15):
#             @property
#             def __qualname__(self) -> str: ...
#         # It's writable on types, but not on instances of TypeAliasType.
#         @property
#         def __module__(self) -> str | None: ...  # type: ignore[override]
#         def __getitem__(self, parameters: Any, /) -> GenericAlias: ...  # AnnotationForm
#         def __or__(self, right: Any, /) -> _SpecialForm: ...
#         def __ror__(self, left: Any, /) -> _SpecialForm: ...
#         if sys.version_info >= (3, 14):
#             def __iter__(self) -> Any: ...  # Unpack[Self]
#             @property
#             def evaluate_value(self) -> EvaluateFunc: ...
#
# if sys.version_info >= (3, 13):
#     def is_protocol(tp: type, /) -> bool: ...
#     def get_protocol_members(tp: type, /) -> frozenset[str]: ...
#
#     @final
#     @type_check_only
#     class _NoDefaultType: ...
#
#     NoDefault: _NoDefaultType
#     TypeIs: _SpecialForm
#     ReadOnly: _SpecialForm
