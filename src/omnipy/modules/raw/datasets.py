from omnipy.data.dataset import Dataset, ListOfParamModelDataset, ParamDataset

from .models import (BytesModel,
                     JoinColumnsToLinesModel,
                     JoinItemsModel,
                     JoinLinesModel,
                     SplitLinesToColumnsModel,
                     SplitToItemsModel,
                     SplitToLinesModel,
                     StrModel)


class BytesDataset(ParamDataset[BytesModel, str]):
    ...


class StrDataset(ParamDataset[StrModel, str]):
    ...


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
