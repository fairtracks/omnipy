from omnipy.data.dataset import ParamDataset

from .models import DefaultStrModel, UpperStrModel


class UpperStrDataset(ParamDataset[UpperStrModel, bool]):
    ...


class DefaultStrDataset(ParamDataset[DefaultStrModel, bool]):
    ...
