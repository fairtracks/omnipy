from typing import Literal, NamedTuple

from omnipy.components.general.models import MergeListsOfRecordsIntoDatasetByPrimaryKeyModel
from omnipy.data._mixins.display import BaseDisplayMixin
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.primary_key import PrimaryKey
import omnipy.util.pydantic as pyd


class DisplayRecord(pyd.BaseModel):
    name: str
    value: int


class IntegerDataset(Dataset[Model[int]]): ...


class WrappedIntegerDataset(Model[IntegerDataset]): ...


class MergedRecordDataset(
    MergeListsOfRecordsIntoDatasetByPrimaryKeyModel[PrimaryKey[Literal['name']], DisplayRecord]
): ...


class WrappedDatasetCase(NamedTuple):
    wrapped: BaseDisplayMixin
    dataset: BaseDisplayMixin
