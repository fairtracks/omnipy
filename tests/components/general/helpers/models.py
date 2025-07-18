from types import NotImplementedType
from typing import Generic

from typing_extensions import TypeVar

from omnipy.data.model import Model

T = TypeVar('T')


class MyList(Generic[T]):
    def __init__(self, *args: T):
        self.data = list(args)

    def __repr__(self) -> str:
        return f'MyList({self.data.__repr__()})'

    def __add__(self, other: object) -> 'MyList[T] | NotImplementedType':
        if type(other) is MyList:
            return MyList(*self.data + other.data)
        return NotImplemented

    def __eq__(self, other):
        if type(other) is MyList:
            return self.data == other.data
        return False


class RotateOneCharModel(Model[str]):
    @classmethod
    def _parse_data(cls, data: str) -> str:
        return data[1:] + data[0]


class SplitCharsModel(Model[list[str] | str]):
    @classmethod
    def _parse_data(cls, data: list[str] | str) -> list[str]:
        if isinstance(data, str):
            return list(data)
        return data


class MyListModel(Model[MyList[str] | list[str]]):
    @classmethod
    def _parse_data(cls, data: MyList[str] | list[str]) -> MyList[str]:
        if isinstance(data, list):
            return MyList(*data)
        return data

    def to_data(self) -> list[str]:
        return self.content.data
