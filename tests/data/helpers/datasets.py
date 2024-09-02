from typing import Generic, Optional, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset, ListOfParamModelDataset, ParamDataset
from omnipy.data.model import Model
from omnipy.data.param import bind_adjust_dataset_func

from .models import (DefaultStrModel,
                     ListOfUpperStrModel,
                     MyFloatObjModel,
                     ParamUpperStrModel,
                     UpperStrModel)

ChildT = TypeVar('ChildT', default=object)


class MyFloatObjDataset(Dataset[MyFloatObjModel]):
    ...


class CBA:
    class MyGenericDataset(Dataset[Model[Optional[ChildT]]], Generic[ChildT]):
        ...


MyFwdRefDataset: TypeAlias = CBA.MyGenericDataset['NumberModel']
MyNestedFwdRefDataset: TypeAlias = CBA.MyGenericDataset['str | NumberModel']


class NumberModel(Model[int]):
    ...


MyFwdRefDataset.update_forward_refs(NumberModel=NumberModel)
MyNestedFwdRefDataset.update_forward_refs(NumberModel=NumberModel)


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
