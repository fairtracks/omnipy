"""Generator-like annotations, as imported from typing and collections.abc."""

import collections.abc
import typing

GENERATOR_ANNOTATIONS: dict[str, object] = {
    'typing.Generator': typing.Generator,
    'collections.abc.Generator': collections.abc.Generator,
    'typing.AsyncGenerator': typing.AsyncGenerator,
    'collections.abc.AsyncGenerator': collections.abc.AsyncGenerator,
}

ITERATOR_ANNOTATIONS: dict[str, object] = {
    'typing.Iterator': typing.Iterator,
    'collections.abc.Iterator': collections.abc.Iterator,
    'typing.AsyncIterator': typing.AsyncIterator,
    'collections.abc.AsyncIterator': collections.abc.AsyncIterator,
}

GENERATOR_LIKE_ANNOTATIONS: dict[str, object] = {
    **GENERATOR_ANNOTATIONS,
    **ITERATOR_ANNOTATIONS,
}
