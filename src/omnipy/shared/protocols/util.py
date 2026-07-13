"""Utility protocols shared across Omnipy runtime and configuration code."""

from typing import Any, Callable, ClassVar, Protocol

from typing_extensions import Self


class IsDataPublisher(Protocol):
    """Protocol for objects that publish change notifications to subscribers."""
    def subscribe_attr(self, attr_name: str, callback_fun: Callable[..., None]):
        """Subscribe to updates for one named attribute.

        Args:
            attr_name: Name of the published attribute to observe.
            callback_fun: Callback invoked when that attribute changes.
        """
        ...

    def subscribe(self, callback_fun: Callable[..., None], do_callback: bool = True) -> None:
        """Subscribe to general publisher updates.

        Args:
            callback_fun: Callback invoked when the publisher changes.
            do_callback: Whether to invoke the callback immediately after subscribing.
        """
        ...

    def unsubscribe_all(self) -> None:
        """Remove every registered subscriber."""
        ...

    def deepcopy(self) -> Self:
        """Return a deep-copied publisher instance.

        Returns:
            Self: Deep copy of the current publisher object.
        """
        ...


class IsDataclass(Protocol):
    """Protocol for objects that expose the standard dataclass marker fields."""

    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[dict[str, Any]]
