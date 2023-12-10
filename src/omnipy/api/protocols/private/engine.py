from typing import Protocol, runtime_checkable, Type

from omnipy.api.protocols.private.log import IsRunStateRegistry
from omnipy.api.protocols.public.config import IsEngineConfig


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

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        ...
