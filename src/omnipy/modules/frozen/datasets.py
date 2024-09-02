from typing import Generic

from omnipy.data.dataset import Dataset
from omnipy.modules.frozen.models import (NestedFrozenDictsModel,
                                          NestedFrozenDictsOrTuplesModel,
                                          NestedFrozenTuplesModel)
from omnipy.modules.frozen.typedefs import KeyT, ValT


class NestedFrozenDictsOrTuplesDataset(Dataset[NestedFrozenDictsOrTuplesModel[KeyT, ValT]],
                                       Generic[KeyT, ValT]):
    ...


class NestedFrozenTuplesDataset(Dataset[NestedFrozenTuplesModel[ValT]], Generic[ValT]):
    ...


class NestedFrozenDictsDataset(Dataset[NestedFrozenDictsModel[KeyT, ValT]], Generic[KeyT, ValT]):
    ...
