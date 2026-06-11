from collections.abc import Iterator
from typing import overload, Protocol, runtime_checkable, SupportsIndex

from typing_extensions import Self, TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException

_ItemT_co = TypeVar('_ItemT_co', covariant=True)


@runtime_checkable
class IsItemSequenceLike(Protocol[_ItemT_co]):
    """Minimal sequence-like protocol for item containers.

    This protocol models indexable and sized containers with membership checks,
    useful for array/dataframe-style structures that don't implement the full
    sequence interface.
    """
    @overload
    def __getitem__(self, index: SupportsIndex, /) -> _ItemT_co:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, index: slice, /) -> 'IsItemSequenceLike[_ItemT_co]':
        raise AssumedToBeImplementedException

    def __getitem__(self, index: SupportsIndex | slice,
                    /) -> _ItemT_co | 'IsItemSequenceLike[_ItemT_co]':
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __contains__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_ItemT_co]:
        raise AssumedToBeImplementedException


class IsConcatenableItemSequenceLike(IsItemSequenceLike[_ItemT_co], Protocol[_ItemT_co]):
    @classmethod
    def default_filled(cls, length: int) -> Self:
        ...

    @classmethod
    def default_value(cls) -> _ItemT_co:
        ...

    def __iter__(self) -> Iterator[_ItemT_co]:
        ...

    def __add__(self, other: object) -> Self:
        ...
