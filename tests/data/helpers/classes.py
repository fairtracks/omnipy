from dataclasses import dataclass
from types import NotImplementedType
from typing import Generic

from typing_extensions import TypeVar

T = TypeVar('T')


@dataclass
class MyFloatObject:
    int_part: int = 0
    float_part: float = 0.0
    precision: int = 4


class MyList(Generic[T]):
    def __init__(self, *args: T):
        self.data = list(args)

    def __repr__(self) -> str:
        return f'MyList({self.data.__repr__()})'

    def __add__(self, other: object) -> 'MyList[T] | NotImplementedType':
        if type(other) is MyList:
            return MyList(*self.data + other.data)
        return NotImplemented

    def __iadd__(self, other: object) -> 'MyList[T] | NotImplementedType':
        if type(other) is MyList:
            self.data += other.data
            return self
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if type(other) is MyList:
            return self.data == other.data
        return False


class MyNumberBase:
    def __init__(self, val: int = 1):
        self.val = val

    def __eq__(self, other: 'MyNumberBase') -> bool:  # type: ignore[override]
        return self.val == other.val


class MyPath():
    def __init__(self, *args, **kwargs):
        self._path = args[0] if len(args) > 0 else '.'

    def __eq__(self, other):
        return self._path == other._path

    def __str__(self):
        return self._path

    def __truediv__(self, append_path: str) -> 'MyPath':
        return MyPath(f'{self._path}/{append_path}')
