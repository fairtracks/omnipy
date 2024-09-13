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

# TODO: switch from plural to singular for names of modules in omnipy modules
# TODO: call omnipy modules something else than modules, to distinguish from Python modules.
#       Perhaps plugins?
#
_JsonModelT = TypeVar('_JsonModelT', bound=Model, default=JsonModel)


class _JsonBaseDataset(Dataset[_JsonModelT], Generic[_JsonModelT]):
    """"""
    ...


class JsonDataset(_JsonBaseDataset[JsonModel]):
    """"""
    ...


class JsonScalarDataset(_JsonBaseDataset[JsonScalarModel]):
    """"""
    ...


# List at the top level


class JsonListDataset(_JsonBaseDataset[JsonListModel]):
    """"""
    ...


class JsonListOfScalarsDataset(_JsonBaseDataset[JsonListOfScalarsModel]):
    """"""
    ...


class JsonListOfListsDataset(_JsonBaseDataset[JsonListOfListsModel]):
    """"""
    ...


class JsonListOfListsOfScalarsDataset(_JsonBaseDataset[JsonListOfListsOfScalarsModel]):
    """"""
    ...


class JsonListOfDictsDataset(_JsonBaseDataset[JsonListOfDictsModel]):
    """"""
    ...


class JsonListOfDictsOfScalarsDataset(_JsonBaseDataset[JsonListOfDictsOfScalarsModel]):
    """"""
    ...


# Dict at the top level


class JsonDictDataset(_JsonBaseDataset[JsonDictModel]):
    ...


class JsonDictOfScalarsDataset(_JsonBaseDataset[JsonDictOfScalarsModel]):
    ...


class JsonDictOfListsDataset(_JsonBaseDataset[JsonDictOfListsModel]):
    ...


class JsonDictOfListsOfScalarsDataset(_JsonBaseDataset[JsonDictOfListsOfScalarsModel]):
    ...


class JsonDictOfDictsDataset(_JsonBaseDataset[JsonDictOfDictsModel]):
    ...


class JsonDictOfDictsOfScalarsDataset(_JsonBaseDataset[JsonDictOfDictsOfScalarsModel]):
    ...


# Nested datasets


class JsonOnlyListsDataset(_JsonBaseDataset[JsonOnlyListsModel]):
    ...


class JsonNestedListsDataset(_JsonBaseDataset[JsonNestedListsModel]):
    ...


class JsonOnlyDictsDataset(_JsonBaseDataset[JsonOnlyDictsModel]):
    ...


class JsonNestedDictsDataset(_JsonBaseDataset[JsonNestedDictsModel]):
    ...


# More specific datasets


class JsonListOfNestedDictsDataset(_JsonBaseDataset[JsonListOfNestedDictsModel]):
    ...


class JsonDictOfNestedListsDataset(_JsonBaseDataset[JsonDictOfNestedListsModel]):
    ...


class JsonDictOfListsOfDictsDataset(_JsonBaseDataset[JsonDictOfListsOfDictsModel]):
    ...


# Custom datasets
