from typing import Generic

from omnipy.components._frozen.models import (NestedFrozenDictsOrTuplesModel,
                                              NestedFrozenOnlyDictsModel,
                                              NestedFrozenOnlyTuplesModel)
from omnipy.components._frozen.typedefs import _KeyT, _ValT
from omnipy.data.dataset import Dataset


class NestedFrozenDictsOrTuplesDataset(Dataset[NestedFrozenDictsOrTuplesModel[_KeyT, _ValT]],
                                       Generic[_KeyT, _ValT]):
    ...


class NestedFrozenTuplesDataset(Dataset[NestedFrozenOnlyTuplesModel[_ValT]], Generic[_ValT]):
    ...


class NestedFrozenDictsDataset(Dataset[NestedFrozenOnlyDictsModel[_KeyT, _ValT]],
                               Generic[_KeyT, _ValT]):
    ...
