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
    """Represent recursively nested datasets with configurable leaf value type.

    Values may be nested datasets or scalar-like leaf models, depending on the
    active generic parameter.
    """

    ...


TableModels: TypeAlias = JsonScalarColumnWiseTableWithColNamesModel | RowWiseTableWithColNamesModel
ColumnAndTableModels: TypeAlias = JsonScalarColumnModel | TableModels
NestedUnion: TypeAlias = (
    'ColumnAndTableModels | NestedDataset | JsonScalarModel | ListAsNestedDatasetModel')


class NestedDataset(GenericNestedDataset[NestedUnion]):
    """Store heterogeneously nested values across dataset, table, list, and scalar forms.

    This concrete nested dataset accepts recursive nested datasets, table models,
    list-as-dataset models, and JSON scalar models as values.
    """
    ...


NestedDataset.update_forward_refs()
ListAsNestedDatasetModel.update_forward_refs()
