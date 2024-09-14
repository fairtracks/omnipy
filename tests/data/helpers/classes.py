from dataclasses import dataclass
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
        if type(other) == MyList:
            return MyList(*self.data + other.data)
        return NotImplemented

    def __iadd__(self, other: object) -> 'MyList[T] | NotImplementedType':
        if type(other) == MyList:
            self.data += other.data
            return self
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if type(other) == MyList:
            return self.data == other.data
        return False


class MyNumberBase:
    def __init__(self, val: int = 1):
        self.val = val

    def __eq__(self, other: 'MyNumberBase') -> bool:  # type: ignore[override]
        return self.val == other.val
