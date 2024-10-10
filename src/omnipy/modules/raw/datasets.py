from typing import Generic

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.param import bind_adjust_dataset_func

from .models import (BytesModel,
                     JoinColumnsToLinesModel,
                     JoinItemsModel,
                     JoinLinesModel,
                     JoinSubitemsToItemsModel,
                     SplitItemsToSubitemsModel,
                     SplitLinesToColumnsModel,
                     SplitToItemsModel,
                     SplitToLinesModel,
                     StrModel)

BytesModelT = TypeVar('BytesModelT', default=BytesModel)
StrModelT = TypeVar('StrModelT', default=StrModel)
SplitToItemsModelT = TypeVar('SplitToItemsModelT', default=SplitToItemsModel)
JoinItemsModelT = TypeVar('JoinItemsModelT', default=JoinItemsModel)
SplitItemsToSubitemsModelT = TypeVar(
    'SplitItemsToSubitemsModelT', default=SplitItemsToSubitemsModel)
JoinSubitemsToItemsModelT = TypeVar('JoinSubitemsToItemsModelT', default=JoinSubitemsToItemsModel)


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


class _SplitToItemsDataset(Dataset[SplitToItemsModelT], Generic[SplitToItemsModelT]):
    ...


class SplitToItemsDataset(_SplitToItemsDataset[SplitToItemsModel]):
    adjust = bind_adjust_dataset_func(
        _SplitToItemsDataset[SplitToItemsModel].clone_dataset_cls,
        SplitToItemsModel,
        SplitToItemsModel.Params,
    )


class SplitToLinesDataset(_SplitToItemsDataset[SplitToLinesModel]):
    adjust = bind_adjust_dataset_func(
        _SplitToItemsDataset[SplitToLinesModel].clone_dataset_cls,
        SplitToLinesModel,
        SplitToLinesModel.Params,
    )


class _JoinItemsDataset(Dataset[JoinItemsModelT], Generic[JoinItemsModelT]):
    ...


class JoinItemsDataset(_JoinItemsDataset[JoinItemsModel]):
    adjust = bind_adjust_dataset_func(
        _JoinItemsDataset[JoinItemsModel].clone_dataset_cls,
        JoinItemsModel,
        JoinItemsModel.Params,
    )


class JoinLinesDataset(_JoinItemsDataset[JoinLinesModel]):
    adjust = bind_adjust_dataset_func(
        _JoinItemsDataset[JoinLinesModel].clone_dataset_cls,
        JoinLinesModel,
        JoinLinesModel.Params,
    )


class _SplitItemsToSubitemsDataset(Dataset[SplitItemsToSubitemsModelT],
                                   Generic[SplitItemsToSubitemsModelT]):
    ...


class SplitLinesToColumnsDataset(_SplitItemsToSubitemsDataset[SplitLinesToColumnsModel]):
    adjust = bind_adjust_dataset_func(
        _SplitItemsToSubitemsDataset[SplitLinesToColumnsModel].clone_dataset_cls,
        SplitLinesToColumnsModel,
        SplitLinesToColumnsModel.Params,
    )


class _JoinSubitemsToItemsDataset(Dataset[JoinSubitemsToItemsModelT],
                                  Generic[JoinSubitemsToItemsModelT]):
    ...


class JoinColumnsToLinesDataset(_JoinSubitemsToItemsDataset[JoinColumnsToLinesModel]):
    adjust = bind_adjust_dataset_func(
        _JoinSubitemsToItemsDataset[JoinColumnsToLinesModel].clone_dataset_cls,
        JoinColumnsToLinesModel,
        JoinColumnsToLinesModel.Params,
    )
