from contextlib import AbstractContextManager
from typing import Any, Callable, ParamSpec, TypeVar

_DecoratedP = ParamSpec('_DecoratedP')
_DecoratedR = TypeVar('_DecoratedR')
_CallbackP = ParamSpec('_CallbackP')


def add_callback_after_call(func: Callable[_DecoratedP, _DecoratedR],
                            callback_func: Callable[_CallbackP, None],
                            *cb_args: _CallbackP.args,
                            with_context: AbstractContextManager | None = None,
                            **cb_kwargs: _CallbackP.kwargs) -> Callable[_DecoratedP, _DecoratedR]:
    class ValidateAfterCall(AbstractContextManager):
        def __enter__(self):
            ...

        def __exit__(self, exc_type, exc_val, exc_tb):
            ret = None

            if exc_val is None:
                callback_func(*cb_args, **cb_kwargs)
            return ret

    def _inner(*args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs) -> _DecoratedR:
        if with_context:
            with with_context:
                with ValidateAfterCall():
                    return func(*args, **kwargs)
        with ValidateAfterCall():
            return func(*args, **kwargs)

    return _inner


def apply_decorator_to_property(prop: property, decorator: Callable[[Callable], Any]) -> property:
    return property(
        fget=decorator(prop.fget) if prop.fget is not None else None,
        fset=decorator(prop.fset) if prop.fset is not None else None,
        fdel=decorator(prop.fdel) if prop.fdel is not None else None,
        doc=prop.__doc__)
