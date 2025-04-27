from typing import Callable, Protocol


class IsDataPublisher(Protocol):
    def subscribe_attr(self, attr_name: str, callback_fun: Callable[..., None]):
        ...

    def subscribe(self, callback_fun: Callable[..., None], do_callback: bool = True) -> None:
        ...

    def unsubscribe_all(self) -> None:
        ...
