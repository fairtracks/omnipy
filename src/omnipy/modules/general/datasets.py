from typing import Generic, Hashable, TypeVar

from omnipy.data.dataset import Dataset

from .models import NestedFrozenDictsModel, NestedFrozenDictsOrTuplesModel, NestedFrozenTuplesModel

_KeyT = TypeVar('_KeyT', bound=Hashable)
_ScT = TypeVar('_ScT')


class NestedFrozenTuplesDataset(Dataset[NestedFrozenTuplesModel[_ScT]], Generic[_ScT]):
    ...


class NestedFrozenDictsDataset(Dataset[NestedFrozenDictsModel[_KeyT, _ScT]], Generic[_KeyT, _ScT]):
    ...


class NestedFrozenDictsOrTuplesDataset(Dataset[NestedFrozenDictsOrTuplesModel[_KeyT, _ScT]],
                                       Generic[_KeyT, _ScT]):
    ...
