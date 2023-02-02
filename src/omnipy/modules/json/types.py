from __future__ import annotations

from typing import Dict, Generic, List, TypeAlias, TypeVar, Union

JsonScalar: TypeAlias = Union[None, int, float, str, bool]

JsonT = TypeVar('JsonT', bound=Union[JsonScalar, 'JsonList', 'JsonDict'])


class JsonList(List[JsonT], Generic[JsonT]):
    ...


class JsonDict(Dict[str, JsonT], Generic[JsonT]):
    ...


Json: TypeAlias = Union[JsonScalar, JsonList['Json'], JsonDict['Json']]
JsonNoLists: TypeAlias = Union[JsonScalar, JsonDict['JsonNoLists']]

# List at the top level

JsonListOfScalars: TypeAlias = JsonList[JsonScalar]
JsonListOfAny: TypeAlias = JsonList[Json]
JsonListOfDictsOfScalars: TypeAlias = JsonList[JsonDict[JsonScalar]]
JsonListOfDictsOfAny: TypeAlias = JsonList[JsonDict[Json]]
JsonListOfListsOfScalars: TypeAlias = JsonList[JsonList[JsonScalar]]
JsonListOfListsOfAny: TypeAlias = JsonList[JsonList[Json]]

# Dict at the top level

JsonDictOfScalars: TypeAlias = JsonDict[JsonScalar]
JsonDictOfAny: TypeAlias = JsonDict[Json]
JsonDictOfDictsOfScalars: TypeAlias = JsonDict[JsonDict[JsonScalar]]
JsonDictOfDictsOfAny: TypeAlias = JsonDict[JsonDict[Json]]
JsonDictOfListsOfScalars: TypeAlias = JsonDict[JsonList[JsonScalar]]
JsonDictOfListsOfAny: TypeAlias = JsonDict[JsonList[Json]]

# More specific models

JsonNestedDicts: TypeAlias = JsonDict[JsonNoLists]
JsonListOfNestedDicts: TypeAlias = JsonList[JsonNestedDicts]
JsonDictOfListsOfDictsOfAny: TypeAlias = JsonDict[JsonListOfDictsOfAny]
