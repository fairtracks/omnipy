from __future__ import annotations

from typing import Dict, Generic, List, Optional, TypeAlias, TypeVar, Union

from omnipy.data.model import Model
from omnipy.modules.json.types import JsonScalar

# Basic building block models

BaseT = TypeVar('BaseT', bound=Union[JsonScalar, 'JsonListModel', 'JsonDictModel', List, Dict])
JsonSubModelT = TypeVar('JsonSubModelT', bound=Union[JsonScalar, 'JsonListModel', 'JsonDictModel'])


class _JsonBaseModel(Model[BaseT], Generic[BaseT]):
    ...


# Optional needed by pydantic
class JsonListModel(_JsonBaseModel[List[Optional[JsonSubModelT]]], Generic[JsonSubModelT]):
    ...


# Optional needed by pydantic
class JsonDictModel(_JsonBaseModel[Dict[str, Optional[JsonSubModelT]]], Generic[JsonSubModelT]):
    ...


JsonSubModel: TypeAlias = Union[JsonScalar,
                                JsonListModel['JsonSubModel'],
                                JsonDictModel['JsonSubModel']]
JsonNoListsSubModel: TypeAlias = Union[JsonScalar, JsonDictModel['JsonNoListsSubModel']]

JsonListModel['JsonSubModel'].update_forward_refs(JsonSubModel=JsonSubModel)
JsonDictModel['JsonSubModel'].update_forward_refs(JsonSubModel=JsonSubModel)
JsonListModel['JsonNoListsSubModel'].update_forward_refs(JsonNoListsSubModel=JsonNoListsSubModel)
JsonDictModel['JsonNoListsSubModel'].update_forward_refs(JsonNoListsSubModel=JsonNoListsSubModel)

# Core JSON model


class JsonModel(_JsonBaseModel[JsonSubModel]):
    ...


# Generic JSON dataset to use for custom JSON models


class JsonCustomModel(_JsonBaseModel[JsonSubModelT], Generic[JsonSubModelT]):
    ...


# List at the top level

JsonListOfScalarsModel: TypeAlias = JsonListModel[JsonScalar]
JsonListOfAnyModel: TypeAlias = JsonListModel[JsonSubModel]
JsonListOfDictsOfScalarsModel: TypeAlias = JsonListModel[JsonDictModel[JsonScalar]]
JsonListOfDictsOfAnyModel: TypeAlias = JsonListModel[JsonDictModel[JsonSubModel]]
JsonListOfListsOfScalarsModel: TypeAlias = JsonListModel[JsonListModel[JsonScalar]]
JsonListOfListsOfAnyModel: TypeAlias = JsonListModel[JsonListModel[JsonSubModel]]

# Dict at the top level

JsonDictOfScalarsModel: TypeAlias = JsonDictModel[JsonScalar]
JsonDictOfAnyModel: TypeAlias = JsonDictModel[JsonSubModel]
JsonDictOfDictsOfScalarsModel: TypeAlias = JsonDictModel[JsonDictModel[JsonScalar]]
JsonDictOfDictsOfAnyModel: TypeAlias = JsonDictModel[JsonDictModel[JsonSubModel]]
JsonDictOfListsOfScalarsModel: TypeAlias = JsonDictModel[JsonListModel[JsonScalar]]
JsonDictOfListsOfAnyModel: TypeAlias = JsonDictModel[JsonListModel[JsonSubModel]]

# More specific models

JsonNestedDictsModel: TypeAlias = JsonDictModel[JsonNoListsSubModel]
JsonListOfNestedDictsModel: TypeAlias = JsonListModel[JsonNestedDictsModel]
JsonDictOfListsOfDictsOfAnyModel: TypeAlias = JsonDictModel[JsonListOfDictsOfAnyModel]
