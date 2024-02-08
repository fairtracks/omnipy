from omnipy.data.dataset import Dataset
from omnipy.modules.isa.models import FlattenedIsaJsonModel, IsaJsonModel


class IsaJsonDataset(Dataset[IsaJsonModel]):
    ...


class FlattenedIsaJsonDataset(Dataset[FlattenedIsaJsonModel]):
    ...
