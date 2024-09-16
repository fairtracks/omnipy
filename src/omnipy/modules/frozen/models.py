from types import MappingProxyType
from typing import Generic, TypeAlias

from typing_extensions import ForwardRef

from omnipy.data.helpers import DoubleTypeVarStore, TypeVarStore
from omnipy.data.model import Model
from omnipy.modules.frozen.typedefs import FrozenDict, KeyT, ValT
from omnipy.modules.general.models import NotIterableExceptStrOrBytesModel

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


class _FrozenScalarM(Model[ValT], Generic[ValT]):
    _parse_data = NotIterableExceptStrOrBytesModel._parse_data


class _FrozenScalarWithTwoParamsM(Model[ValT], Generic[KeyT, ValT]):
    ...


# class _FrozenTupleBaseM(Model[tuple[_FrozenBaseT, ...]], Generic[_FrozenBaseT]):
#     ...

# class _FrozenDictBaseM(Model[FrozenDict[KeyT, _FrozenBaseT]], Generic[KeyT, _FrozenBaseT]):
#     ...


class _FrozenTupleM(Model[tuple[DoubleTypeVarStore[KeyT, ValT]
                                | ForwardRef('_FrozenAnyUnion[KeyT, ValT]'),
                                ...]],
                    Generic[KeyT, ValT]):
    ...


#
# class _FrozenDictM(_FrozenDictBaseM[KeyT, '_FrozenAnyUnion'], Generic[KeyT, ValT]):
#     ...


class _FrozenDictM(Model[FrozenDict[KeyT, TypeVarStore[ValT]
                                    | ForwardRef('_FrozenAnyUnion')]],
                   Generic[KeyT, ValT]):
    def to_data(self) -> dict[KeyT, ValT]:
        to_data = super().to_data()
        return MappingProxyType({key: val.to_data() for key, val in to_data.items()})


class _FrozenNoDictsM(Model[tuple[TypeVarStore[ValT]
                                  | ForwardRef('_FrozenNoDictsUnion[ValT]'), ...]],
                      Generic[ValT]):
    ...


# class _FrozenNoTuplesM(_FrozenDictBaseM['KeyT', '_FrozenNoTuplesUnion'], Generic[KeyT, ValT]):
#     ...


class _FrozenNoTuplesM(Model[FrozenDict[KeyT,
                                        DoubleTypeVarStore[KeyT, ValT]
                                        | ForwardRef('_FrozenNoTuplesUnion')]],
                       Generic[KeyT, ValT]):
    def to_data(self) -> dict[KeyT, ValT]:
        to_data = super().to_data()
        return MappingProxyType({key: val.to_data() for key, val in to_data.items()})


# TypeAliases

_FrozenAnyUnion: TypeAlias = \
    DoubleTypeVarStore[KeyT, ValT] | _FrozenScalarM[ValT] \
    | _FrozenTupleM[KeyT, ValT] | _FrozenDictM[KeyT, ValT]
_FrozenTupleM.update_forward_refs()
_FrozenDictM.update_forward_refs()
_FrozenNoDictsUnion: TypeAlias = TypeVarStore[ValT] | _FrozenScalarM[ValT] | _FrozenNoDictsM[ValT]
_FrozenNoTuplesUnion: TypeAlias = DoubleTypeVarStore[
    KeyT, ValT] | _FrozenScalarM[ValT] | _FrozenNoTuplesM[KeyT, ValT]


class _FrozenAnyUnionM(Model[_FrozenAnyUnion[KeyT, ValT]], Generic[KeyT, ValT]):
    ...


# Basic models needs to update their forward_refs with type aliases declared above

_FrozenTupleM.update_forward_refs()
_FrozenDictM.update_forward_refs()
_FrozenAnyUnionM.update_forward_refs()
_FrozenNoDictsM.update_forward_refs()
_FrozenNoTuplesM.update_forward_refs()

#
# Exportable models
#


class NestedFrozenDictsOrTuplesModel(Model[_FrozenAnyUnionM[KeyT, ValT]], Generic[KeyT, ValT]):
    """
    Recursive model for nested immutable containers (FrozenDict and tuples). Not functional.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """


class NestedFrozenOnlyTuplesModel(Model[_FrozenNoDictsM[ValT]], Generic[ValT]):
    """
    Recursive model for nested tuples.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """


class NestedFrozenOnlyDictsModel(Model[_FrozenNoTuplesM[KeyT, ValT]], Generic[KeyT, ValT]):
    """
    Recursive model for nested FrozenDicts.

    Awaiting support for MappingProxyType in pydantic for the immutability to actually work.
    Also use as generic types awaits Python 3.13. Way ahead of the crowd here!
    """
