"""Datasets for recursively nested data structures that can contain tables or scalar values."""

from typing import ClassVar, Generic, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from ..json.models import JsonScalarModel
from ..tables.models import (
    JsonScalarColumnModel,
    JsonScalarColumnWiseTableWithColNamesModel,
    RowWiseTableWithColNamesModel,
)
from .models import ListAsStructuredNestedDatasetModel

NestedAnyUnionT = TypeVar('NestedAnyUnionT', bound='Dataset | Model')


class NestedDataset(
    Dataset['NestedDataset[NestedAnyUnionT]| NestedAnyUnionT'], Generic[NestedAnyUnionT]
):
    """A recursive Dataset with a caller-defined leaf Model or Dataset type.

    Each named data item is either another ``NestedDataset[T]`` or an instance
    of ``T``. This preserves a uniform leaf type throughout a hierarchy.
    """

    # Inherited as True from the parametrized Dataset base. Must be False for pydantic to
    # substitute the type variable into the recursive self-reference when specializing.
    __concrete__: ClassVar[bool] = False


NestedDataset.update_forward_refs()

TableModels: TypeAlias = JsonScalarColumnWiseTableWithColNamesModel | RowWiseTableWithColNamesModel
ColumnAndTableModels: TypeAlias = JsonScalarColumnModel | TableModels
ScalarAndListModels: TypeAlias = JsonScalarModel | ListAsStructuredNestedDatasetModel
NestedUnion: TypeAlias = 'ColumnAndTableModels | StructuredNestedDataset | ScalarAndListModels'


class StructuredNestedDataset(Dataset[NestedUnion]):
    """A Dataset that applies structure to hierarchical data.

    Each named data item is interpreted recursively using the alternatives in
    ``NestedUnion``, in their defined order. From the leaves upwards, values
    are represented as tables or list-derived nested Datasets when their
    structure permits; otherwise, JSON scalar Models provide the leaf values.

    This preserves tables, records, and lists as structured data that can be
    inspected and used for visualisation. Nested mappings become
    ``StructuredNestedDataset`` items, allowing the same interpretation at
    every level of the hierarchy.
    """

    ...


StructuredNestedDataset.update_forward_refs()
ListAsStructuredNestedDatasetModel.update_forward_refs()
