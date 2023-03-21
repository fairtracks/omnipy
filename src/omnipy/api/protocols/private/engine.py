from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable, Type

from omnipy.api.protocols.private.log import IsRunStateRegistry


@runtime_checkable
class IsEngine(Protocol):
    """"""
    def __init__(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsEngineConfig]:
        ...

    def set_config(self, config: IsEngineConfig) -> None:
        ...

    def set_registry(self, registry: Optional[IsRunStateRegistry]) -> None:
        ...


class IsEngineConfig(Protocol):
    """"""
    ...
