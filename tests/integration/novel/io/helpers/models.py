"""Typed declarations for the paged-loading integration example."""

from typing import Literal

from omnipy.components.general.models import MergeListsOfRecordsIntoDatasetByPrimaryKeyModel
from omnipy.components.remote.datasets import HttpUrlDataset
from omnipy.components.remote.models import GeneratePagedUrlsModel
from omnipy.data._typing.helpers import mimics
from omnipy.data.primary_key import PrimaryKey
import omnipy.util.pydantic as pyd
from tests.components.remote.helpers.models import ObservationPagesInfo, ObservationPageUrl


@mimics(HttpUrlDataset)
class ObservationUrls(GeneratePagedUrlsModel[ObservationPageUrl, ObservationPagesInfo]): ...


class Observation(pyd.BaseModel):
    project: str
    identity: str
    value: int


class MergeObservations(
    MergeListsOfRecordsIntoDatasetByPrimaryKeyModel[
        PrimaryKey[Literal['project'], Literal['identity']], Observation
    ]
): ...
