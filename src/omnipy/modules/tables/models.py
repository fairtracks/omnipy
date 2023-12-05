from typing import Dict, List, Union

from omnipy.data.model import Model
from omnipy.modules.json.models import JsonCustomDictModel, JsonCustomListModel


class TableOfStrings(Model[List[Dict[str, str]]]):
    ...


class JsonTableOfStrings(JsonCustomListModel[JsonCustomDictModel[str]]):
    ...


class TableOfStringsAndLists(Model[List[Dict[str, Union[str, List[str]]]]]):
    ...
