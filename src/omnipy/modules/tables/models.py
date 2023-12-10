from typing import Union

from omnipy.data.model import Model
from omnipy.modules.json.models import JsonDictM, JsonListM


class TableOfStrings(Model[list[dict[str, str]]]):
    ...


class JsonTableOfStrings(JsonListM[JsonDictM[str]]):
    ...


class TableOfStringsAndLists(Model[list[dict[str, Union[str, list[str]]]]]):
    ...
