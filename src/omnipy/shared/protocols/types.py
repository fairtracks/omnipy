# Modified from the "types.py.imported" file in the same directory,
# which was imported from the Typeshed (https://github.com/python/typeshed).
#
# The Typeshed is licensed under the Apache License, Version 2.0 and the
# MIT License. See the LICENSE file in the root of the repository for
# details (https://github.com/python/typeshed/blob/main/LICENSE).
#
# See "types.py.imported" for more details.
from collections.abc import Iterator
from typing import ClassVar, Mapping, overload, Protocol

from typing_extensions import TypeVar

from omnipy.shared.exceptions import AssumedToBeImplementedException
from omnipy.shared.protocols.typing import IsItemsView, IsKeysView, IsMapping, IsValuesView

_KT_co = TypeVar('_KT_co', covariant=True)
_VT_co = TypeVar('_VT_co', covariant=True)
_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')


# @final
# class MappingProxyType(Mapping[_KT, _VT_co]):
class IsMappingProxyType(  # type: ignore[misc, type-var]
        IsMapping[_KT_co, _VT_co],  # pyright: ignore[reportInvalidTypeArguments]
        Protocol[_KT_co, _VT_co],
):
    __hash__: ClassVar[None] = None  # type: ignore[assignment]

    # def __new__(cls, mapping: 'SupportsKeysAndGetItem[_KT_co, _VT_co]') -> Self:
    #     raise AssumedToBeImplementedException

    def __getitem__(self, key: _KT_co, /) -> _VT_co:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    def __iter__(self) -> Iterator[_KT_co]:
        raise AssumedToBeImplementedException

    def __len__(self) -> int:
        raise AssumedToBeImplementedException

    def __eq__(self, value: object, /) -> bool:
        raise AssumedToBeImplementedException

    # def copy(self) -> dict[_KT_co, _VT_co]:
    #     raise AssumedToBeImplementedException

    def keys(self) -> IsKeysView[_KT_co]:
        raise AssumedToBeImplementedException

    def values(self) -> IsValuesView[_VT_co]:
        raise AssumedToBeImplementedException

    def items(self) -> IsItemsView[_KT_co, _VT_co]:
        raise AssumedToBeImplementedException

    @overload
    def get(self, key: _KT_co, /) -> _VT_co | None:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    @overload
    def get(self, key: _KT_co, default: _VT_co, /) -> _VT_co:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    @overload
    def get(self, key: _KT_co, default: _T2, /) -> _VT_co | _T2:  # type: ignore[misc]
        raise AssumedToBeImplementedException

    def get(
        self,
        key: _KT_co,  # type: ignore[misc]
        default: None | _VT_co | _T2 = None,
        /,
    ) -> _VT_co | _T2 | None:
        raise AssumedToBeImplementedException

    # def __class_getitem__(cls, item: Any, /) -> GenericAlias:
    #     raise AssumedToBeImplementedException

    def __reversed__(self) -> Iterator[_KT_co]:
        raise AssumedToBeImplementedException

    def __or__(self, value: Mapping[_T1, _T2], /) -> dict[_KT_co | _T1, _VT_co | _T2]:
        raise AssumedToBeImplementedException

    def __ror__(self, value: Mapping[_T1, _T2], /) -> dict[_KT_co | _T1, _VT_co | _T2]:
        raise AssumedToBeImplementedException
