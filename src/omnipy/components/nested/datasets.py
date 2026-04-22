from typing import Any, Generic

from typing_extensions import TypeAlias, TypeVar

from omnipy.data.dataset import Dataset

from ..json.models import JsonScalarModel
from ..tables.models import ColumnWiseTableWithColNamesModel, RowWiseTableWithColNamesModel
from .models import ListAsNestedDatasetModel

# from .models import ListAsNestedDatasetModel, MixedJsonDictModel

NestedAnyUnionT = TypeVar(
    'NestedAnyUnionT', bound='NestedDataset | JsonScalarModel', default=JsonScalarModel)
#
# NestedAnyUnionT = TypeVar(
#     'NestedAnyUnionT', default=JsonScalarModel)


class GenericNestedDataset(Dataset[NestedAnyUnionT], Generic[NestedAnyUnionT]):
    ...


# NestedAnyUnion: TypeAlias = 'NestedDataset | ListAsNestedDatasetModel | JsonScalarModel'
TableModels: TypeAlias = ColumnWiseTableWithColNamesModel | RowWiseTableWithColNamesModel
# RecordModels: TypeAlias = JsonScalarModel | MixedJsonDictModel
RecordModels: TypeAlias = JsonScalarModel
OtherModels: TypeAlias = ListAsNestedDatasetModel | JsonScalarModel
NestedUnion: TypeAlias = 'TableModels | RecordModels | NestedDataset | OtherModels'


class NestedDataset(GenericNestedDataset[NestedUnion]):
    def _init(self, super_kwargs: dict[str, Any], **kwargs: Any) -> None:
        pass

    ...


NestedDataset.update_forward_refs()
ListAsNestedDatasetModel.update_forward_refs()
# MixedJsonDictModel.update_forward_refs()
