from typing import Iterable

from omnipy.data.model import Model


class NotIteratorExceptStrings(Model[object]):
    def _parse_data(cls, data: object) -> object:
        assert isinstance(data, str) or not isinstance(data, Iterable)