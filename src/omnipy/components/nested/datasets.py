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
    ...


TableModels: TypeAlias = JsonScalarColumnWiseTableWithColNamesModel | RowWiseTableWithColNamesModel
ColumnAndTableModels: TypeAlias = JsonScalarColumnModel | TableModels
NestedUnion: TypeAlias = (
    'ColumnAndTableModels | NestedDataset | JsonScalarModel | ListAsNestedDatasetModel')


class NestedDataset(GenericNestedDataset[NestedUnion]):
    ...


NestedDataset.update_forward_refs()
ListAsNestedDatasetModel.update_forward_refs()
