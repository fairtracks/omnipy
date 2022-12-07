from typing import Dict, List, Union

from unifair.data.model import Model

from ..json.models import JsonDict, JsonList


class TableOfStrings(Model[List[Dict[str, str]]]):
    ...


class JsonTableOfStrings(Model[JsonList[JsonDict[str]]]):
    ...


class TableOfStringsAndLists(Model[List[Dict[str, Union[str, List[str]]]]]):
    ...
