from typing import Protocol

from typing_extensions import runtime_checkable, Self, TypeVar

_T_contra = TypeVar('_T_contra', contravariant=True)


@runtime_checkable
class SupportsIAdd(Protocol[_T_contra]):
    def __iadd__(self, x: _T_contra, /) -> Self:
        ...


@runtime_checkable
class SupportsIOr(Protocol[_T_contra]):
    def __ior__(self, x: _T_contra, /) -> Self:
        ...
