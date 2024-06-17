from typing import Generic, Hashable, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.model import Model

from ..general.models import NotIterableExceptStrOrBytesModel
from .typedefs import FrozenDict

# TODO: Follow pydantic topic https://github.com/pydantic/pydantic/issues/6868 on MappingProxyType.
#       Used way too much energy to implement (and test) recursive frozen models, only to discover
#       that pydantic actually does not support MappingProxyType, which was hugely surprising.
#       Add tests on the immutability part once there is support for this.

# Note: see comments in omnipy.modules.json.models for more information on the basic organisation of
#       nested models.

# Note 2: currently crashes mypy (v1.10), probably due to recursive type aliases combined with
#         TypeVars from typing_extensions (with default). Not urgent to fix, as this in any case
#         awaits pydantic 2 and issue 6868 to be resolved. Keep out of __all__ until mypy issue
#         is fixed in order to avoid crashes with pytest-mypy-plugins, e.g. "test_json_types.yml".

#
# Private models
#

# Basic building block models

_KeyT = TypeVar('_KeyT', default=str | Hashable)
_ValT = TypeVar('_ValT', default=NotIterableExceptStrOrBytesModel | object)

_FrozenBaseT = TypeVar('_FrozenBaseT', default='_FrozenAnyUnion')

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
