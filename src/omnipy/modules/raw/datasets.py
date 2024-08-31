from typing import Generic

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset, ListOfParamModelDataset, ParamDataset
from omnipy.data.param import bind_adjust_dataset_func

from .models import (BytesModel,
                     JoinColumnsToLinesModel,
                     JoinItemsModel,
                     JoinLinesModel,
                     SplitLinesToColumnsModel,
                     SplitToItemsModel,
                     SplitToLinesModel,
                     StrModel)

BytesModelT = TypeVar('BytesModelT', default=BytesModel)
StrModelT = TypeVar('StrModelT', default=StrModel)


class _BytesDataset(Dataset[BytesModelT], Generic[BytesModelT]):
    ...


class BytesDataset(_BytesDataset[BytesModelT], Generic[BytesModelT]):
    adjust = bind_adjust_dataset_func(
        _BytesDataset[BytesModelT].clone_dataset_cls,
        BytesModel,
        BytesModel.Params,
    )


class _StrDataset(Dataset[StrModelT], Generic[StrModelT]):
    ...


class StrDataset(_StrDataset[StrModelT], Generic[StrModelT]):
    adjust = bind_adjust_dataset_func(
        _StrDataset[StrModelT].clone_dataset_cls,
        StrModel,
        StrModel.Params,
    )


class SplitToLinesDataset(ParamDataset[SplitToLinesModel, bool]):
    ...


class JoinLinesDataset(Dataset[JoinLinesModel]):
    ...


class SplitToItemsDataset(ParamDataset[SplitToItemsModel, bool | str]):
    ...


class JoinItemsDataset(ParamDataset[JoinItemsModel, str]):
    ...


class SplitLinesToColumnsDataset(ListOfParamModelDataset[SplitLinesToColumnsModel, bool | str]):
    ...


class JoinColumnsToLinesDataset(ListOfParamModelDataset[JoinColumnsToLinesModel, str]):
    ...
