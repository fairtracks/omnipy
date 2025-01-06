from typing import Generic

from omnipy.components.frozen.models import (NestedFrozenDictsOrTuplesModel,
                                             NestedFrozenOnlyDictsModel,
                                             NestedFrozenOnlyTuplesModel)
from omnipy.components.frozen.typedefs import KeyT, ValT
from omnipy.data.dataset import Dataset


class NestedFrozenDictsOrTuplesDataset(Dataset[NestedFrozenDictsOrTuplesModel[KeyT, ValT]],
                                       Generic[KeyT, ValT]):
    ...


class NestedFrozenTuplesDataset(Dataset[NestedFrozenOnlyTuplesModel[ValT]], Generic[ValT]):
    ...


class NestedFrozenDictsDataset(Dataset[NestedFrozenOnlyDictsModel[KeyT, ValT]], Generic[KeyT,
                                                                                        ValT]):
    ...
