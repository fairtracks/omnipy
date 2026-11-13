"""Operations on the LifeWatch ERIC catalogue search API."""

import omnipy as om

from .constants import SEARCH_URL
from .datasets import CatalogueTablesDataset, SearchRequestDataset


@om.TaskTemplate()
async def search_catalogue(
    requests: SearchRequestDataset,
    *,
    search_url: str = SEARCH_URL,
) -> CatalogueTablesDataset:
    """Post each search request to the catalogue, converting each response into a table."""
    return await om.resolve(requests.post(search_url, response_cls=CatalogueTablesDataset))
