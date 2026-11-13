"""Dataflow importing the LifeWatch ERIC catalogue into pandas tables."""

import omnipy as om

from .constants import CATALOGUE_TABLES, SEARCH_URL
from .datasets import SearchRequestDataset
from .enums import ResourceType
from .tasks import search_catalogue


@om.LinearFlowTemplate(
    SearchRequestDataset,
    search_catalogue,
    om.require_all_items,
    om.PandasDataset,
)
async def import_lifewatch_catalogue(
    resource_types_by_table: dict[str, ResourceType] = CATALOGUE_TABLES,
    *,
    search_url: str = SEARCH_URL,
) -> om.PandasDataset: ...
