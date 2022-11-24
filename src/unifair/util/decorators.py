from inspect import Parameter, signature
from typing import Callable, cast, Type, TypeAlias

InitWithCallableFirstArgAfterSelf: TypeAlias = Callable[[object, Callable, ...], None]


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


def callable_decorator_class(cls: Type) -> Callable:
    check_cls_init_has_callable_as_first_arg_after_self(cls)

    def _forward_call_to_obj_if_callable(self, *args, **kwargs):
        if hasattr(self, '_obj_call'):
            return self._obj_call(*args, **kwargs)
        raise TypeError("'{}' object is not callable".format(self.__class__.__name__))

    cls.__call__ = _forward_call_to_obj_if_callable

    def _real_callable(arg: object) -> bool:
        if callable(arg):
            if hasattr(arg, '__call__'):
                if hasattr(arg.__call__, '__func__'):
                    if arg.__call__.__func__.__name__ == _forward_call_to_obj_if_callable.__name__:
                        return False
            return True
        return False

    _wrapped_init: InitWithCallableFirstArgAfterSelf = \
        cast(InitWithCallableFirstArgAfterSelf, cls.__init__)

    def _init_wrapper(self, *args: object, **kwargs: object):
        args = list(args)

        def _forward_init(callable_arg: Callable) -> None:
            _wrapped_init(self, callable_arg, *args, **kwargs)

        if len(args) > 0 and _real_callable(args[0]):
            _callable_arg: Callable = cast(Callable, args[0])
            args.pop(0)
            _forward_init(_callable_arg)
        else:

            def _init_wrapper_as_obj_call_method(self, *inner_args: Callable):  # noqa
                inner_args = list(inner_args)
                assert not len(inner_args) > 1
                _forward_init(*inner_args)

                del self._obj_call

                return self

            self._obj_call = _init_wrapper_as_obj_call_method.__get__(self)

    cls.__init__ = _init_wrapper

    return cls
