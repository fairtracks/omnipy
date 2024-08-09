from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, DefaultDict

from omnipy.api.protocols.public.hub import IsRuntime


def _subscribers_factory():
    return defaultdict(list)


@dataclass
class DataPublisher:
    _subscriptions: DefaultDict[str, list[Callable[[Any], None]]] = \
        field(default_factory=_subscribers_factory, init=False, repr=False)

    def subscribe(self, config_item: str, callback_fun: Callable[[Any], None]):
        if not hasattr(self, config_item):
            raise AttributeError(f'No config items named "{config_item}"')
        elif config_item.startswith('_'):
            raise AttributeError(f'Subscribing to private member "{config_item}" not allowed')
        else:
            self._subscriptions[config_item].append(callback_fun)
            callback_fun(getattr(self, config_item))

    def unsubscribe_all(self) -> None:
        self._subscriptions = _subscribers_factory()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if key in self._subscriptions:
            for callback_fun in self._subscriptions[key]:
                callback_fun(value)


@dataclass
class RuntimeEntryPublisher(DataPublisher):
    _back: IsRuntime | None = field(default=None, init=False, repr=False)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if hasattr(self, key) and not key.startswith('_') and self._back is not None:
            self._back.reset_subscriptions()
