from omnipy.data.dataset import Dataset

from .models import AutoResponseContentsModel, HttpUrlModel


class HttpUrlDataset(Dataset[HttpUrlModel]):
    ...


class AutoResponseContentsDataset(Dataset[AutoResponseContentsModel]):
    ...
