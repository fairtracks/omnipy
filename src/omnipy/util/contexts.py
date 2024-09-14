from contextlib import AbstractContextManager, contextmanager
from copy import deepcopy
from typing import Callable, Iterator, ParamSpec

from typing_extensions import TypeVar

# TODO: Consider refactoring as many as possible of the context managers (AbstractContextManager
#       subclasses) to @contextmanager-decorated methods

_SetupP = ParamSpec('_SetupP')
_TeardownP = ParamSpec('_TeardownP')
_ValT = TypeVar('_ValT')


@contextmanager
def setup_and_teardown_callback_context(
    *,
    setup_func: Callable[_SetupP, _ValT] | None = None,
    setup_func_args: _SetupP.args = (),
    setup_func_kwargs: _SetupP.kwargs = {},
    exception_func: Callable[_TeardownP, None] | None = None,
    exception_func_args: _TeardownP.args = (),
    exception_func_kwargs: _TeardownP.kwargs = {},
    teardown_func: Callable[_TeardownP, None] | None = None,
    teardown_func_args: _TeardownP.args = (),
    teardown_func_kwargs: _TeardownP.kwargs = {},
) -> Iterator[_ValT | None]:
    setup_val: _ValT | None = None
    if setup_func is not None:
        setup_val = setup_func(*setup_func_args, **setup_func_kwargs)
    try:
        yield setup_val
    except Exception:
        if exception_func is not None:
            exception_func(*exception_func_args, **exception_func_kwargs)
        raise
    finally:
        if teardown_func is not None:
            teardown_func(*teardown_func_args, **teardown_func_kwargs)


class LastErrorHolder(AbstractContextManager):
    def __init__(self):
        self._last_error = None

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self._last_error = exc_val
        return True

    def raise_derived(self, exc: Exception):
        if self._last_error is not None:
            raise exc from self._last_error
        else:
            raise exc


@contextmanager
def hold_and_reset_prev_attrib_value(
    obj: object,
    attr_name: str,
    copy_attr: bool = False,
) -> Iterator[None]:
    attr_value = getattr(obj, attr_name)
    prev_value = deepcopy(attr_value) if copy_attr else attr_value

    try:
        yield
    finally:
        setattr(obj, attr_name, prev_value)


@contextmanager
def nothing(*args, **kwds) -> Iterator[None]:
    yield None


class PrintExceptionContext(AbstractContextManager):
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f'{exc_type.__name__}: {str(exc_val).splitlines()[0]}', end='')
        return True


print_exception = PrintExceptionContext()
