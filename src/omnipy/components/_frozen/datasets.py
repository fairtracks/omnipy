"""Datasets built from recursive frozen container models."""

from typing import Generic

from omnipy.components._frozen.models import (NestedFrozenDictsOrTuplesModel,
                                              NestedFrozenOnlyDictsModel,
                                              NestedFrozenOnlyTuplesModel)
from omnipy.components._frozen.typedefs import _KeyT, _ValT
from omnipy.data.dataset import Dataset


class NestedFrozenDictsOrTuplesDataset(Dataset[NestedFrozenDictsOrTuplesModel[_KeyT, _ValT]],
                                       Generic[_KeyT, _ValT]):
    """Dataset of recursively nested frozen dictionaries or tuples."""

    ...


class NestedFrozenTuplesDataset(Dataset[NestedFrozenOnlyTuplesModel[_ValT]], Generic[_ValT]):
    """Dataset of recursively nested immutable tuples."""

    ...


class NestedFrozenDictsDataset(Dataset[NestedFrozenOnlyDictsModel[_KeyT, _ValT]],
                               Generic[_KeyT, _ValT]):
    """Dataset of recursively nested frozen dictionaries."""

    ...
