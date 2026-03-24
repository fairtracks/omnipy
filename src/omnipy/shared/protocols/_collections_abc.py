# Modified from the "_collections_abc.py.imported" file in the same
# directory, which was imported from the Typeshed
# (https://github.com/python/typeshed).
#
# The Typeshed is licensed under the Apache License, Version 2.0 and the
# MIT License. See the LICENSE file in the root of the repository for
# details (https://github.com/python/typeshed/blob/main/LICENSE).
#
# See "_collections_abc.py.imported" for more details.

from collections.abc import Iterable, Iterator
import sys
from typing import ClassVar, Protocol

from typing_extensions import TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols.types import IsMappingProxyType
from omnipy.shared.protocols.typing import IsItemsView, IsKeysView, IsValuesView

_KT_co = TypeVar('_KT_co', covariant=True)  # Key type covariant containers.
_VT_co = TypeVar('_VT_co', covariant=True)  # Value type covariant containers.


# @final
# class dict_keys(KeysView[_KT_co], Generic[_KT_co, _VT_co]):  # undocumented
class IsDictKeys(IsKeysView[_KT_co], Protocol[_KT_co, _VT_co]):  # type: ignore[misc]
    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __reversed__(self) -> Iterator[_KT_co]:
        raise AssumedToBeImplementedException

    # __hash__: ClassVar[None]  # type: ignore[assignment]
    __hash__: ClassVar[None] = None  # type: ignore[assignment]
    if sys.version_info >= (3, 13):

        def isdisjoint(self, other: Iterable[_KT_co], /) -> bool:
            raise AssumedToBeImplementedException

    if sys.version_info >= (3, 10):

        @property
        # def mapping(self) -> MappingProxyType[_KT_co, _VT_co]:
        def mapping(self) -> IsMappingProxyType[_KT_co, _VT_co]:
            raise AssumedToBeImplementedException


# @final
# class dict_values(ValuesView[_VT_co], Generic[_KT_co, _VT_co]):  # undocumented
class IsDictValues(IsValuesView[_VT_co], Protocol[_KT_co, _VT_co]):  # type: ignore[misc]
    def __reversed__(self) -> Iterator[_VT_co]:
        raise AssumedToBeImplementedException

    if sys.version_info >= (3, 10):

        @property
        # def mapping(self) -> MappingProxyType[_KT_co, _VT_co]:
        def mapping(self) -> IsMappingProxyType[_KT_co, _VT_co]:
            raise AssumedToBeImplementedException


# @final
# class dict_items(ItemsView[_KT_co, _VT_co]):  # undocumented
class IsDictItems(IsItemsView[_KT_co, _VT_co], Protocol[_KT_co, _VT_co]):  # type: ignore[misc]
    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    def __reversed__(self) -> Iterator[tuple[_KT_co, _VT_co]]:
        raise AssumedToBeImplementedException

    # __hash__: ClassVar[None]  # type: ignore[assignment]
    __hash__: ClassVar[None] = None  # type: ignore[assignment]
    if sys.version_info >= (3, 13):

        def isdisjoint(self, other: Iterable[tuple[_KT_co, _VT_co]], /) -> bool:
            raise AssumedToBeImplementedException

    if sys.version_info >= (3, 10):

        @property
        # def mapping(self) -> MappingProxyType[_KT_co, _VT_co]:
        def mapping(self) -> IsMappingProxyType[_KT_co, _VT_co]:
            raise AssumedToBeImplementedException
