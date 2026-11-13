"""Datasets of catalogue search requests and tables, keyed by table name."""

import omnipy as om

from .models import ResourceTypeToSearchRequestMapper, SearchResponseToTableMapper


class SearchRequestDataset(om.Dataset[ResourceTypeToSearchRequestMapper]):
    """Search requests, keyed by the name of the table to create from each response."""


class CatalogueTablesDataset(om.Dataset[SearchResponseToTableMapper]):
    """Tables of catalogue records, keyed by the name of the table."""
