from typing import Generic

from omnipy.data.dataset import Dataset
from omnipy.modules.frozen.models import (NestedFrozenDictsOrTuplesModel,
                                          NestedFrozenOnlyDictsModel,
                                          NestedFrozenOnlyTuplesModel)
from omnipy.modules.frozen.typedefs import KeyT, ValT


class NestedFrozenDictsOrTuplesDataset(Dataset[NestedFrozenDictsOrTuplesModel[KeyT, ValT]],
                                       Generic[KeyT, ValT]):
    ...


class NestedFrozenTuplesDataset(Dataset[NestedFrozenOnlyTuplesModel[ValT]], Generic[ValT]):
    ...


class NestedFrozenDictsDataset(Dataset[NestedFrozenOnlyDictsModel[KeyT, ValT]], Generic[KeyT,
                                                                                        ValT]):
    ...
