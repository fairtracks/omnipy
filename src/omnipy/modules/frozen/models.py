from typing import Generic, Hashable, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.model import Model

from ...data.helpers import TypeVarStore
from ..general.models import NotIterableExceptStrOrBytesModel
from .typedefs import FrozenDict, KeyT, ValT

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

_FrozenBaseT = TypeVar('_FrozenBaseT', default='_FrozenAnyUnion')

# class _FrozenScalarM(NotIterableExceptStrOrBytesModel):
#     ...


class _FrozenScalarM(Model[ValT], Generic[ValT]):
    _parse_data = NotIterableExceptStrOrBytesModel._parse_data


class _FrozenTupleBaseM(Model[tuple[_FrozenBaseT, ...]], Generic[_FrozenBaseT]):
    ...


class _FrozenDictBaseM(Model[FrozenDict[KeyT, _FrozenBaseT]], Generic[KeyT, _FrozenBaseT]):
    ...


class _FrozenTupleM(_FrozenTupleBaseM['_FrozenAnyUnion'], Generic[ValT]):
    ...


#
# class _FrozenDictM(_FrozenDictBaseM[KeyT, '_FrozenAnyUnion'], Generic[KeyT, ValT]):
#     ...


class _FrozenDictM(_FrozenDictBaseM[str | Hashable, '_FrozenAnyUnion'], Generic[KeyT, ValT]):
    ...


class _FrozenNoDictsM(_FrozenTupleBaseM['_FrozenNoDictsUnion'], Generic[ValT]):
    ...


# class _FrozenNoTuplesM(_FrozenDictBaseM['KeyT', '_FrozenNoTuplesUnion'], Generic[KeyT, ValT]):
#     ...


class _FrozenNoTuplesM(_FrozenDictBaseM[str | Hashable, '_FrozenNoTuplesUnion'],
                       Generic[KeyT, ValT]):
    ...


# TypeAliases

_FrozenAnyUnion: TypeAlias = \
    TypeVarStore[KeyT] | _FrozenScalarM[ValT]| _FrozenTupleM[ValT] | _FrozenDictM[KeyT, ValT]
_FrozenNoDictsUnion: TypeAlias = _FrozenNoDictsM[ValT] | _FrozenScalarM[ValT]
_FrozenNoTuplesUnion: TypeAlias = _FrozenNoTuplesM[KeyT, ValT] | _FrozenScalarM[ValT]

# Basic models needs to update their forward_refs with type aliases declared above

_FrozenTupleM.update_forward_refs()
_FrozenDictM.update_forward_refs()
_FrozenNoDictsM.update_forward_refs()
_FrozenNoTuplesM.update_forward_refs()

#
# Exportable models
#


class NestedFrozenDictsOrTuplesModel(Model[_FrozenAnyUnion], Generic[KeyT, ValT]):
    """
    Recursive model for nested immutable containers (FrozenDict and tuples). Not functional.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """


class NestedFrozenTuplesModel(Model[_FrozenNoDictsM[ValT]], Generic[ValT]):
    """
    Recursive model for nested tuples.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """


class NestedFrozenDictsModel(Model[_FrozenNoTuplesM[KeyT, ValT]], Generic[KeyT, ValT]):
    """
    Recursive model for nested FrozenDicts.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """
