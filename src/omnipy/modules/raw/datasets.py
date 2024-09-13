from typing import Generic

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
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
SplitToLinesModelT = TypeVar('SplitToLinesModelT', default=SplitToLinesModel)
SplitToItemsModelT = TypeVar('SplitToItemsModelT', default=SplitToItemsModel)
JoinItemsModelT = TypeVar('JoinItemsModelT', default=JoinItemsModel)
SplitLinesToColumnsModelT = TypeVar('SplitLinesToColumnsModelT', default=SplitLinesToColumnsModel)
JoinColumnsToLinesModelT = TypeVar('JoinColumnsToLinesModelT', default=JoinColumnsToLinesModel)


class _BytesDataset(Dataset[BytesModelT], Generic[BytesModelT]):
    ...


class BytesDataset(_BytesDataset[BytesModel]):
    adjust = bind_adjust_dataset_func(
        _BytesDataset[BytesModel].clone_dataset_cls,
        BytesModel,
        BytesModel.Params,
    )


class _StrDataset(Dataset[StrModelT], Generic[StrModelT]):
    ...


class StrDataset(_StrDataset[StrModel]):
    adjust = bind_adjust_dataset_func(
        _StrDataset[StrModel].clone_dataset_cls,
        StrModel,
        StrModel.Params,
    )


class _SplitToLinesDataset(Dataset[SplitToLinesModelT], Generic[SplitToLinesModelT]):
    ...


class SplitToLinesDataset(_SplitToLinesDataset[SplitToLinesModel]):
    adjust = bind_adjust_dataset_func(
        _SplitToLinesDataset[SplitToLinesModel].clone_dataset_cls,
        SplitToLinesModel,
        SplitToLinesModel.Params,
    )


class JoinLinesDataset(Dataset[JoinLinesModel]):
    ...


class _SplitToItemsDataset(Dataset[SplitToItemsModelT], Generic[SplitToItemsModelT]):
    ...


class SplitToItemsDataset(_SplitToItemsDataset[SplitToItemsModel]):
    adjust = bind_adjust_dataset_func(
        _SplitToItemsDataset[SplitToItemsModel].clone_dataset_cls,
        SplitToItemsModel,
        SplitToItemsModel.Params,
    )


class _JoinItemsDataset(Dataset[JoinItemsModelT], Generic[JoinItemsModelT]):
    ...


class JoinItemsDataset(_JoinItemsDataset[JoinItemsModel]):
    adjust = bind_adjust_dataset_func(
        _JoinItemsDataset[JoinItemsModel].clone_dataset_cls,
        JoinItemsModel,
        JoinItemsModel.Params,
    )


class _SplitLinesToColumnsDataset(Dataset[SplitLinesToColumnsModelT],
                                  Generic[SplitLinesToColumnsModelT]):
    ...


class SplitLinesToColumnsDataset(_SplitLinesToColumnsDataset[SplitLinesToColumnsModel]):
    adjust = bind_adjust_dataset_func(
        _SplitLinesToColumnsDataset[SplitLinesToColumnsModel].clone_dataset_cls,
        SplitLinesToColumnsModel,
        SplitLinesToColumnsModel.Params,
    )


class _JoinColumnsToLinesDataset(Dataset[JoinColumnsToLinesModelT],
                                 Generic[JoinColumnsToLinesModelT]):
    ...


class JoinColumnsToLinesDataset(_JoinColumnsToLinesDataset[JoinColumnsToLinesModel]):
    adjust = bind_adjust_dataset_func(
        _JoinColumnsToLinesDataset[JoinColumnsToLinesModel].clone_dataset_cls,
        JoinColumnsToLinesModel,
        JoinColumnsToLinesModel.Params,
    )
