from typing import Callable, ContextManager, Protocol, runtime_checkable, TypeVar

from omnipy.shared.protocols._util import HasContents, IsSnapshotHolder
from omnipy.shared.protocols.config import IsDataConfig

_ObjT = TypeVar('_ObjT', bound=HasContents)
_ContentsT = TypeVar('_ContentsT', bound=object)


@runtime_checkable
class IsDataClassCreator(Protocol[_ObjT, _ContentsT]):
    """"""
    @property
    def config(self) -> IsDataConfig:
        ...

    def set_config(self, config: IsDataConfig) -> None:
        ...

    @property
    def snapshot_holder(self) -> IsSnapshotHolder[_ObjT, _ContentsT]:
        ...

    def deepcopy_context(
        self,
        top_level_entry_func: Callable[[], None],
        top_level_exit_func: Callable[[], None],
    ) -> ContextManager[int]:
        ...


@runtime_checkable
class IsDataClassBase(Protocol):
    """"""
    @property
    def _data_class_creator(self) -> IsDataClassCreator:
        ...

    @property
    def config(self) -> IsDataConfig:
        ...
