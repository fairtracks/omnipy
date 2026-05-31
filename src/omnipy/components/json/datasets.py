"""JSON dataset types for collections of items with specific JSON shapes."""

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
                     JsonListOrDictModel,
                     JsonModel,
                     JsonNestedDictsModel,
                     JsonNestedListsModel,
                     JsonOnlyDictsModel,
                     JsonOnlyListsModel,
                     JsonScalarModel)

_JsonModelT = TypeVar('_JsonModelT', bound=Model, default=JsonModel)


class JsonBaseDataset(Dataset[_JsonModelT], Generic[_JsonModelT]):
    """A dataset type containing items that are each a JSON model."""
    ...


class JsonDataset(JsonBaseDataset[JsonModel]):
    """A dataset type containing items that are each a JSON model for any valid JSON value."""
    ...


class JsonListOrDictDataset(JsonBaseDataset[JsonListOrDictModel]):
    """A dataset type containing items that are each a JSON model for a top-level list or dictionary."""
    ...


class JsonScalarDataset(JsonBaseDataset[JsonScalarModel]):
    """A dataset type containing items that are each a JSON model for a JSON scalar value."""
    ...


# List at the top level


class JsonListDataset(JsonBaseDataset[JsonListModel]):
    """A dataset type containing items that are each a JSON model for a top-level list of JSON values."""
    ...


class JsonListOfScalarsDataset(JsonBaseDataset[JsonListOfScalarsModel]):
    """A dataset type containing items that are each a JSON model for a list of JSON scalars."""
    ...


class JsonListOfListsDataset(JsonBaseDataset[JsonListOfListsModel]):
    """A dataset type containing items that are each a JSON model for a list of JSON lists."""
    ...


class JsonListOfListsOfScalarsDataset(JsonBaseDataset[JsonListOfListsOfScalarsModel]):
    """A dataset type containing items that are each a JSON model for a list of lists of JSON scalars."""
    ...


class JsonListOfDictsDataset(JsonBaseDataset[JsonListOfDictsModel]):
    """A dataset type containing items that are each a JSON model for a list of JSON dictionaries."""
    ...


class JsonListOfDictsOfScalarsDataset(JsonBaseDataset[JsonListOfDictsOfScalarsModel]):
    """A dataset type containing items that are each a JSON model for a list of dictionaries of JSON scalars."""
    ...


# Dict at the top level


class JsonDictDataset(JsonBaseDataset[JsonDictModel]):
    """A dataset type containing items that are each a JSON model for a top-level dictionary of JSON values."""
    ...


class JsonDictOfScalarsDataset(JsonBaseDataset[JsonDictOfScalarsModel]):
    """A dataset type containing items that are each a JSON model for a dictionary of JSON scalars."""
    ...


class JsonDictOfListsDataset(JsonBaseDataset[JsonDictOfListsModel]):
    """A dataset type containing items that are each a JSON model for a dictionary of JSON lists."""
    ...


class JsonDictOfListsOfScalarsDataset(JsonBaseDataset[JsonDictOfListsOfScalarsModel]):
    """A dataset type containing items that are each a JSON model for a dictionary of lists of JSON scalars."""
    ...


class JsonDictOfDictsDataset(JsonBaseDataset[JsonDictOfDictsModel]):
    """A dataset type containing items that are each a JSON model for a dictionary of JSON dictionaries."""
    ...


class JsonDictOfDictsOfScalarsDataset(JsonBaseDataset[JsonDictOfDictsOfScalarsModel]):
    """A dataset type containing items that are each a JSON model for a dictionary of dictionaries of JSON scalars."""
    ...


# Nested datasets


class JsonOnlyListsDataset(JsonBaseDataset[JsonOnlyListsModel]):
    """A dataset type containing items that are each a JSON model composed only of nested lists and scalars."""
    ...


class JsonNestedListsDataset(JsonBaseDataset[JsonNestedListsModel]):
    """A dataset type containing items that are each a JSON model for a nested list structure of JSON scalars."""
    ...


class JsonOnlyDictsDataset(JsonBaseDataset[JsonOnlyDictsModel]):
    """A dataset type containing items that are each a JSON model composed only of nested dictionaries and scalars."""
    ...


class JsonNestedDictsDataset(JsonBaseDataset[JsonNestedDictsModel]):
    """A dataset type containing items that are each a JSON model for a nested dictionary structure of JSON scalars."""
    ...


# More specific datasets


class JsonListOfNestedDictsDataset(JsonBaseDataset[JsonListOfNestedDictsModel]):
    """A dataset type containing items that are each a JSON model for a list of nested dictionaries of JSON scalars."""
    ...


class JsonDictOfNestedListsDataset(JsonBaseDataset[JsonDictOfNestedListsModel]):
    """A dataset type containing items that are each a JSON model for a dictionary of nested lists of JSON scalars."""
    ...


class JsonDictOfListsOfDictsDataset(JsonBaseDataset[JsonDictOfListsOfDictsModel]):
    """A dataset type containing items that are each a JSON model for a dictionary of lists of JSON dictionaries."""
    ...


# Custom datasets
