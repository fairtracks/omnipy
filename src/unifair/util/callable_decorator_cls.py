from functools import update_wrapper
from types import MethodWrapperType
from typing import Callable, cast, Protocol, runtime_checkable, Type, TypeVar

# Types

DecoratorClassT = TypeVar('DecoratorClassT', covariant=True)


@runtime_checkable
class CallableParamAfterSelf(Protocol):
    def __call__(self, callable_arg: Callable, /, *args: object, **kwargs: object) -> None:
        ...


@runtime_checkable
class CallableClass(Protocol[DecoratorClassT]):
    def __call__(self, *args: object, **kwargs: object) -> Callable[[Callable], DecoratorClassT]:
        ...


def callable_decorator_cls(cls: Type[DecoratorClassT]) -> CallableClass[DecoratorClassT]:
    """
    "Meta-decorator" that allows any class to function as a decorator for a callable.

    The only requirements are that 1) the first argument after self of the __init__() method needs
    to be annotated as a callable, and 2) the class must not already be callable (have a __call__()
    method).

    Arguments and keyword arguments to the class decorator are supported.
    """
    if not isinstance(cls.__call__, MethodWrapperType):
        cls._wrapped_call: Callable = cast(Callable, cls.__call__)

    def _forward_call_to_obj_if_callable(self, *args: object,
                                         **kwargs: object) -> Type[DecoratorClassT]:
        """
        __call__ method at the class level which forward the call to instance-level call methods,
        if present (hardcoded as '_obj_call()'). This is needed due to the peculiarity that Python
        only looks up special methods (with double underscores) at the class level, and not at the
        instance level. Used in the decoration process to forward __call__ calls to the object level
        _obj_call() methods, if present.

        See: https://stackoverflow.com/q/33824228
        """
        if hasattr(self, '_obj_call'):
            return self._obj_call(*args, **kwargs)
        if hasattr(self, '_wrapped_call'):
            return self._wrapped_call(*args, **kwargs)
        raise TypeError("'{}' object is not callable".format(self.__class__.__name__))

    setattr(cls, '__call__', _forward_call_to_obj_if_callable)

    def _real_callable(arg: object) -> bool:
        """
        Helper method needed to ignore the class level __call__ method when checking whether the
        decorated class is callable.
        """
        if callable(arg):
            if hasattr(arg, '__call__'):
                if hasattr(arg.__call__, '__func__'):
                    # due to mypy bug: https://github.com/python/mypy/issues/14123
                    call_func_name = getattr(arg.__call__, '__func__').__name__

                    if call_func_name == _forward_call_to_obj_if_callable.__name__:
                        return False
            return True
        return False

    _wrapped_new: Callable = cls.__new__

    def _new_wrapper(cls, *args: object, **kwargs: object) -> DecoratorClassT:
        if _wrapped_new is object.__new__:
            obj = _wrapped_new(cls)
        else:
            obj = _wrapped_new(cls, *args, **kwargs)
            # setattr(cls, '__new__', _wrapped_new)

        _wrapped_init: CallableParamAfterSelf = cast(CallableParamAfterSelf, obj.__class__.__init__)

        # Wrapper method that replaces the __init__ method of the decorated class
        def _init_wrapper(self, *args: object, **kwargs: object) -> None:
            args_list = list(args)

            def _init(callable_arg: Callable) -> None:
                _wrapped_init(self, callable_arg, *args_list, **kwargs)
                update_wrapper(self, callable_arg, updated=[])

            if len(args_list) == 1 and _real_callable(args_list[0]):
                # Decorate the callable directly
                _callable_arg: Callable = cast(Callable, args_list[0])
                args_list.pop(0)
                _init(_callable_arg)
            else:
                # Add an instance-level _obj_call method, which are again callable by the
                # class-level __call__ method. When this method is called, the provided _callable_arg
                # is decorated.
                def _init_as_obj_call_method(
                        self, _callable_arg: Callable) -> Type[DecoratorClassT]:  # noqa
                    _init(_callable_arg)
                    del self._obj_call
                    return self

                self._obj_call = _init_as_obj_call_method.__get__(self)

            setattr(self.__class__, '__init__', _wrapped_init)

        setattr(obj.__class__, '__init__', _init_wrapper)

        return obj

    setattr(cls, '__new__', _new_wrapper)

    return cast(CallableClass[DecoratorClassT], cls)
