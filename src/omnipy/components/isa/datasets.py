"""Datasets for ISA-JSON documents and flattened ISA-JSON records."""

from omnipy.data.dataset import Dataset

from .models import FlattenedIsaJsonModel, IsaJsonModel


class IsaJsonDataset(Dataset[IsaJsonModel]):
    """Store ISA-JSON documents."""
    ...


class FlattenedIsaJsonDataset(Dataset[FlattenedIsaJsonModel]):
    """Store ISA-JSON documents transformed into flattened record structures."""
    ...
