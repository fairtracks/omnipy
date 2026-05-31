"""Observable Pydantic models for propagating attribute change notifications.

This module provides publisher models that notify subscribers when their public
attributes change, including nested publisher attributes used in runtime and
configuration state.
"""

from collections import defaultdict
from typing import Callable, DefaultDict

from typing_extensions import Self

from omnipy.shared.protocols.hub.runtime import IsRuntime
import omnipy.util.pydantic as pyd


def _subscribers_factory():
    """Create the default subscription mapping for publisher instances.

    Args:
        None.

    Returns:
        A ``defaultdict(list)`` keyed by attribute name where each value is a
        list of subscriber callbacks.

    Raises:
        None.

    Example:
        >>> subs = _subscribers_factory()
        >>> type(subs).__name__
        'defaultdict'
    """
    return defaultdict(list)


class DataPublisher(pyd.BaseModel):
    """Pydantic model that publishes updates to subscribers.

    Subscribers can watch a single public attribute or the whole model. Nested
    ``DataPublisher`` attributes propagate their changes to parent subscribers.

    Args:
        **data: Field values accepted by the concrete publisher model.

    Returns:
        A configured publisher instance.

    Raises:
        pyd.ValidationError: If provided field values fail model validation.

    Example:
        >>> class DemoPublisher(DataPublisher):
        ...     value: int = 0
        >>> demo = DemoPublisher(value=1)
        >>> demo.value
        1
    """
    class Config:
        """Pydantic settings for ``DataPublisher`` models.

        Args:
            None.

        Returns:
            None. This class defines configuration attributes consumed by
            Pydantic during model construction.

        Raises:
            None.

        Example:
            ``validate_assignment = True`` ensures subscribers are triggered after
            validated attribute updates.
        """
        arbitrary_types_allowed = True
        validate_assignment = True

    _self_subscriptions: list[Callable[..., None]] = pyd.PrivateAttr(default_factory=list)
    _attr_subscriptions: DefaultDict[str, list[Callable[..., None]]] = \
        pyd.PrivateAttr(default_factory=_subscribers_factory)

    def subscribe_attr(self, attr_name: str, callback_fun: Callable[..., None]):
        """Subscribe to updates for one public attribute.

        The callback is invoked immediately with the current attribute value.

        Args:
            attr_name: Public attribute name to observe.
            callback_fun: Callback receiving the current/new attribute value.

        Returns:
            None.

        Raises:
            AttributeError: If ``attr_name`` does not exist or is private.

        Example:
            >>> class DemoPublisher(DataPublisher):
            ...     value: int = 0
            >>> values = []
            >>> demo = DemoPublisher()
            >>> demo.subscribe_attr('value', values.append)
            >>> values[-1]
            0
        """
        if not hasattr(self, attr_name):
            raise AttributeError(f'No attribute named "{attr_name}"')
        elif attr_name.startswith('_'):
            raise AttributeError(f'Subscribing to private member "{attr_name}" not allowed')
        else:
            self._attr_subscriptions[attr_name].append(callback_fun)
            attr = getattr(self, attr_name)
            callback_fun(attr)

            if isinstance(attr, DataPublisher):
                attr.subscribe(callback_fun, do_callback=False)

    def subscribe(self, callback_fun: Callable[..., None], do_callback: bool = True) -> None:
        """Subscribe to updates for the full publisher object.

        The callback receives ``self`` whenever any public attribute changes.

        Args:
            callback_fun: Callback receiving the publisher instance.
            do_callback: When ``True``, call the callback immediately after
                registration.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> class DemoPublisher(DataPublisher):
            ...     value: int = 0
            >>> updates = []
            >>> demo = DemoPublisher()
            >>> demo.subscribe(lambda obj: updates.append(obj.value))
            >>> updates[-1]
            0
        """
        self._self_subscriptions.append(callback_fun)

        def _get_attr_callback_for_publisher_child(
                attr_name: str) -> Callable[[DataPublisher], None]:
            """Build a child-publisher callback forwarding updates to parent subscribers.

            Args:
                attr_name: Child attribute name for which the callback is created.

            Returns:
                A callback that triggers ``callback_fun(self)`` when the child
                publisher emits an update.

            Raises:
                None.

            Example:
                Constructed internally while registering nested
                ``DataPublisher`` attributes.
            """
            def _attr_callback_for_publisher_child(value: object) -> None:
                """Forward child updates as parent-object updates.

                Args:
                    value: Updated child value (unused by the forwarding logic).

                Returns:
                    None.

                Raises:
                    None.

                Example:
                    Called by nested publishers to notify parent subscribers.
                """
                callback_fun(self)

            return _attr_callback_for_publisher_child

        for attr_name in self.__class__.__fields__.keys():
            if not attr_name.startswith('_'):
                attr = getattr(self, attr_name)
                if isinstance(attr, DataPublisher):
                    attr.subscribe(
                        _get_attr_callback_for_publisher_child(attr_name), do_callback=False)

        if do_callback:
            callback_fun(self)

    def unsubscribe_all(self) -> None:
        """Remove all subscriptions from this publisher and nested publishers.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> class DemoPublisher(DataPublisher):
            ...     value: int = 0
            >>> demo = DemoPublisher()
            >>> demo.subscribe(lambda obj: None)
            >>> demo.unsubscribe_all()
        """
        self._self_subscriptions.clear()
        self._attr_subscriptions.clear()

        for attr_name in self.__class__.__fields__.keys():
            if not attr_name.startswith('_'):
                attr = getattr(self, attr_name)
                if isinstance(attr, DataPublisher):
                    attr.unsubscribe_all()

    def _call_subscribers(self, attr_name: str, value: object) -> None:
        """Notify callbacks subscribed to a specific attribute.

        Args:
            attr_name: Name of the changed attribute.
            value: New value assigned to the attribute.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> class DemoPublisher(DataPublisher):
            ...     value: int = 0
            >>> demo = DemoPublisher()
            >>> demo._call_subscribers('value', 1)
        """
        if attr_name in self._attr_subscriptions:
            for callback_fun in self._attr_subscriptions[attr_name]:
                callback_fun(value)

    def _call_self_subscribers(self) -> None:
        """Notify callbacks subscribed to whole-object updates.

        Args:
            None.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> class DemoPublisher(DataPublisher):
            ...     value: int = 0
            >>> demo = DemoPublisher()
            >>> demo._call_self_subscribers()
        """
        for callback_fun in self._self_subscriptions:
            callback_fun(self)

    def _call_all_subscribers(self, attr_name: str, value: object) -> None:
        """Notify both attribute-specific and model-wide subscribers.

        Args:
            attr_name: Name of the changed attribute.
            value: New value assigned to the attribute.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> class DemoPublisher(DataPublisher):
            ...     value: int = 0
            >>> demo = DemoPublisher()
            >>> demo._call_all_subscribers('value', 1)
        """
        self._call_subscribers(attr_name, value)
        self._call_self_subscribers()

    def __setattr__(self, attr_name: str, value: object) -> None:
        """Assign an attribute and publish notifications for public fields.

        Args:
            attr_name: Attribute name being assigned.
            value: New value to store.

        Returns:
            None.

        Raises:
            Exception: Propagates any validation or assignment errors from
                ``pyd.BaseModel.__setattr__``.

        Example:
            >>> class DemoPublisher(DataPublisher):
            ...     value: int = 0
            >>> demo = DemoPublisher()
            >>> demo.value = 2
            >>> demo.value
            2
        """
        super().__setattr__(attr_name, value)

        if not attr_name.startswith('_'):
            self._call_all_subscribers(attr_name, value)

    def deepcopy(self) -> Self:
        """Create a deep copy with subscriptions reset on the copied object.

        Args:
            None.

        Returns:
            A deep-copied publisher with empty subscription registries.

        Raises:
            None.

        Example:
            >>> class DemoPublisher(DataPublisher):
            ...     value: int = 0
            >>> demo = DemoPublisher()
            >>> clone = demo.deepcopy()
            >>> clone is demo
            False
        """
        self_copy = self.copy()
        self_copy._self_subscriptions = []
        self_copy._attr_subscriptions = _subscribers_factory()
        return self_copy.copy(deep=True)


class RuntimeEntryPublisher(DataPublisher):
    """Data publisher that resets runtime subscriptions on value replacement.

    When a public attribute is rebound to a different object and a runtime
    backend is attached, the runtime subscription graph is rebuilt.

    Args:
        **data: Field values accepted by the concrete runtime entry model.

    Returns:
        A runtime-aware publisher instance.

    Raises:
        pyd.ValidationError: If provided field values fail model validation.

    Example:
        >>> class DemoRuntimeEntry(RuntimeEntryPublisher):
        ...     value: int = 0
        >>> entry = DemoRuntimeEntry()
        >>> entry.value
        0
    """

    _back: IsRuntime | None = pyd.PrivateAttr(default=None)

    def __setattr__(self, attr_name: str, value: object) -> None:
        """Assign an attribute and reset runtime subscriptions when rebinding.

        Args:
            attr_name: Attribute name being assigned.
            value: New value to store.

        Returns:
            None.

        Raises:
            Exception: Propagates assignment or validation errors from parent
                ``__setattr__`` implementations.

        Example:
            >>> class DemoRuntimeEntry(RuntimeEntryPublisher):
            ...     value: int = 0
            >>> entry = DemoRuntimeEntry()
            >>> entry.value = 3
            >>> entry.value
            3
        """
        new_value = hasattr(self, attr_name) and getattr(self, attr_name) is not value

        super().__setattr__(attr_name, value)

        if new_value and not attr_name.startswith('_') and self._back is not None:
            self._back.reset_subscriptions()
