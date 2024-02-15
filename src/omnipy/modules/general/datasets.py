from typing import Generic, TypeVar

from omnipy.data.dataset import Dataset

_KeyT = TypeVar('_KeyT')
from .models import NestedFrozenDictsModel, NestedFrozenDictsOrTuplesModel, NestedFrozenTuplesModel
_ScT = TypeVar('_ScT')


class NestedFrozenTuplesDataset(Dataset[NestedFrozenTuplesModel[_ScT]], Generic[_ScT]):
    ...


class NestedFrozenDictsDataset(Dataset[NestedFrozenDictsModel[_KeyT, _ScT]], Generic[_KeyT, _ScT]):
    ...


class NestedFrozenDictsOrTuplesDataset(Dataset[NestedFrozenDictsOrTuplesModel[_KeyT, _ScT]],
                                       Generic[_KeyT, _ScT]):
    ...
