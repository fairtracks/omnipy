"""Decorator helpers for callbacks, properties, and dual-bound methods.

This module provides lightweight decorator-building utilities used across Omnipy.
The helpers cover common patterns such as fallback callbacks on exceptions,
post-call result transformation, applying decorators to properties, optionally
delegating through ``super()``, and exposing one implementation as both a class
method and an instance method.
"""

from contextlib import AbstractContextManager
from typing import Any, Callable, Concatenate, ContextManager, Generic, ParamSpec, TypeVar

_DecoratedP = ParamSpec('_DecoratedP')
_DecoratedR = TypeVar('_DecoratedR')
_CallbackP = ParamSpec('_CallbackP')

_ArgT = TypeVar('_ArgT')
_SelfOrClsT = TypeVar('_SelfOrClsT')
T = TypeVar('T')

#: Sentinel used when no extra context manager should wrap a decorated call.
no_context = None


def add_callback_if_exception(
    decorated_func: Callable[_DecoratedP, _DecoratedR],
    callback_func: Callable[_DecoratedP, _DecoratedR],
    exception_types: tuple[type[Exception], ...] = (Exception,),
) -> Callable[_DecoratedP, _DecoratedR]:
    """Return a wrapper that falls back to ``callback_func`` on selected exceptions.

    Args:
        decorated_func: Primary callable.
        callback_func: Fallback callable invoked with the same arguments.
        exception_types: Exception types that trigger the fallback.

    Returns:
        A wrapped callable with exception-triggered fallback behavior.

    Raises:
        None. Matching exceptions are handled by calling ``callback_func``.

    Example:
        >>> def main(x):
        ...     return 10 // x
        >>> def fallback(x):
        ...     return 0
        >>> safe_main = add_callback_if_exception(main, fallback, (ZeroDivisionError,))
        >>> safe_main(0)
        0
    """
    def _inner(*args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs) -> _DecoratedR:
        """Invoke primary callable and fall back on handled exceptions.

        Args:
            *args: Positional arguments forwarded to both callables.
            **kwargs: Keyword arguments forwarded to both callables.

        Returns:
            Result from ``decorated_func`` or, on matched exception, from
            ``callback_func``.

        Raises:
            Exception: Propagates exceptions not listed in ``exception_types``.

        Example:
            >>> def main(x):
            ...     return 10 // x
            >>> def fallback(x):
            ...     return 0
            >>> wrapped = add_callback_if_exception(main, fallback, (ZeroDivisionError,))
            >>> wrapped(5)
            2
        """
        try:
            return decorated_func(*args, **kwargs)
        except exception_types:
            return callback_func(*args, **kwargs)

    return _inner


def add_callback_after_call(decorated_func: Callable[_DecoratedP, _DecoratedR],
                            callback_func: Callable[Concatenate[_DecoratedR, _CallbackP],
                                                    _DecoratedR],
                            with_context: ContextManager[None] | None,
                            *cb_args: _CallbackP.args,
                            **cb_kwargs: _CallbackP.kwargs) -> Callable[_DecoratedP, _DecoratedR]:
    """Return a wrapper that post-processes a successful result.

    Args:
        decorated_func: Callable producing the initial result.
        callback_func: Callable receiving the result plus callback arguments.
        with_context: Optional context manager wrapped around the full call.
        *cb_args: Extra positional callback arguments.
        **cb_kwargs: Extra keyword callback arguments.

    Returns:
        A wrapped callable that runs ``callback_func`` only when the decorated
        call succeeds without raising an exception.

    Raises:
        None. Exceptions from ``decorated_func`` are propagated unchanged.

    Example:
        >>> def parse_int(text):
        ...     return int(text)
        >>> def clamp(value, lower):
        ...     return max(value, lower)
        >>> wrapped = add_callback_after_call(parse_int, clamp, None, 0)
        >>> wrapped('-2')
        0
    """
    class CallbackAfterCall(AbstractContextManager):
        """Context manager running callback only after successful call completion.

        Args:
            None.

        Returns:
            None. Instances are created for scoped call handling.

        Raises:
            None.

        Example:
            Used internally by ``add_callback_after_call``.
        """

        def __init__(self, dec_func, *args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs):
            """Store callable and invocation arguments for deferred execution.

            Args:
                dec_func: Callable invoked on ``__enter__``.
                *args: Positional arguments forwarded to ``dec_func``.
                **kwargs: Keyword arguments forwarded to ``dec_func``.

            Returns:
                None.

            Raises:
                None.

            Example:
                Constructed internally by ``_callback_after_call``.
            """
            self._decorated_func = dec_func
            self._args = args
            self._kwargs = kwargs
            self.return_value: _DecoratedR

        def __enter__(self):
            """Execute the decorated callable and cache its return value.

            Args:
                None.

            Returns:
                ``self`` with ``return_value`` populated.

            Raises:
                Exception: Propagates exceptions from the decorated callable.

            Example:
                Called by ``with CallbackAfterCall(...):``.
            """
            self.return_value = self._decorated_func(*self._args, **self._kwargs)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Run post-callback when exiting without an exception.

            Args:
                exc_type: Exception type if raised inside the context.
                exc_val: Exception instance if raised inside the context.
                exc_tb: Traceback if raised inside the context.

            Returns:
                ``None`` to preserve normal exception propagation behavior.

            Raises:
                Exception: Propagates callback exceptions and any context
                    exception by returning ``None``.

            Example:
                Triggered automatically at context-manager exit.
            """
            ret = None

            if exc_val is None:
                self.return_value = callback_func(self.return_value, *cb_args, **cb_kwargs)
            return ret

    def _callback_after_call(dec_func, *args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs):
        """Execute ``dec_func`` through ``CallbackAfterCall``.

        Args:
            dec_func: Callable to invoke.
            *args: Positional arguments forwarded to ``dec_func``.
            **kwargs: Keyword arguments forwarded to ``dec_func``.

        Returns:
            Return value captured by the context manager, potentially transformed
            by ``callback_func``.

        Raises:
            Exception: Propagates exceptions from ``dec_func`` or
                ``callback_func``.

        Example:
            Used internally to centralize callback-after-call sequencing.
        """
        with CallbackAfterCall(dec_func, *args, **kwargs) as callback:
            ...
        return callback.return_value

    def _inner(*args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs) -> _DecoratedR:
        """Invoke wrapped call optionally inside ``with_context``.

        Args:
            *args: Positional arguments for ``decorated_func``.
            **kwargs: Keyword arguments for ``decorated_func``.

        Returns:
            The callback-processed return value.

        Raises:
            Exception: Propagates exceptions from context manager, decorated
                callable, or callback callable.

        Example:
            Returned as the callable wrapper from
            ``add_callback_after_call(...)``.
        """
        if with_context:
            with with_context:
                return _callback_after_call(decorated_func, *args, **kwargs)
        else:
            return _callback_after_call(decorated_func, *args, **kwargs)

    return _inner


def apply_decorator_to_property(prop: property, decorator: Callable[[Callable], Any]) -> property:
    """Apply the same decorator to all available accessors of a property.

    Args:
        prop: Property whose getter, setter, and deleter should be decorated.
        decorator: Decorator applied to each existing accessor.

    Returns:
        A new property with decorated accessors and the original docstring.

    Raises:
        None.

    Example:
        >>> def passthrough(func):
        ...     return func
        >>> class Demo:
        ...     @property
        ...     def value(self):
        ...         return 1
        >>> Demo.value = apply_decorator_to_property(Demo.value, passthrough)
        >>> Demo().value
        1
    """
    return property(
        fget=decorator(prop.fget) if prop.fget is not None else None,
        fset=decorator(prop.fset) if prop.fset is not None else None,
        fdel=decorator(prop.fdel) if prop.fdel is not None else None,
        doc=prop.__doc__)


def call_super_if_available(call_super_before_method: bool):
    """Create a descriptor that composes a method with its ``super()`` version.

    Args:
        call_super_before_method: When ``True``, pass the result of ``super()`` to
            the decorated method. When ``False``, feed the decorated result into
            ``super()`` instead.

    Returns:
        A descriptor class wrapping a single-argument instance or class method.

    Raises:
        None.

    Notes:
        If the parent class has no same-named callable, the original method is
        executed directly.

    Example:
        >>> class Base:
        ...     def normalize(self, value):
        ...         return value + 1
        >>> class Child(Base):
        ...     @call_super_if_available(call_super_before_method=True)
        ...     def normalize(self, value):
        ...         return value * 2
        >>> Child().normalize(3)
        8
    """
    class SuperCaller(Generic[_SelfOrClsT, _ArgT]):
        """Descriptor binding method calls and optional ``super()`` delegation.

        Args:
            None.

        Returns:
            None. Instances are descriptor objects returned by the decorator.

        Raises:
            None.

        Example:
            Created internally by ``call_super_if_available``.
        """

        def __init__(self, method: Callable[[_SelfOrClsT, _ArgT], _ArgT]):
            """Store the decorated method and descriptor state placeholders.

            Args:
                method: Method that may be composed with a parent implementation.

            Returns:
                None.

            Raises:
                None.

            Example:
                Invoked by Python at decoration time.
            """
            self._method = method
            self._calling_obj_or_cls: _SelfOrClsT
            self._cls_of_decorated_method: type

        def __set_name__(self, cls: type, name: str) -> None:
            """Capture owner class when descriptor is assigned on class creation.

            Args:
                cls: Class owning this descriptor.
                name: Attribute name assigned on ``cls``.

            Returns:
                None.

            Raises:
                None.

            Example:
                Called automatically by Python descriptor protocol.
            """
            self._cls_of_decorated_method = cls
            # return self._call_methods_if_callable(arg)

        def __get__(self, obj: _SelfOrClsT | None, cls: _SelfOrClsT | None = None) -> 'SuperCaller':
            """Bind the descriptor to either instance or class access context.

            Args:
                obj: Instance on instance access, else ``None``.
                cls: Class on class access.

            Returns:
                ``self`` ready for ``__call__`` invocation.

            Raises:
                AssertionError: If both ``obj`` and ``cls`` are ``None``.

            Example:
                Triggered when accessing the decorated attribute.
            """
            if obj is not None:
                self._calling_obj_or_cls = obj
            else:
                assert cls is not None
                self._calling_obj_or_cls = cls
            return self

        def __call__(self, arg: _ArgT) -> _ArgT:
            """Invoke method and optionally compose with parent implementation.

            Args:
                arg: Single argument passed to both methods.

            Returns:
                Result from the decorated method alone or composed with
                ``super()`` based on ``call_super_before_method``.

            Raises:
                Exception: Propagates any exception from decorated or parent
                    method calls.

            Example:
                Executed when calling the decorated attribute like a function.
            """
            method = self._method.__func__ if hasattr(self._method, '__func__') else self._method
            super_method: Callable[[_ArgT], _ArgT] | None = getattr(
                super(self._cls_of_decorated_method, self._calling_obj_or_cls),
                self._method.__name__,
                None)
            if super_method and callable(super_method):
                if call_super_before_method:
                    return method(self._calling_obj_or_cls, super_method(arg))
                else:
                    return super_method(method(self._calling_obj_or_cls, arg))
            else:
                return method(self._calling_obj_or_cls, arg)

    return SuperCaller


class class_or_instance_method(Generic[T, _DecoratedP, _DecoratedR], object):
    """Descriptor decorator enabling both class and instance invocation styles.

    The wrapped implementation receives both ``instance`` and ``cls`` so it can
    branch behavior depending on whether it was called via ``obj.method(...)`` or
    ``Cls.method(...)``.

    Args:
        None.

    Returns:
        None. This class is used as a descriptor/decorator type.

    Raises:
        None.

    Example:
        >>> class Demo:
        ...     @class_or_instance_method
        ...     def whoami(self, cls):
        ...         return cls.__name__ if self is None else type(self).__name__
        >>> Demo.whoami()
        'Demo'
    """

    # TODO: Properly attribute Stackoverflow contributions here and elsewhere,
    #       adding to the general license info which parts of the code follow
    #       CC BY-SA 4.0

    def __init__(
        self,
        decorated_func: Callable[Concatenate[T | None, type[T], _DecoratedP], _DecoratedR],
    ):
        """Store the dual-bound implementation function.

        Args:
            decorated_func: Callable receiving ``(instance_or_none, cls, *args,
                **kwargs)``.

        Returns:
            None.

        Raises:
            None.

        Example:
            >>> def impl(instance, cls):
            ...     return cls.__name__
            >>> wrapper = class_or_instance_method(impl)
            >>> isinstance(wrapper, class_or_instance_method)
            True
        """
        self._decorated_func = decorated_func

    def __get__(self, instance: T | None, cls: type[T]) -> Callable[_DecoratedP, _DecoratedR]:
        """Bind access and return a callable proxy for invocation.

        Args:
            instance: Object instance when accessed on an instance, otherwise
                ``None``.
            cls: Owner class used for class-level access.

        Returns:
            A callable that forwards arguments to the wrapped implementation with
            both ``instance`` and ``cls``.

        Raises:
            None.

        Example:
            >>> class Demo:
            ...     @class_or_instance_method
            ...     def name(self, cls):
            ...         return cls.__name__
            >>> Demo().name()
            'Demo'
        """
        def _func(*args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs) -> _DecoratedR:
            """Forward invocation to the stored dual-bound implementation.

            Args:
                *args: Positional arguments for the decorated implementation.
                **kwargs: Keyword arguments for the decorated implementation.

            Returns:
                Result produced by ``self._decorated_func``.

            Raises:
                Exception: Propagates exceptions raised by the decorated
                    implementation.

            Example:
                Returned by ``__get__`` and called as the bound method.
            """
            return self._decorated_func(instance, cls, *args, **kwargs)

        return _func
