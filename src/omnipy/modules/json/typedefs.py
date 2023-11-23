from __future__ import annotations

from typing import Dict, List, TypeAlias, Union

JsonScalar: TypeAlias = Union[None, int, float, str, bool]
JsonList: TypeAlias = List['Json']
JsonDict: TypeAlias = Dict[str, 'Json']
Json: TypeAlias = Union[JsonList, JsonDict, JsonScalar]

# List at the top level

JsonListOfScalars: TypeAlias = List[JsonScalar]
JsonListOfLists: TypeAlias = List[JsonList]
JsonListOfListsOfScalars: TypeAlias = List[JsonListOfScalars]
JsonListOfDicts: TypeAlias = List[JsonDict]
JsonListOfDictsOfScalars: TypeAlias = List['JsonDictOfScalars']

# Dict at the top level

JsonDictOfScalars: TypeAlias = Dict[str, JsonScalar]
JsonDictOfLists: TypeAlias = Dict[str, JsonList]
JsonDictOfListsOfScalars: TypeAlias = Dict[str, JsonListOfScalars]
JsonDictOfDicts: TypeAlias = Dict[str, JsonDict]
JsonDictOfDictsOfScalars: TypeAlias = Dict[str, JsonDictOfScalars]

# Exclusion variants

JsonNoDicts: TypeAlias = Union[JsonScalar, 'JsonNestedLists']
JsonNestedLists: TypeAlias = List[JsonNoDicts]

JsonNoLists: TypeAlias = Union[JsonScalar, 'JsonNestedDicts']
JsonNestedDicts: TypeAlias = Dict[str, JsonNoLists]

# More specific types

JsonListOfNestedDicts: TypeAlias = List[JsonNestedDicts]
JsonDictOfNestedLists: TypeAlias = Dict[str, JsonNestedLists]
JsonDictOfListsOfDicts: TypeAlias = Dict[str, JsonListOfDicts]
