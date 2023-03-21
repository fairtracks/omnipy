from __future__ import annotations

from typing import Any, Callable, Optional, Protocol

from omnipy.api.enums import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions
from omnipy.api.protocols.private.engine import IsEngine


class IsDataPublisher(Protocol):
    """"""
    def subscribe(self, config_item: str, callback_fun: Callable[[Any], None]):
        ...

    def unsubscribe_all(self) -> None:
        ...


class IsJobConfigBase(Protocol):
    """"""
    persist_outputs: ConfigPersistOutputsOptions
    restore_outputs: ConfigRestoreOutputsOptions
    persist_data_dir_path: str


class IsJobConfigHolder(Protocol):
    """"""
    @property
    def config(self) -> Optional[IsJobConfigBase]:
        ...

    @property
    def engine(self) -> Optional[IsEngine]:
        ...

    def set_config(self, config: IsJobConfigBase) -> None:
        ...

    def set_engine(self, engine: IsEngine) -> None:
        ...
