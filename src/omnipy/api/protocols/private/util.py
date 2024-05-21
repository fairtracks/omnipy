from typing import Callable, Protocol, runtime_checkable, TypeVar

from omnipy.api.typedefs import DecoratorClassT

_ObjT = TypeVar('_ObjT', bound=object)
_ObjContraT = TypeVar('_ObjContraT', contravariant=True, bound=object)
_AnyKeyT = TypeVar('_AnyKeyT', contravariant=True, bound=object)
_ValT = TypeVar('_ValT', bound=object)
_ContentT = TypeVar("_ContentT", bound=object)
_ContentCovT = TypeVar("_ContentCovT", covariant=True, bound=object)
_ContentContraT = TypeVar("_ContentContraT", contravariant=True, bound=object)


@runtime_checkable
class IsCallableParamAfterSelf(Protocol):
    """"""
    def __call__(self, callable_arg: Callable, /, *args: object, **kwargs: object) -> None:
        ...


@runtime_checkable
class IsCallableClass(Protocol[DecoratorClassT]):
    """"""
    def __call__(self, *args: object, **kwargs: object) -> Callable[[Callable], DecoratorClassT]:
        ...


class HasContents(Protocol[_ContentCovT]):
    @property
    def contents(self) -> _ContentCovT:
        ...


class IsWeakKeyRefContainer(Protocol[_AnyKeyT, _ValT]):
    def __contains__(self, key: _AnyKeyT) -> bool:
        ...

    def get(self, key: _AnyKeyT) -> _ValT | None:
        ...

    def __getitem__(self, key: _AnyKeyT) -> _ValT:
        ...

    def __setitem__(self, key: _AnyKeyT, value: _ValT) -> None:
        ...

    def __len__(self) -> int:
        ...


class IsSnapshot(Protocol[_ObjContraT, _ContentT]):
    id: int
    obj_copy: _ContentT

    def taken_of_same_obj(self, obj: _ObjContraT) -> bool:
        ...

    def differs_from(self, obj: _ContentT) -> bool:
        ...


class IsSnapshotHolder(IsWeakKeyRefContainer[HasContents[_ContentT], IsSnapshot[_ObjT, _ContentT]],
                       Protocol[_ObjT, _ContentT]):
    """"""
    def take_snapshot(self, obj: HasContents[_ContentT]) -> None:
        ...

    def recursively_remove_deleted_obj_from_deepcopy_memo(self, key: int) -> None:
        ...