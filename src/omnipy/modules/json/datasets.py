from typing import Generic, TypeVar

from omnipy.data.dataset import Dataset

from ...data.model import Model
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
                     JsonNoDictsModel,
                     JsonNoListsModel,
                     JsonScalarModel)

# TODO: switch from plural to singular for names of modules in omnipy modules
# TODO: call omnipy modules something else than modules, to distinguish from Python modules.
#       Perhaps plugins?
#
JsonModelT = TypeVar('JsonModelT', bound=Model)


class JsonBaseDataset(Dataset[JsonModelT], Generic[JsonModelT]):
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


class JsonNoDictsDataset(JsonBaseDataset[JsonNoDictsModel]):
    ...


class JsonNestedListsDataset(JsonBaseDataset[JsonNestedListsModel]):
    ...


class JsonNoListsDataset(JsonBaseDataset[JsonNoListsModel]):
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
