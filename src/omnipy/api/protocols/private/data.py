from typing import Protocol

from omnipy.api.protocols.private.util import IsSnapshotHolder
from omnipy.api.protocols.public.config import IsDataConfig


class IsDataClassCreator(Protocol):
    """"""
    @property
    def config(self) -> IsDataConfig:
        ...

    def set_config(self, config: IsDataConfig) -> None:
        ...

    @property
    def snapshot_holder(self) -> IsSnapshotHolder:
        ...


class IsDataClassBase(Protocol):
    """"""
    @property
    def _data_class_creator(self) -> IsDataClassCreator:
        ...

    @property
    def config(self) -> IsDataConfig:
        ...
