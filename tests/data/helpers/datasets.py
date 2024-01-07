from omnipy.data.dataset import ListOfParamModelDataset, ParamDataset

from .models import DefaultStrModel, ListOfUpperStrModel, UpperStrModel

from .models import DefaultStrModel, UpperStrModel


class UpperStrDataset(ParamDataset[UpperStrModel, bool]):
    ...


class DefaultStrDataset(ParamDataset[DefaultStrModel, bool]):
    ...


class ListOfUpperStrDataset(ListOfParamModelDataset[ListOfUpperStrModel, bool]):
    ...
