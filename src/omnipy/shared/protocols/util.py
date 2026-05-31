"""Utility protocols shared across Omnipy runtime and configuration code."""

from typing import Any, Callable, ClassVar, Protocol

from typing_extensions import Self


class IsDataPublisher(Protocol):
    """Define the ``IsDataPublisher`` interface.
    """
    def subscribe_attr(self, attr_name: str, callback_fun: Callable[..., None]):
        """Subscribe attr.
        
        Args:
            attr_name: (str) Argument passed to ``subscribe_attr()``.
            callback_fun: (Callable[..., None]) Argument passed to ``subscribe_attr()``.
        """
        ...

    def subscribe(self, callback_fun: Callable[..., None], do_callback: bool = True) -> None:
        """Subscribe.
        
        Args:
            callback_fun: (Callable[..., None]) Argument passed to ``subscribe()``.
            do_callback: (bool) Argument passed to ``subscribe()``.
        """
        ...

    def unsubscribe_all(self) -> None:
        """Unsubscribe all.
        """
        ...

    def deepcopy(self) -> Self:
        """Deepcopy.
        
        Returns:
            Self: Result produced by ``deepcopy()``.
        """
        ...


class IsDataclass(Protocol):
    """Define the ``IsDataclass`` interface.
    """

    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[dict[str, Any]]
