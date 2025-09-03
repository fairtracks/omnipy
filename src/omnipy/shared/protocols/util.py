from typing import Any, Callable, ClassVar, Protocol

from typing_extensions import Self


class IsDataPublisher(Protocol):
    def subscribe_attr(self, attr_name: str, callback_fun: Callable[..., None]):
        ...

    def subscribe(self, callback_fun: Callable[..., None], do_callback: bool = True) -> None:
        ...

    def unsubscribe_all(self) -> None:
        ...

    def deepcopy(self) -> Self:
        ...


class IsDataclass(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[dict[str, Any]]
