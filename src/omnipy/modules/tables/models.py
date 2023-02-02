from typing import Dict, List, Union

from omnipy.data.model import Model
from omnipy.modules.json.models import JsonDictModel, JsonListModel


class TableOfStrings(Model[List[Dict[str, str]]]):
    ...


class JsonTableOfStrings(JsonListModel[JsonDictModel[str]]):
    ...


class TableOfStringsAndLists(Model[List[Dict[str, Union[str, List[str]]]]]):
    ...
