from math import nan
from typing import Generic, Iterator, overload, SupportsIndex

from typing_extensions import Self, TypeVar

from omnipy import ColumnModel, ColumnWiseTableWithColNamesModel
from omnipy.components.tables.models import ConcatByAddArrayAdapterModel

T = TypeVar('T')


class ListLikeNoAdd(Generic[T]):
    def __init__(self, items: list[T] | None = None):
        if items is None:
            items = []

        self._list = items

    def copy(self) -> 'ListLikeNoAdd':
        return ListLikeNoAdd(self._list.copy())

    def extend(self, other: 'ListLikeNoAdd'):
        self._list.extend(other._list)

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> T:
        return self._list[index]

    @overload
    def __getitem__(self, index: slice, /) -> list[T]:
        return self._list[index]

    def __getitem__(self, index: SupportsIndex | slice, /) -> T | list[T]:
        return self._list[index]

    def __len__(self) -> int:
        return len(self._list)

    def __contains__(self, value: object, /) -> bool:
        return value in self._list

    def __iter__(self) -> Iterator[T]:
        return iter(self._list)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ListLikeNoAdd):
            return self._list == other._list
        return False

    def __repr__(self) -> str:
        return f'ConcatLackingList({self._list})'


def _list_like_no_add_concat_function(
    left: ListLikeNoAdd[T],
    right: ListLikeNoAdd[T],
) -> ListLikeNoAdd[T]:
    assert isinstance(left, ListLikeNoAdd) and isinstance(right, ListLikeNoAdd)
    concat_list = left.copy()
    concat_list.extend(right)
    return concat_list


class ListLikeAdapterModel(ConcatByAddArrayAdapterModel[ListLikeNoAdd, T], Generic[T]):
    @classmethod
    def _concat_column_values(
        cls,
        left: ListLikeNoAdd[T],
        right: ListLikeNoAdd[T],
    ) -> ListLikeNoAdd[T]:
        return _list_like_no_add_concat_function(left, right)


class IntListLikeColumnModel(ColumnModel[ListLikeAdapterModel[int], int]):
    @classmethod
    def default_value(cls) -> int:
        return 0

    @classmethod
    def filled(cls, value: int, length: int) -> Self:
        return cls(ListLikeNoAdd([value] * length))


class FloatListLikeColumnModel(ColumnModel[ListLikeAdapterModel[float], float]):
    @classmethod
    def default_value(cls) -> float:
        return nan


class IntListLikeColumnWiseTableWithColNamesModel(ColumnWiseTableWithColNamesModel[
        IntListLikeColumnModel,
        int,
]):
    ...


class FloatListLikeColumnWiseTableWithColNamesModel(ColumnWiseTableWithColNamesModel[
        FloatListLikeColumnModel,
        float,
]):
    ...
