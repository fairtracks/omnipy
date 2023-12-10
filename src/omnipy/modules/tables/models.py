from omnipy.data.model import Model
from omnipy.modules.json.models import JsonDictM, JsonListM


class TableOfStrings(Model[list[dict[str, str]]]):
    ...


class JsonTableOfStrings(JsonListM[JsonDictM[str]]):
    ...


class TableOfStringsAndLists(Model[list[dict[str, str | list[str]]]]):
    ...
