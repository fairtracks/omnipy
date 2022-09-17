from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, DefaultDict, Dict, List


def _subscribers_factory():
    return defaultdict(list)


@dataclass
class ConfigPublisher:
    _subscribers: DefaultDict[str, List[Callable[[Any], None]]] = \
        field(default_factory=_subscribers_factory, init=False, repr=False)

    def subscribe(self, config_item: str, callback_fun: Callable[[Any], None]):
        self._subscribers[config_item].append(callback_fun)
        callback_fun(getattr(self, config_item))

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if not key.startswith('_'):
            if key in self._subscribers:
                for callback_fun in self._subscribers[key]:
                    callback_fun(value)
