from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable, TypeVar

from omnipy.api.types import DecoratorClassT


@runtime_checkable
class IsCallableParamAfterSelf(Protocol):
    """"""
    def __call__(self, callable_arg: Callable, /, *args: object, **kwargs: object) -> None:
        ...


CC = TypeVar('CC', bound=Callable, contravariant=True)


@runtime_checkable
class IsCallableClass(Protocol[DecoratorClassT, CC]):
    """"""
    def __call__(self, *args: object, **kwargs: object) -> Callable[[CC], DecoratorClassT]:
        ...
