"""Ordered unique queue utilities.

This module provides ``SetDeque``, a deque-backed data structure that preserves
insertion order like ``collections.deque`` while enforcing set-like uniqueness.
It is useful for work queues, caches, and registration lists where membership
checks must be fast and duplicates should be ignored instead of accumulated.
"""

from collections import deque
from copy import copy
import inspect
import sys
from types import NotImplementedType
from typing import cast, Generic, get_args, Iterable, SupportsIndex, TypeVar

_ObjT = TypeVar('_ObjT', bound=object)


class SetDeque(deque, Generic[_ObjT]):
    """Deque variant that keeps each element at most once.

    ``SetDeque`` combines the ordered, append/pop-friendly behavior of
    ``collections.deque`` with an internal set for ``O(1)`` membership tests.
    Duplicate insertions are ignored, existing order is preserved, and explicit
    removals keep the deque and set views synchronized.

    Args:
        iterable: Initial values. Later duplicates are discarded while keeping the
            first occurrence.
        maxlen: Optional deque length limit passed through to ``deque``.

    Notes:
        When ``maxlen`` causes ``deque`` to evict elements during appends, this
        implementation does not proactively remove evicted values from the backing
        set. Use this type primarily without ``maxlen`` unless that edge case is
        acceptable for the calling code.
    """
    def __init__(self, iterable: Iterable = (), maxlen: int | None = None):
        unique_ordered_els = dict.fromkeys(iterable).keys()
        super().__init__(iterable=unique_ordered_els, maxlen=maxlen)
        self._set: set[_ObjT] = set(self.__iter__())

    def _add_element(self, method_name: str, *args: object, el: _ObjT) -> bool:
        if el not in self._set:
            getattr(super(), method_name)(*args, el)
            self._set.add(el)
            return True
        return False

    def _add_elements(self, method_name: str, el_iter: Iterable[_ObjT]) -> None:
        unique_ordered_els = dict.fromkeys(el_iter).keys()
        new_unique_ordered_els = (el for el in unique_ordered_els if el not in self._set)
        getattr(super(), method_name)(new_unique_ordered_els)
        self._set |= unique_ordered_els

    def _remove_returned_element(self, method_name: str) -> _ObjT:
        el = getattr(super(), method_name)()
        self._set.remove(el)
        return el

    def _remove_explicit_element(self,
                                 method_name: str,
                                 *args: object,
                                 el: _ObjT,
                                 add_el_to_args: bool) -> None:
        if add_el_to_args:
            args = args + (el,)
        getattr(super(), method_name)(*args)
        self._set.remove(el)

    def append(self, el: _ObjT) -> None:
        """Append ``el`` to the right side if it is not already present."""
        self._add_element('append', el=el)

    def appendleft(self, el: _ObjT) -> None:
        """Append ``el`` to the left side if it is not already present."""
        self._add_element('appendleft', el=el)

    def extend(self, el_iter: Iterable[_ObjT]) -> None:
        """Append each new unique element from ``el_iter`` to the right side."""
        self._add_elements('extend', el_iter)

    def extendleft(self, el_iter: Iterable[_ObjT]) -> None:
        """Append each new unique element from ``el_iter`` to the left side."""
        self._add_elements('extendleft', el_iter)

    def insert(self, __i: int, __x: _ObjT) -> None:
        """Insert ``__x`` at ``__i`` when it is not already present."""
        self._add_element('insert', __i, el=__x)

    def pop(self) -> _ObjT:  # type: ignore[override]
        """Remove and return the rightmost element."""
        return self._remove_returned_element('pop')

    def popleft(self) -> _ObjT:
        """Remove and return the leftmost element."""
        return self._remove_returned_element('popleft')

    def remove(self, __value) -> None:
        """Remove ``__value`` from both the deque order and membership set."""
        self._remove_explicit_element('remove', el=__value, add_el_to_args=True)

    def clear(self) -> None:
        """Remove all elements and reset the backing membership set."""
        super().clear()
        self._set.clear()

    def count(self, __x: _ObjT) -> int:
        """Return ``1`` when ``__x`` is present, otherwise ``0``."""
        return 1 if __x in self._set else 0

    def __setitem__(self, __key: SupportsIndex, __value: _ObjT) -> None:  # type: ignore[override]
        old_val = super().__getitem__(__key)
        if __value != old_val:
            added = self._add_element('__setitem__', __key, el=__value)
            if added:
                self._set.remove(old_val)

    def __delitem__(self, __key: SupportsIndex) -> None:  # type: ignore[override]
        self._remove_explicit_element(
            '__delitem__',
            __key,
            el=super().__getitem__(__key),
            add_el_to_args=False,
        )

    def __add__(self, __value: 'SetDeque[_ObjT]') -> 'SetDeque[_ObjT] | NotImplementedType':
        if not isinstance(__value, SetDeque):
            return NotImplemented
        self_copy = copy(self)
        self_copy.extend(__value)
        return self_copy

    def __iadd__(self, __value: Iterable[_ObjT]):  # type: ignore[misc]
        self.extend(__value)
        return self

    def __eq__(self, __value: object):
        return super().__eq__(__value) and self._set == cast(SetDeque[_ObjT], __value)._set

    def __reduce__(self):
        ret = super().__reduce__()
        return ret[0], ret[1], None, ret[3]

    def __contains__(self, __key: object) -> bool:
        return self._set.__contains__(__key)

    def _common_mul(self, __value: int):
        if __value > 0:
            return SetDeque[_ObjT](self.__iter__())
        else:
            return SetDeque[_ObjT]()

    def __mul__(self, __value: int):
        return self._common_mul(__value)

    def __rmul__(self, __value: int):
        return self._common_mul(__value)

    def __imul__(self, __value: int):
        if __value <= 0:
            self.clear()
        return self

    def __repr__(self):
        arg_repr = ''
        if hasattr(self, '__orig_class__'):
            args = get_args(self.__orig_class__)  # pyright: ignore [reportAttributeAccessIssue]
            if len(args) == 1:
                arg = args[0]
                arg_repr = f'[{arg.__name__ if inspect.isclass(arg) else repr(arg)}]'
        maxlen_repr = f', maxlen={self.maxlen}' if self.maxlen is not None else ''
        return f'{self.__class__.__name__}{arg_repr}({list(self)}{maxlen_repr})'

    def __sizeof__(self):
        return super().__sizeof__() + sys.getsizeof(self._set)
