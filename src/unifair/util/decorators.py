from inspect import Parameter, signature
from typing import Callable, cast, Type, TypeAlias

# Types
InitWithCallableFirstArgAfterSelf: TypeAlias = Callable[[object, Callable, ...], None]


# Helper functions
def check_cls_init_has_callable_as_first_arg_after_self(cls: Type):
    init_params = signature(cls.__init__).parameters

    if len(init_params) > 1:
        first_param = tuple(init_params.values())[1]

        first_param_positional = first_param.kind in [
            Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD
        ]
        first_param_callable = first_param.annotation in [Callable, 'Callable']

        if first_param_positional and first_param_callable:
            return

    raise AttributeError('The first non-self argument of the __init__() method of class '
                         f'"{cls.__name__}" is not annotated as a callable')


# Decorators
def callable_decorator_class(cls: Type) -> Callable:
    """
    "Meta-decorator" that allows any class to function as a decorator for a callable. The only
    requirement is that the first argument after self of the __init__() method needs to be annotated
    as a callable. Arguments and keyword arguments to the class decorator are supported.
    """
    check_cls_init_has_callable_as_first_arg_after_self(cls)

    def _forward_call_to_obj_if_callable(self, *args, **kwargs):
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
        raise TypeError("'{}' object is not callable".format(self.__class__.__name__))

    cls.__call__ = _forward_call_to_obj_if_callable

    def _real_callable(arg: object) -> bool:
        """
        Helper method needed to ignore the class level __call__ method when checking whether the
        decorated class is callable.
        """
        if callable(arg):
            if hasattr(arg, '__call__'):
                if hasattr(arg.__call__, '__func__'):
                    if arg.__call__.__func__.__name__ == _forward_call_to_obj_if_callable.__name__:
                        return False
            return True
        return False

    _wrapped_init: InitWithCallableFirstArgAfterSelf = \
        cast(InitWithCallableFirstArgAfterSelf, cls.__init__)

    # Wrapper method that replaces the __init __ method of the decorated class
    def _init_wrapper(self, *args: object, **kwargs: object):
        args = list(args)

        def _init(callable_arg: Callable) -> None:
            _wrapped_init(self, callable_arg, *args, **kwargs)

        if len(args) > 0 and _real_callable(args[0]):
            # Decorate the callable directly
            _callable_arg: Callable = cast(Callable, args[0])
            args.pop(0)
            _init(_callable_arg)
        else:
            # Add an instance-level _obj_call method, which are again callable by the
            # class-level __call__ method. When this method is called, the provided _callable_arg
            # is decorated.
            def _init_as_obj_call_method(self, _callable_arg: Callable):  # noqa
                _init(_callable_arg)
                del self._obj_call
                return self

            self._obj_call = _init_as_obj_call_method.__get__(self)

    cls.__init__ = _init_wrapper

    return cls
