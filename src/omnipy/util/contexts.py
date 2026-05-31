"""Context managers and context helper utilities used across Omnipy."""

from contextlib import AbstractContextManager, contextmanager
from copy import deepcopy
from typing import Callable, Iterator

from typing_extensions import TypeVar

# TODO: Consider refactoring as many as possible of the context managers (AbstractContextManager
#       subclasses) to @contextmanager-decorated methods

_ValT = TypeVar('_ValT')


@contextmanager
def setup_and_teardown_callback_context(
    *,
    setup_func: Callable[..., _ValT] | None = None,
    setup_func_args: tuple[object, ...] = (),
    setup_func_kwargs: dict[str, object] = {},
    exception_func: Callable[..., None] | None = None,
    exception_func_args: tuple[object, ...] = (),
    exception_func_kwargs: dict[str, object] = {},
    teardown_func: Callable[..., None] | None = None,
    teardown_func_args: tuple[object, ...] = (),
    teardown_func_kwargs: dict[str, object] = {},
) -> Iterator[_ValT | None]:
    """Run optional setup, exception, and teardown callbacks around a context block.

    Args:
        setup_func: Optional callback invoked before entering the context.
        setup_func_args: Positional arguments passed to ``setup_func``.
        setup_func_kwargs: Keyword arguments passed to ``setup_func``.
        exception_func: Optional callback invoked if the context raises.
        exception_func_args: Positional arguments passed to ``exception_func``.
        exception_func_kwargs: Keyword arguments passed to ``exception_func``.
        teardown_func: Optional callback invoked when leaving the context.
        teardown_func_args: Positional arguments passed to ``teardown_func``.
        teardown_func_kwargs: Keyword arguments passed to ``teardown_func``.

    Yields:
        The value returned by ``setup_func``, if any.
    """

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
    """Context manager that stores the latest suppressed exception for later chaining."""
    def __init__(self):
        self._last_error = None

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self._last_error = exc_val
        return True

    def raise_derived(self, exc: Exception):
        """Raise an exception, chained from the last captured one when available.

        Args:
            exc: Exception to raise.

        Raises:
            Exception: ``exc``, with ``__cause__`` set to the most recently
                captured exception when present.
        """
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
    """Restore an object's attribute to its previous value when the context exits.

    Args:
        obj: Object whose attribute should be restored.
        attr_name: Name of the attribute to preserve and restore.
        copy_attr: Whether to deep-copy the original value before storing it.

    Yields:
        ``None`` while the caller temporarily mutates the attribute.
    """

    attr_value = getattr(obj, attr_name)
    prev_value = deepcopy(attr_value) if copy_attr else attr_value

    try:
        yield
    finally:
        setattr(obj, attr_name, prev_value)


@contextmanager
def nothing(*args, **kwds) -> Iterator[None]:
    """Yield a no-op context value."""

    yield None


class PrintExceptionContext(AbstractContextManager):
    """Context manager that prints and suppresses the first line of an exception."""
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f'{exc_type.__name__}: {str(exc_val).splitlines()[0]}', end='')
        return True


print_exception = PrintExceptionContext()
"""Context manager instance that prints and suppresses the first line of an exception."""
