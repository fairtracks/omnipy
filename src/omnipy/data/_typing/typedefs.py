"""Private helper type variables used by typing support modules.

Type Aliases:
    _KeyT: Hashable key type for typed dictionary-like content.
    _ValT: Primary value type parameter.
    _ValT2: Secondary value type parameter for tuple helpers.
"""

from typing import Hashable

from typing_extensions import TypeVar

_KeyT = TypeVar('_KeyT', bound=Hashable)
_ValT = TypeVar('_ValT')
_ValT2 = TypeVar('_ValT2')
