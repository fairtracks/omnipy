from dataclasses import dataclass
from types import NotImplementedType
from typing import Generic, Iterator

from typing_extensions import TypeVar

from omnipy.shared.protocols._collections_abc import IsDictItems, IsDictKeys, IsDictValues

T = TypeVar('T')
U = TypeVar('U')


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

    def __getitem__(self, item: int):
        return self.data[item]

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)

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


class MyDict(Generic[T, U]):
    def __init__(self, _dict: dict[T, U] | None = None) -> None:
        self.data: dict[T, U] = _dict if _dict is not None else {}

    def __repr__(self) -> str:
        return f'MyStrKeyDict({self.data.__repr__()})'

    def __getitem__(self, item: T) -> U:
        return self.data[item]

    def __iter__(self) -> Iterator[T]:
        return (_ for _ in self.keys())

    def keys(self) -> IsDictKeys[T, U]:
        return self.data.keys()

    def values(self) -> IsDictValues[T, U]:
        return self.data.values()

    def items(self) -> IsDictItems[T, U]:
        return self.data.items()


class MyStrKeyDict(MyDict[str, U], Generic[U]):
    def __init__(self, **kwargs: U) -> None:
        super().__init__(kwargs)


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
