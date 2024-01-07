from omnipy.data.dataset import Dataset, ListOfParamModelDataset, ParamDataset

from .models import DefaultStrModel, ListOfUpperStrModel, MyFloatObjModel, UpperStrModel


class MyFloatObjDataset(Dataset[MyFloatObjModel]):
    ...


class UpperStrDataset(ParamDataset[UpperStrModel, bool]):
    ...


class DefaultStrDataset(ParamDataset[DefaultStrModel, bool]):
    ...


class ListOfUpperStrDataset(ListOfParamModelDataset[ListOfUpperStrModel, bool]):
    ...
