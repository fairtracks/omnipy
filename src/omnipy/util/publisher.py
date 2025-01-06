from collections import defaultdict
from typing import Callable, DefaultDict

from omnipy.shared.protocols.hub.runtime import IsRuntime
import omnipy.util._pydantic as pyd


def _subscribers_factory():
    return defaultdict(list)


class DataPublisher(pyd.BaseModel):
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    _self_subscriptions: list[Callable[..., None]] = pyd.PrivateAttr(default_factory=list)
    _attr_subscriptions: DefaultDict[str, list[Callable[..., None]]] = \
        pyd.PrivateAttr(default_factory=_subscribers_factory)

    def subscribe_attr(self, attr_name: str, callback_fun: Callable[..., None]):
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
        self._self_subscriptions.append(callback_fun)

        def _get_attr_callback_for_publisher_child(
                attr_name: str) -> Callable[[DataPublisher], None]:
            def _attr_callback_for_publisher_child(value: object) -> None:
                self._call_all_subscribers(attr_name, value)

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
        self._self_subscriptions.clear()
        self._attr_subscriptions.clear()

    def _call_subscribers(self, attr_name: str, value: object) -> None:
        if attr_name in self._attr_subscriptions:
            for callback_fun in self._attr_subscriptions[attr_name]:
                callback_fun(value)

    def _call_self_subscribers(self) -> None:
        for callback_fun in self._self_subscriptions:
            callback_fun(self)

    def _call_all_subscribers(self, attr_name: str, value: object) -> None:
        self._call_subscribers(attr_name, value)
        self._call_self_subscribers()

    def __setattr__(self, attr_name: str, value: object) -> None:
        super().__setattr__(attr_name, value)

        if not attr_name.startswith('_'):
            self._call_all_subscribers(attr_name, value)


class RuntimeEntryPublisher(DataPublisher):
    _back: IsRuntime | None = pyd.PrivateAttr(default=None)

    def __setattr__(self, attr_name: str, value: object) -> None:
        new_value = hasattr(self, attr_name) and getattr(self, attr_name) is not value

        super().__setattr__(attr_name, value)

        if new_value and not attr_name.startswith('_') and self._back is not None:
            self._back.reset_subscriptions()
