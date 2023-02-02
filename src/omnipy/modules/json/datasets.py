from __future__ import annotations

from typing import Generic, TypeAlias, TypeVar, Union

from omnipy.data.dataset import Dataset
from omnipy.modules.json.models import (JsonDictModel,
                                        JsonDictOfAnyModel,
                                        JsonDictOfDictsOfAnyModel,
                                        JsonDictOfDictsOfScalarsModel,
                                        JsonDictOfListsOfAnyModel,
                                        JsonDictOfListsOfDictsOfAnyModel,
                                        JsonDictOfListsOfScalarsModel,
                                        JsonDictOfScalarsModel,
                                        JsonListModel,
                                        JsonListOfAnyModel,
                                        JsonListOfDictsOfAnyModel,
                                        JsonListOfDictsOfScalarsModel,
                                        JsonListOfListsOfAnyModel,
                                        JsonListOfListsOfScalarsModel,
                                        JsonListOfNestedDictsModel,
                                        JsonListOfScalarsModel,
                                        JsonModel,
                                        JsonNestedDictsModel)

# TODO: switch from plural to singular for names of modules in omnipy modules
# TODO: call omnipy modules something else than modules, to distinguish from Python modules.
#       Perhaps plugins?

JsonModelT = TypeVar('JsonModelT', bound=Union[JsonModel, JsonListModel, JsonDictModel])


class JsonBaseDataset(Dataset[JsonModelT], Generic[JsonModelT]):
    ...


# Instance of JsonBaseDataset that covers all JSON data


class JsonDataset(JsonBaseDataset[JsonModel]):
    ...


# Generic JSON dataset to use for custom JSON datasets

JsonCustomDataset: TypeAlias = JsonBaseDataset

# List as top-level type

JsonListOfScalarsDatabase: TypeAlias = JsonBaseDataset[JsonListOfScalarsModel]
JsonListOfAnyDataset: TypeAlias = JsonBaseDataset[JsonListOfAnyModel]
JsonListOfDictsOfScalarsDataset: TypeAlias = JsonBaseDataset[JsonListOfDictsOfScalarsModel]
JsonListOfDictsOfAnyDataset: TypeAlias = JsonBaseDataset[JsonListOfDictsOfAnyModel]
JsonListOfListsOfScalarsDataset: TypeAlias = JsonBaseDataset[JsonListOfListsOfScalarsModel]
JsonListOfListsOfAnyDataset: TypeAlias = JsonBaseDataset[JsonListOfListsOfAnyModel]

# Dict as top-level type

JsonDictOfScalarsDataset: TypeAlias = JsonBaseDataset[JsonDictOfScalarsModel]
JsonDictOfAnyDataset: TypeAlias = JsonBaseDataset[JsonDictOfAnyModel]
JsonDictOfDictsOfScalarsDataset: TypeAlias = JsonBaseDataset[JsonDictOfDictsOfScalarsModel]
JsonDictOfDictsOfAnyDataset: TypeAlias = JsonBaseDataset[JsonDictOfDictsOfAnyModel]
JsonDictOfListsOfScalarsDataset: TypeAlias = JsonBaseDataset[JsonDictOfListsOfScalarsModel]
JsonDictOfListsOfAnyDataset: TypeAlias = JsonBaseDataset[JsonDictOfListsOfAnyModel]

# More specific models

JsonNestedDictsDataset: TypeAlias = JsonBaseDataset[JsonNestedDictsModel]
JsonListOfNestedDictsDataset: TypeAlias = JsonBaseDataset[JsonListOfNestedDictsModel]
JsonDictOfListsOfDictsOfAnyDataset: TypeAlias = JsonBaseDataset[JsonDictOfListsOfDictsOfAnyModel]
