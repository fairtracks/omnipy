from typing import Callable, Protocol, runtime_checkable, TypeVar

from omnipy.api.typedefs import DecoratorClassT

_ObjT = TypeVar('_ObjT', bound=object)
_ObjContraT = TypeVar('_ObjContraT', contravariant=True, bound=object)
_AnyKeyT = TypeVar('_AnyKeyT', contravariant=True, bound=object)
_ValT = TypeVar('_ValT', bound=object)
_ContentsT = TypeVar("_ContentsT", bound=object)
_ContentCovT = TypeVar("_ContentCovT", covariant=True, bound=object)
_ContentContraT = TypeVar("_ContentContraT", contravariant=True, bound=object)
_HasContentsT = TypeVar('_HasContentsT', bound='HasContents')


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


@runtime_checkable
class HasContents(Protocol[_ContentsT]):
    @property
    def contents(self) -> _ContentsT:
        ...

    @contents.setter
    def contents(self, value: _ContentsT) -> None:
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


class IsSnapshotWrapper(Protocol[_ObjContraT, _ContentsT]):
    id: int
    snapshot: _ContentsT

    def taken_of_same_obj(self, obj: _ObjContraT) -> bool:
        ...

    def differs_from(self, obj: _ObjContraT) -> bool:
        ...


class IsSnapshotHolder(IsWeakKeyRefContainer[_HasContentsT,
                                             IsSnapshotWrapper[_HasContentsT, _ContentsT]],
                       Protocol[_HasContentsT, _ContentsT]):
    """"""
    def schedule_for_deletion(self, key: int) -> None:
        ...

    def delete_scheduled(self) -> None:
        ...

    def clear(self) -> None:
        ...

    def take_snapshot_setup(self) -> None:
        ...

    def take_snapshot_cleanup(self) -> None:
        ...

    def take_snapshot(self, obj: _HasContentsT) -> None:
        ...

    #
    # def recursively_remove_deleted_obj_from_deepcopy_memo(self, key: int) -> None:
    #     ...
