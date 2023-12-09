from typing import Callable, Protocol, runtime_checkable

from omnipy.api.typedefs import DecoratorClassT


@runtime_checkable
class IsCallableParamAfterSelf(Protocol):
    """"""
    def __call__(self, callable_arg: Callable, /, *args: object, **kwargs: object) -> None:
        ...


@runtime_checkable
class IsCallableClass(Protocol[DecoratorClassT]):
    """"""
    def __call__(self, *args: object, **kwargs: object) -> Callable[[Callable], DecoratorClassT]:
        ...
