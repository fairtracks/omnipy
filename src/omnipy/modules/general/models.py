from typing import Generic, Hashable, TypeAlias, TypeVar

from omnipy.data.model import Model
from omnipy.modules.general.typedefs import FrozenDict
from omnipy.util.helpers import is_iterable


class NotIterableExceptStrOrBytesModel(Model[object | None]):
    """
    Model describing any object that is not iterable, except for `str` and `bytes` types.
    As strings and bytes are iterable (over the characters/bytes) but also generally useful and
    often considered singular (or scalar) types, they are specifically allowed by this model.

    Examples:
        >>> from omnipy import NotIterableExceptStrOrBytesModel, print_exception
        >>>
        >>> NotIterableExceptStrOrBytesModel(1234)
        NotIterableExceptStrOrBytesModel(1234)
        >>> NotIterableExceptStrOrBytesModel('1234')
        NotIterableExceptStrOrBytesModel(1234)
        >>> with print_exception:
        ...     NotIterableExceptStrOrBytesModel((1, 2, 3, 4))
        ValidationError: 1 validation error for NotIterableExceptStrOrBytesModel

    Note:
        JsonScalarModel is a strict submodel of NotIterableExceptStrOrBytesModel in that all objects
        allowed by JsonScalarModel are also allowed by NotIterableExceptStrOrBytesModel.
    """
    @classmethod
    def _parse_data(cls, data: object) -> object:
        assert isinstance(data, str) or isinstance(data, bytes) or not is_iterable(data), \
            f'Data of type {type(data)} is iterable'
        return data


# TODO: Follow pydantic topic https://github.com/pydantic/pydantic/issues/6868 on MappingProxyType.
#       Used way too much energy to implement (and test) recursive frozen models, only to discover
#       that pydantic actually does not support MappingProxyType, which was hugely surprising.
#       Add tests on the immutability part once there is support for this.

# Note: see comments in omnipy.modules.json.models for more information on the basic organisation of
#       nested models.

#
# Private models
#

# Basic building block models

_KeyT = TypeVar('_KeyT', bound=str | Hashable)
_ValT = TypeVar('_ValT', bound=NotIterableExceptStrOrBytesModel | object)

_FrozenBaseT = TypeVar('_FrozenBaseT')

# class _FrozenScalarM(NotIterableExceptStrOrBytesModel):
#     ...


class _FrozenScalarM(Model[_ValT], Generic[_ValT]):
    _parse_data = NotIterableExceptStrOrBytesModel._parse_data


class _FrozenTupleBaseM(Model[tuple[_FrozenBaseT, ...]], Generic[_FrozenBaseT]):
    ...


class _FrozenDictBaseM(Model[FrozenDict[_KeyT, _FrozenBaseT]], Generic[_KeyT, _FrozenBaseT]):
    ...


class _FrozenTupleM(_FrozenTupleBaseM['_FrozenAnyUnion'], Generic[_ValT]):
    ...


#
# class _FrozenDictM(_FrozenDictBaseM[_KeyT, '_FrozenAnyUnion'], Generic[_KeyT, _ValT]):
#     ...


class _FrozenDictM(_FrozenDictBaseM[str | Hashable, '_FrozenAnyUnion'], Generic[_KeyT, _ValT]):
    ...


class _FrozenNoDictsM(_FrozenTupleBaseM['_FrozenNoDictsUnion'], Generic[_ValT]):
    ...


# class _FrozenNoTuplesM(_FrozenDictBaseM['_KeyT', '_FrozenNoTuplesUnion'], Generic[_KeyT, _ValT]):
#     ...


class _FrozenNoTuplesM(_FrozenDictBaseM[str | Hashable, '_FrozenNoTuplesUnion'],
                       Generic[_KeyT, _ValT]):
    ...


# TypeAliases

_FrozenAnyUnion: TypeAlias = \
    _FrozenScalarM[_ValT] | _FrozenTupleM[_ValT] | _FrozenDictM[_KeyT, _ValT]
_FrozenNoDictsUnion: TypeAlias = _FrozenScalarM[_ValT] | _FrozenNoDictsM[_ValT]
_FrozenNoTuplesUnion: TypeAlias = _FrozenScalarM[_ValT] | _FrozenNoTuplesM[_KeyT, _ValT]

# Basic models needs to update their forward_refs with type aliases declared above

_FrozenTupleM.update_forward_refs()
_FrozenDictM.update_forward_refs()
_FrozenNoDictsM.update_forward_refs()
_FrozenNoTuplesM.update_forward_refs()

#
# Exportable models
#

# General


class NestedFrozenDictsOrTuplesModel(Model[_FrozenAnyUnion], Generic[_KeyT, _ValT]):
    """
    Recursive model for nested immutable containers (FrozenDict and tuples). Not functional.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """


class NestedFrozenTuplesModel(Model[_FrozenNoDictsM[_ValT]], Generic[_ValT]):
    """
    Recursive model for nested tuples.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """


class NestedFrozenDictsModel(Model[_FrozenNoTuplesM[_KeyT, _ValT]], Generic[_KeyT, _ValT]):
    """
    Recursive model for nested FrozenDicts.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """
