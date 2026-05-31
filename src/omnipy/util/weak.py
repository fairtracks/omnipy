"""Weak-reference containers keyed by object identity.

This module provides helpers for storing values against live objects without
keeping those keys alive, while still performing lookups by object identity.
"""

from typing import Generic
from weakref import WeakKeyDictionary, WeakValueDictionary

from typing_extensions import TypeVar

_AnyKeyT = TypeVar('_AnyKeyT', bound=object)
_ValT = TypeVar('_ValT', bound=object)


class KeyRef(list):
    """Identity-based weak-dictionary key wrapper.

    Args:
        obj: Object whose identity should be used as the key value.
    """

    def __init__(self, obj: object) -> None:
        super().__init__([id(obj)])

    def __hash__(self) -> int:  # type: ignore[override]
        return self[0]


class WeakKeyRefContainer(Generic[_AnyKeyT, _ValT]):
    """Map live objects to values without keeping the keys alive.

    The container stores a weak reference to each original key object and uses a
    stable identity wrapper so callers can retrieve values with the original
    object instance while automatic cleanup still works when keys are collected.
    """

    def __init__(self) -> None:
        self._key_dict: WeakValueDictionary[KeyRef, _AnyKeyT] = WeakValueDictionary()
        self._value_dict: WeakKeyDictionary[KeyRef, _ValT] = WeakKeyDictionary()

    def __contains__(self, key: _AnyKeyT) -> bool:
        return KeyRef(key) in self._value_dict

    def get(self, key: _AnyKeyT) -> _ValT | None:
        key_ref = KeyRef(key)
        if key_ref in self._value_dict:
            return self._value_dict[key_ref]
        else:
            return None

    def __getitem__(self, key: _AnyKeyT) -> _ValT:
        key_ref = KeyRef(key)
        if key_ref in self._value_dict:
            return self._value_dict[key_ref]
        else:
            raise KeyError(f'{key} is not in {self.__class__.__name__}')

    def __setitem__(self, key: _AnyKeyT, value: _ValT) -> None:
        key_ref = KeyRef(key)
        self._key_dict[key_ref] = key
        self._value_dict[key_ref] = value

    def __len__(self) -> int:
        return len(self._value_dict)

    def clear(self) -> None:
        self._key_dict.clear()
        self._value_dict.clear()
