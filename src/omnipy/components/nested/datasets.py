from typing import Generic

from typing_extensions import TypeAlias, TypeVar

from omnipy.data.dataset import Dataset

from ..json.models import JsonScalarModel
from .models import ListAsNestedDatasetModel

NestedAnyUnionT = TypeVar(
    'NestedAnyUnionT', bound='NestedDataset | JsonScalarModel', default=JsonScalarModel)


class GenericNestedDataset(Dataset[NestedAnyUnionT], Generic[NestedAnyUnionT]):
    ...


NestedAnyUnion: TypeAlias = 'NestedDataset | ListAsNestedDatasetModel | JsonScalarModel'


class NestedDataset(GenericNestedDataset[NestedAnyUnion]):
    ...


NestedDataset.update_forward_refs(**{'NestedDataset': NestedDataset})
ListAsNestedDatasetModel.update_forward_refs()
