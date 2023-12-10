from typing import Callable, ParamSpec, TypeVar

DecoratedP = ParamSpec('DecoratedP')
DecoratedR = TypeVar('DecoratedR')
CallbackP = ParamSpec('CallbackP')


def add_callback_after_call(func: Callable[DecoratedP, DecoratedR],
                            callback_func: Callable[CallbackP, None],
                            *cb_args: CallbackP.args,
                            **cb_kwargs: CallbackP.kwargs) -> Callable[DecoratedP, DecoratedR]:
    class ValidateAfterCall:
        def __enter__(self):
            ...

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_val is None:
                callback_func(*cb_args, **cb_kwargs)

    def _inner(*args: DecoratedP.args, **kwargs: DecoratedP.kwargs) -> DecoratedR:
        with ValidateAfterCall():
            return func(*args, **kwargs)

    return _inner
