from __future__ import annotations

from typing import Any, Callable, Protocol


class IsDataPublisher(Protocol):
    """"""
    def subscribe(self, config_item: str, callback_fun: Callable[[Any], None]):
        ...

    def unsubscribe_all(self) -> None:
        ...
