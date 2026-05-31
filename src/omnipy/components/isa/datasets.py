"""Datasets for ISA-JSON documents and flattened ISA-JSON records."""

from omnipy.data.dataset import Dataset

from .models import FlattenedIsaJsonModel, IsaJsonModel


class IsaJsonDataset(Dataset[IsaJsonModel]):
    """Dataset containing validated ISA-JSON documents.

    Each record in the dataset is validated by :class:`IsaJsonModel`, allowing
    downstream ISA flows and tasks to operate on a consistent document shape.
    """
    ...


class FlattenedIsaJsonDataset(Dataset[FlattenedIsaJsonModel]):
    """Dataset containing flattened ISA-JSON records.

    Records in this dataset follow :class:`FlattenedIsaJsonModel` and are
    intended for tabular-style processing after ISA structures are flattened.
    """
    ...
