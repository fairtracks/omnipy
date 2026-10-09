"""Datasets for recursively nested data structures that can contain tables or scalar values."""

from typing import ClassVar, Generic

from typing_extensions import TypeAlias, TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..json.models import JsonScalarModel
from ..tables.models import (JsonScalarColumnModel,
                             JsonScalarColumnWiseTableWithColNamesModel,
                             RowWiseTableWithColNamesModel)
from .models import ListAsNestedDatasetModel

NestedAnyUnionT = TypeVar('NestedAnyUnionT', bound='Dataset | Model')


class GenericNestedDataset(Dataset['GenericNestedDataset[NestedAnyUnionT]| NestedAnyUnionT'],
                           Generic[NestedAnyUnionT]):
    """Represent recursively nested datasets with configurable leaf value type.

    Values may be nested datasets or scalar-like leaf models, depending on the
    active generic parameter.
    """

    # Inherited as True from the parametrized Dataset base. Must be False for pydantic to
    # substitute the type variable into the recursive self-reference when specializing.
    __concrete__: ClassVar[bool] = False


GenericNestedDataset.update_forward_refs()

TableModels: TypeAlias = JsonScalarColumnWiseTableWithColNamesModel | RowWiseTableWithColNamesModel
ColumnAndTableModels: TypeAlias = JsonScalarColumnModel | TableModels
NestedUnion: TypeAlias = (
    'ColumnAndTableModels | NestedDataset | JsonScalarModel | ListAsNestedDatasetModel')


class NestedDataset(Dataset[NestedUnion]):
    """Store heterogeneously nested values across dataset, table, list, and scalar forms.

    This concrete nested dataset accepts recursive nested datasets, table models,
    list-as-dataset models, and JSON scalar models as values.
    """
    ...


NestedDataset.update_forward_refs()
ListAsNestedDatasetModel.update_forward_refs()
