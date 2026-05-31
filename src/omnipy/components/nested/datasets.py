"""Datasets for recursively nested data structures that can contain tables or scalar values."""

from typing import Generic

from typing_extensions import TypeAlias, TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..json.models import JsonScalarModel
from ..tables.models import (JsonScalarColumnModel,
                             JsonScalarColumnWiseTableWithColNamesModel,
                             RowWiseTableWithColNamesModel)
from .models import ListAsNestedDatasetModel

NestedAnyUnionT = TypeVar('NestedAnyUnionT', bound='Dataset | Model', default=JsonScalarModel)


class GenericNestedDataset(Dataset[NestedAnyUnionT], Generic[NestedAnyUnionT]):
    """Represent datasets whose values may recursively contain nested datasets."""

    ...


TableModels: TypeAlias = JsonScalarColumnWiseTableWithColNamesModel | RowWiseTableWithColNamesModel
ColumnAndTableModels: TypeAlias = JsonScalarColumnModel | TableModels
NestedUnion: TypeAlias = (
    'ColumnAndTableModels | NestedDataset | JsonScalarModel | ListAsNestedDatasetModel')


class NestedDataset(GenericNestedDataset[NestedUnion]):
    """Store nested datasets whose values may themselves be datasets, tables, lists, or scalars."""
    ...


NestedDataset.update_forward_refs()
ListAsNestedDatasetModel.update_forward_refs()
