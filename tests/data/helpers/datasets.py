from typing import Generic, Optional, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset, ListOfParamModelDataset, ParamDataset
from omnipy.data.param import bind_adjust_dataset_func

from .models import (DefaultStrModel,
                     ListOfUpperStrModel,
                     MyFloatObjModel,
                     ParamUpperStrModel,
                     UpperStrModel)


class MyFloatObjDataset(Dataset[MyFloatObjModel]):
    ...


class UpperStrDataset(ParamDataset[UpperStrModel, bool]):
    ...


ParamUpperStrModelT = TypeVar('ParamUpperStrModelT', default=ParamUpperStrModel)


class _ParamUpperStrDataset(Dataset[ParamUpperStrModelT], Generic[ParamUpperStrModelT]):
    ...


class ParamUpperStrDataset(_ParamUpperStrDataset[ParamUpperStrModelT],
                           Generic[ParamUpperStrModelT]):
    adjust = bind_adjust_dataset_func(
        _ParamUpperStrDataset[ParamUpperStrModelT].clone_dataset_cls,
        ParamUpperStrModel,
        ParamUpperStrModel.Params,
    )


class DefaultStrDataset(ParamDataset[DefaultStrModel, bool]):
    ...


class ListOfUpperStrDataset(ListOfParamModelDataset[ListOfUpperStrModel, bool]):
    ...
