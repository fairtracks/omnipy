from typing import Generic

from typing_extensions import TypeVar

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model

from .models import (JsonDictModel,
                     JsonDictOfDictsModel,
                     JsonDictOfDictsOfScalarsModel,
                     JsonDictOfListsModel,
                     JsonDictOfListsOfDictsModel,
                     JsonDictOfListsOfScalarsModel,
                     JsonDictOfNestedListsModel,
                     JsonDictOfScalarsModel,
                     JsonListModel,
                     JsonListOfDictsModel,
                     JsonListOfDictsOfScalarsModel,
                     JsonListOfListsModel,
                     JsonListOfListsOfScalarsModel,
                     JsonListOfNestedDictsModel,
                     JsonListOfScalarsModel,
                     JsonModel,
                     JsonNestedDictsModel,
                     JsonNestedListsModel,
                     JsonOnlyDictsModel,
                     JsonOnlyListsModel,
                     JsonScalarModel)

_JsonModelT = TypeVar('_JsonModelT', bound=Model, default=JsonModel)


class JsonBaseDataset(Dataset[_JsonModelT], Generic[_JsonModelT]):
    """"""
    ...


class JsonDataset(JsonBaseDataset[JsonModel]):
    """"""
    ...


class JsonScalarDataset(JsonBaseDataset[JsonScalarModel]):
    """"""
    ...


# List at the top level


class JsonListDataset(JsonBaseDataset[JsonListModel]):
    """"""
    ...


class JsonListOfScalarsDataset(JsonBaseDataset[JsonListOfScalarsModel]):
    """"""
    ...


class JsonListOfListsDataset(JsonBaseDataset[JsonListOfListsModel]):
    """"""
    ...


class JsonListOfListsOfScalarsDataset(JsonBaseDataset[JsonListOfListsOfScalarsModel]):
    """"""
    ...


class JsonListOfDictsDataset(JsonBaseDataset[JsonListOfDictsModel]):
    """"""
    ...


class JsonListOfDictsOfScalarsDataset(JsonBaseDataset[JsonListOfDictsOfScalarsModel]):
    """"""
    ...


# Dict at the top level


class JsonDictDataset(JsonBaseDataset[JsonDictModel]):
    ...


class JsonDictOfScalarsDataset(JsonBaseDataset[JsonDictOfScalarsModel]):
    ...


class JsonDictOfListsDataset(JsonBaseDataset[JsonDictOfListsModel]):
    ...


class JsonDictOfListsOfScalarsDataset(JsonBaseDataset[JsonDictOfListsOfScalarsModel]):
    ...


class JsonDictOfDictsDataset(JsonBaseDataset[JsonDictOfDictsModel]):
    ...


class JsonDictOfDictsOfScalarsDataset(JsonBaseDataset[JsonDictOfDictsOfScalarsModel]):
    ...


# Nested datasets


class JsonOnlyListsDataset(JsonBaseDataset[JsonOnlyListsModel]):
    ...


class JsonNestedListsDataset(JsonBaseDataset[JsonNestedListsModel]):
    ...


class JsonOnlyDictsDataset(JsonBaseDataset[JsonOnlyDictsModel]):
    ...


class JsonNestedDictsDataset(JsonBaseDataset[JsonNestedDictsModel]):
    ...


# More specific datasets


class JsonListOfNestedDictsDataset(JsonBaseDataset[JsonListOfNestedDictsModel]):
    ...


class JsonDictOfNestedListsDataset(JsonBaseDataset[JsonDictOfNestedListsModel]):
    ...


class JsonDictOfListsOfDictsDataset(JsonBaseDataset[JsonDictOfListsOfDictsModel]):
    ...


# Custom datasets
