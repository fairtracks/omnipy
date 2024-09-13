from typing import Generic, Optional, TypeAlias

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy.data.param import bind_adjust_dataset_func

from .models import DefaultStrModel, MyFloatObjModel, ParamUpperStrModel

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

ParamUpperStrModelT = TypeVar('ParamUpperStrModelT', default=ParamUpperStrModel)


class _ParamUpperStrDataset(Dataset[ParamUpperStrModelT], Generic[ParamUpperStrModelT]):
    ...


class ParamUpperStrDataset(_ParamUpperStrDataset[ParamUpperStrModel]):
    adjust = bind_adjust_dataset_func(
        _ParamUpperStrDataset[ParamUpperStrModel].clone_dataset_cls,
        ParamUpperStrModel,
        ParamUpperStrModel.Params,
    )


DefaultStrModelT = TypeVar('DefaultStrModelT', default=DefaultStrModel)


class _DefaultStrDataset(Dataset[DefaultStrModelT], Generic[DefaultStrModelT]):
    ...


class DefaultStrDataset(_DefaultStrDataset[DefaultStrModel]):
    adjust = bind_adjust_dataset_func(
        _DefaultStrDataset[DefaultStrModel].clone_dataset_cls,
        DefaultStrModel,
        DefaultStrModel.Params,
    )
