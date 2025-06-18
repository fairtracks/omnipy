from typing import Protocol, runtime_checkable, Type

from omnipy.shared.protocols.config import IsJobRunnerConfig
from omnipy.shared.protocols.hub.registry import IsRunStateRegistry


@runtime_checkable
class IsEngine(Protocol):
    """"""
    def __init__(self) -> None:
        ...

    @classmethod
    def get_config_cls(cls) -> Type[IsJobRunnerConfig]:
        ...

    def set_config(self, config: IsJobRunnerConfig) -> None:
        ...

    def set_registry(self, registry: IsRunStateRegistry | None) -> None:
        ...

    @property
    def config(self) -> IsJobRunnerConfig:
        ...

    @property
    def registry(self) -> IsRunStateRegistry | None:
        ...
