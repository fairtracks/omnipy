from typing import TypeAlias, Union

JsonScalar: TypeAlias = Union[None, int, float, str, bool]
JsonList: TypeAlias = list['Json']
JsonDict: TypeAlias = dict[str, 'Json']
Json: TypeAlias = Union[JsonList, JsonDict, JsonScalar]

# list at the top level

JsonListOfScalars: TypeAlias = list[JsonScalar]
JsonListOfLists: TypeAlias = list[JsonList]
JsonListOfListsOfScalars: TypeAlias = list[JsonListOfScalars]
JsonListOfDicts: TypeAlias = list[JsonDict]
JsonListOfDictsOfScalars: TypeAlias = list['JsonDictOfScalars']

# dict at the top level

JsonDictOfScalars: TypeAlias = dict[str, JsonScalar]
JsonDictOfLists: TypeAlias = dict[str, JsonList]
JsonDictOfListsOfScalars: TypeAlias = dict[str, JsonListOfScalars]
JsonDictOfDicts: TypeAlias = dict[str, JsonDict]
JsonDictOfDictsOfScalars: TypeAlias = dict[str, JsonDictOfScalars]

# Exclusion variants

JsonNoDicts: TypeAlias = Union[JsonScalar, 'JsonNestedLists']
JsonNestedLists: TypeAlias = list[JsonNoDicts]

JsonNoLists: TypeAlias = Union[JsonScalar, 'JsonNestedDicts']
JsonNestedDicts: TypeAlias = dict[str, JsonNoLists]

# More specific types

JsonListOfNestedDicts: TypeAlias = list[JsonNestedDicts]
JsonDictOfNestedLists: TypeAlias = dict[str, JsonNestedLists]
JsonDictOfListsOfDicts: TypeAlias = dict[str, JsonListOfDicts]
