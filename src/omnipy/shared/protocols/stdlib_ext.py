from collections.abc import Iterator
from typing import overload, Protocol, runtime_checkable, SupportsIndex

from typing_extensions import TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException

_T_co = TypeVar('_T_co', covariant=True)


@runtime_checkable
class IsItemSequenceLike(Protocol[_T_co]):
    """Minimal sequence-like protocol for item containers.

    This protocol models indexable and sized containers with membership checks,
    useful for array/dataframe-style structures that don't implement the full
    sequence interface.
    """
    @overload
    def __getitem__(self, index: SupportsIndex, /) -> _T_co:
        raise AssumedToBeImplementedException

    @overload
    def __getitem__(self, index: slice, /) -> 'IsItemSequenceLike[_T_co]':
        raise AssumedToBeImplementedException

    def __getitem__(self, index: SupportsIndex | slice, /) -> _T_co | 'IsItemSequenceLike[_T_co]':
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __contains__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_T_co]:
        raise AssumedToBeImplementedException
