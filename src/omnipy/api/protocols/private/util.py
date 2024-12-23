from types import TracebackType
from typing import Callable, Protocol, runtime_checkable

from typing_extensions import TypeVar

from omnipy.util.setdeque import SetDeque

_ObjContraT = TypeVar('_ObjContraT', contravariant=True, bound=object)
_AnyKeyT = TypeVar('_AnyKeyT', contravariant=True, bound=object)
_ValT = TypeVar('_ValT', bound=object)
_ContentsT = TypeVar('_ContentsT', bound=object)
_HasContentsT = TypeVar('_HasContentsT', bound='HasContents')


class IsDataPublisher(Protocol):
    def subscribe_attr(self, attr_name: str, callback_fun: Callable[..., None]):
        ...

    def subscribe(self, callback_fun: Callable[..., None], do_callback: bool = True) -> None:
        ...

    def unsubscribe_all(self) -> None:
        ...


@runtime_checkable
class IsCallableParamAfterSelf(Protocol):
    """"""
    def __call__(self, callable_arg: Callable, /, *args: object, **kwargs: object) -> None:
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
    def clear(self) -> None:
        ...

    def all_are_empty(self, debug: bool = False) -> bool:
        ...

    def get_deepcopy_content_ids(self) -> SetDeque[int]:
        ...

    def get_deepcopy_content_ids_scheduled_for_deletion(self) -> SetDeque[int]:
        ...

    def schedule_deepcopy_content_ids_for_deletion(self, *keys: int) -> None:
        ...

    def delete_scheduled_deepcopy_content_ids(self) -> None:
        ...

    def take_snapshot_setup(self) -> None:
        ...

    def take_snapshot_teardown(self) -> None:
        ...

    def take_snapshot(self, obj: _HasContentsT) -> None:
        ...


class IsRateLimitingClientSession(Protocol):
    """"""
    @property
    def requests_per_second(self) -> float:
        ...

    async def __aenter__(self) -> 'IsRateLimitingClientSession':
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        ...

    async def close(self) -> None:
        ...
