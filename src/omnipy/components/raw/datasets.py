from typing import Generic

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.param import bind_adjust_dataset_func

from .models import (BytesModel,
                     JoinColumnsToLinesModel,
                     JoinItemsModel,
                     JoinItemsModelBase,
                     JoinLinesModel,
                     JoinSubitemsToItemsModelBase,
                     SplitItemsToSubitemsModelBase,
                     SplitLinesToColumnsModel,
                     SplitToItemsModel,
                     SplitToItemsModelBase,
                     SplitToLinesModel,
                     StrictBytesModel,
                     StrictStrModel,
                     StrModel)

_BytesModelT = TypeVar('_BytesModelT', bound=BytesModel)
_StrModelT = TypeVar('_StrModelT', bound=StrModel)
_SplitToItemsModelT = TypeVar('_SplitToItemsModelT', bound=SplitToItemsModelBase)
_JoinItemsModelT = TypeVar('_JoinItemsModelT', bound=JoinItemsModelBase)
_SplitItemsToSubitemsModelT = TypeVar(
    '_SplitItemsToSubitemsModelT', bound=SplitItemsToSubitemsModelBase)
_JoinSubitemsToItemsModelT = TypeVar(
    '_JoinSubitemsToItemsModelT', bound=JoinSubitemsToItemsModelBase)


class _BytesDataset(Dataset[_BytesModelT], Generic[_BytesModelT]):
    ...


class BytesDataset(_BytesDataset[BytesModel]):
    adjust = bind_adjust_dataset_func(
        _BytesDataset[BytesModel].clone_dataset_cls,
        BytesModel,
        BytesModel.Params,
    )


class StrictBytesDataset(Dataset[StrictBytesModel]):
    ...


class _StrDataset(Dataset[_StrModelT], Generic[_StrModelT]):
    ...


class StrDataset(_StrDataset[StrModel]):
    adjust = bind_adjust_dataset_func(
        _StrDataset[StrModel].clone_dataset_cls,
        StrModel,
        StrModel.Params,
    )


class StrictStrDataset(Dataset[StrictStrModel]):
    ...


class _SplitToItemsDataset(Dataset[_SplitToItemsModelT], Generic[_SplitToItemsModelT]):
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


class _JoinItemsDataset(Dataset[_JoinItemsModelT], Generic[_JoinItemsModelT]):
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


class _SplitItemsToSubitemsDataset(Dataset[_SplitItemsToSubitemsModelT],
                                   Generic[_SplitItemsToSubitemsModelT]):
    ...


class SplitLinesToColumnsDataset(_SplitItemsToSubitemsDataset[SplitLinesToColumnsModel]):
    adjust = bind_adjust_dataset_func(
        _SplitItemsToSubitemsDataset[SplitLinesToColumnsModel].clone_dataset_cls,
        SplitLinesToColumnsModel,
        SplitLinesToColumnsModel.Params,
    )


class _JoinSubitemsToItemsDataset(Dataset[_JoinSubitemsToItemsModelT],
                                  Generic[_JoinSubitemsToItemsModelT]):
    ...


class JoinColumnsToLinesDataset(_JoinSubitemsToItemsDataset[JoinColumnsToLinesModel]):
    adjust = bind_adjust_dataset_func(
        _JoinSubitemsToItemsDataset[JoinColumnsToLinesModel].clone_dataset_cls,
        JoinColumnsToLinesModel,
        JoinColumnsToLinesModel.Params,
    )
