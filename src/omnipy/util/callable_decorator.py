from functools import update_wrapper
from types import MethodWrapperType
from typing import Callable, cast, Concatenate, ParamSpec, TypeVar

from omnipy.api.protocols.private.util import IsCallableParamAfterSelf

InitP = ParamSpec('InitP')
CallP = ParamSpec('CallP')
RetT = TypeVar('RetT', contravariant=True)

DecoratedT = TypeVar('DecoratedT')


def callable_decorator_cls(  # noqa: C901
    cls: Callable[Concatenate[Callable[CallP, RetT], InitP], DecoratedT]) -> \
        Callable[InitP, Callable[[Callable[CallP, RetT]], DecoratedT]]:
    """
    "Meta-decorator" that allows any class to function as a decorator for a callable.

    The only requirements are that the first argument after self of the __init__() method needs
    to be annotated as a callable.

    Arguments and keyword arguments to the class decorator are supported.
    """

    # Retain existing __call__ method, if present, except for built-in classes (e.g. int, str),
    # whose call method is a MethodWrapperType.
    if not isinstance(cls.__call__, MethodWrapperType):  # type: ignore[operator]
        cls._wrapped_call: Callable = cast(  # type: ignore[attr-defined, misc]
            Callable, cls.__call__)  # type: ignore[operator]

    def _forward_call_to_obj_if_callable(self, *args: object, **kwargs: object) -> DecoratedT:
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

    def _new_wrapper(cls, *args: object, **kwargs: object) -> DecoratedT:
        if _wrapped_new is object.__new__:
            obj = _wrapped_new(cls)
        else:
            obj = _wrapped_new(cls, *args, **kwargs)
            # setattr(cls, '__new__', _wrapped_new)

        _wrapped_init: IsCallableParamAfterSelf = cast(IsCallableParamAfterSelf,
                                                       obj.__class__.__init__)

        # Wrapper method that replaces the __init__ method of the decorated class
        def _init_wrapper(self, *args: object, **kwargs: object) -> None:
            args_list = list(args)

            def _init(callable_arg: Callable[CallP, RetT]) -> None:
                _wrapped_init(self, callable_arg, *args_list, **kwargs)
                update_wrapper(self, callable_arg, updated=[])

            if len(args_list) == 1 and _real_callable(args_list[0]):
                # If no parentheses used in the decoration syntax (e.g. @decorator)
                # then decorate the callable directly
                _callable_arg = cast(Callable[CallP, RetT], args_list[0])
                args_list.pop(0)
                _init(_callable_arg)
            else:
                # If parentheses used in the decoration syntax (e.g. @decorator())
                # then add an instance-level _obj_call method, which are again callable by the
                # class-level __call__ method. When this method is called, the provided
                # _callable_arg is decorated.
                def _init_as_obj_call_method(
                        self, _callable_arg: Callable[CallP, RetT]) -> DecoratedT:  # noqa
                    _init(_callable_arg)
                    del self._obj_call
                    return self

                self._obj_call = _init_as_obj_call_method.__get__(self)

            setattr(self.__class__, '__init__', _wrapped_init)

        setattr(obj.__class__, '__init__', _init_wrapper)

        return obj

    setattr(cls, '__new__', _new_wrapper)

    return cast(Callable[InitP, Callable[[Callable[CallP, RetT]], DecoratedT]], cls)
