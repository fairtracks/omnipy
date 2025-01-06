from typing import Callable, Protocol, runtime_checkable

from typing_extensions import TypeVar

_AnyKeyT = TypeVar('_AnyKeyT', contravariant=True, bound=object)
_ValT = TypeVar('_ValT', bound=object)


@runtime_checkable
class IsCallableParamAfterSelf(Protocol):
    """"""
    def __call__(self, callable_arg: Callable, /, *args: object, **kwargs: object) -> None:
        ...


class IsWeakKeyRefContainer(Protocol[_AnyKeyT, _ValT]):
    def __contains__(self, key: _AnyKeyT) -> bool:
        ...

    def get(self, key: _AnyKeyT) -> _ValT | None:
        ...

    def __getitem__(self, key: _AnyKeyT) -> _ValT:
        ...

    def __setitem__(self, key: _AnyKeyT, value: _ValT) -> None:
        ...

    def __len__(self) -> int:
        ...
