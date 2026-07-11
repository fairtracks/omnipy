"""Protocol extensions for standard-library style container behavior."""

from collections.abc import Iterator
from typing import overload, Protocol, runtime_checkable, SupportsIndex

from typing_extensions import TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException

_ItemCovT = TypeVar('_ItemCovT', covariant=True)


@runtime_checkable
class IsItemSequenceLike(Protocol[_ItemCovT]):
    """Minimal sequence-like protocol for item containers.

    This protocol models indexable and sized containers with membership checks,
    useful for array/dataframe-style structures that don't implement the full
    sequence interface.
    """
    @overload
    def __getitem__(self, index: SupportsIndex, /) -> _ItemCovT:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, index: slice, /) -> 'IsItemSequenceLike[_ItemCovT]':
        raise AssumedToBeImplementedException

    def __getitem__(self, index: SupportsIndex | slice,
                    /) -> _ItemCovT | 'IsItemSequenceLike[_ItemCovT]':
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __contains__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_ItemCovT]:
        raise AssumedToBeImplementedException
