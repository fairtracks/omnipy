from typing import Hashable

from typing_extensions import TypeVar, TypeVarTuple

_KeyT = TypeVar('_KeyT', bound=Hashable)
_ValT = TypeVar('_ValT')

_ValTupleT = TypeVarTuple('_ValTupleT')
