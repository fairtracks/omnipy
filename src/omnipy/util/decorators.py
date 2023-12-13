from contextlib import AbstractContextManager
from typing import Callable, ParamSpec, TypeVar

DecoratedP = ParamSpec('DecoratedP')
DecoratedR = TypeVar('DecoratedR')
CallbackP = ParamSpec('CallbackP')


def add_callback_after_call(func: Callable[DecoratedP, DecoratedR],
                            callback_func: Callable[CallbackP, None],
                            *cb_args: CallbackP.args,
                            with_context: AbstractContextManager | None = None,
                            **cb_kwargs: CallbackP.kwargs) -> Callable[DecoratedP, DecoratedR]:
    class ValidateAfterCall(AbstractContextManager):
        def __enter__(self):
            ...

        def __exit__(self, exc_type, exc_val, exc_tb):
            ret = None

            if exc_val is None:
                callback_func(*cb_args, **cb_kwargs)
            return ret

    def _inner(*args: DecoratedP.args, **kwargs: DecoratedP.kwargs) -> DecoratedR:
        if with_context:
            with with_context:
                with ValidateAfterCall():
                    return func(*args, **kwargs)
        with ValidateAfterCall():
            return func(*args, **kwargs)

    return _inner
