from omnipy.data.dataset import Dataset

from .models import FlattenedIsaJsonModel, IsaJsonModel


class IsaJsonDataset(Dataset[IsaJsonModel]):
    ...


class FlattenedIsaJsonDataset(Dataset[FlattenedIsaJsonModel]):
    ...
