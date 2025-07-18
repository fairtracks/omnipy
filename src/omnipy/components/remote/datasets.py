from omnipy.data.dataset import Dataset

from .models import AutoResponseContentModel, HttpUrlModel


class HttpUrlDataset(Dataset[HttpUrlModel]):
    ...


class AutoResponseContentDataset(Dataset[AutoResponseContentModel]):
    ...
