from typing import Dict, List, Union

from unifair.data.model import Model


class TableOfStrings(Model[List[Dict[str, str]]]):
    ...


class TableOfStringsAndLists(Model[List[Dict[str, Union[str, List[str]]]]]):
    ...
