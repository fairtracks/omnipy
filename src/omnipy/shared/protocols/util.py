from typing import Callable, Protocol, runtime_checkable

from typing_extensions import TypeVar

from omnipy.shared.protocols._util import IsWeakKeyRefContainer
from omnipy.util.setdeque import SetDeque

_ContentsT = TypeVar('_ContentsT', bound=object)
_ObjContraT = TypeVar('_ObjContraT', contravariant=True, bound=object)
_HasContentsT = TypeVar('_HasContentsT', bound='HasContents')


class IsDataPublisher(Protocol):
    def subscribe_attr(self, attr_name: str, callback_fun: Callable[..., None]):
        ...

    def subscribe(self, callback_fun: Callable[..., None], do_callback: bool = True) -> None:
        ...

    def unsubscribe_all(self) -> None:
        ...


@runtime_checkable
class HasContents(Protocol[_ContentsT]):
    @property
    def contents(self) -> _ContentsT:
        ...

    @contents.setter
    def contents(self, value: _ContentsT) -> None:
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
