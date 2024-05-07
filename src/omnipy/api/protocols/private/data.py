from typing import Protocol

from omnipy.api.protocols.public.config import IsDataConfig


class IsDataConfigHolder(Protocol):
    @property
    def config(self) -> IsDataConfig | None:
        ...

    def set_config(self, config: IsDataConfig) -> None:
        ...


class IsDataClassCreator(IsDataConfigHolder, Protocol):
    ...
