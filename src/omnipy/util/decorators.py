from contextlib import AbstractContextManager
from typing import Any, Callable, Concatenate, ContextManager, Generic, ParamSpec, TypeVar

_DecoratedP = ParamSpec('_DecoratedP')
_DecoratedR = TypeVar('_DecoratedR')
_CallbackP = ParamSpec('_CallbackP')

_ArgT = TypeVar('_ArgT')
_SelfOrClsT = TypeVar('_SelfOrClsT')
T = TypeVar('T')

no_context = None


def add_callback_if_exception(
    decorated_func: Callable[_DecoratedP, _DecoratedR],
    callback_func: Callable[_DecoratedP, _DecoratedR],
    exception_types: tuple[type[Exception], ...] = (Exception,),
) -> Callable[_DecoratedP, _DecoratedR]:
    def _inner(*args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs) -> _DecoratedR:
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
    class CallbackAfterCall(AbstractContextManager):
        def __init__(self, dec_func, *args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs):
            self._decorated_func = dec_func
            self._args = args
            self._kwargs = kwargs
            self.return_value: _DecoratedR

        def __enter__(self):
            self.return_value = self._decorated_func(*self._args, **self._kwargs)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            ret = None

            if exc_val is None:
                self.return_value = callback_func(self.return_value, *cb_args, **cb_kwargs)
            return ret

    def _callback_after_call(dec_func, *args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs):
        with CallbackAfterCall(dec_func, *args, **kwargs) as callback:
            ...
        return callback.return_value

    def _inner(*args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs) -> _DecoratedR:
        if with_context:
            with with_context:
                return _callback_after_call(decorated_func, *args, **kwargs)
        else:
            return _callback_after_call(decorated_func, *args, **kwargs)

    return _inner


def apply_decorator_to_property(prop: property, decorator: Callable[[Callable], Any]) -> property:
    return property(
        fget=decorator(prop.fget) if prop.fget is not None else None,
        fset=decorator(prop.fset) if prop.fset is not None else None,
        fdel=decorator(prop.fdel) if prop.fdel is not None else None,
        doc=prop.__doc__)


def call_super_if_available(call_super_before_method: bool):
    class SuperCaller(Generic[_SelfOrClsT, _ArgT]):
        def __init__(self, method: Callable[[_SelfOrClsT, _ArgT], _ArgT]):
            self._method = method
            self._calling_obj_or_cls: _SelfOrClsT
            self._cls_of_decorated_method: type

        def __set_name__(self, cls: type, name: str) -> None:
            self._cls_of_decorated_method = cls
            # return self._call_methods_if_callable(arg)

        def __get__(self, obj: _SelfOrClsT | None, cls: _SelfOrClsT | None = None) -> 'SuperCaller':
            if obj is not None:
                self._calling_obj_or_cls = obj
            else:
                assert cls is not None
                self._calling_obj_or_cls = cls
            return self

        def __call__(self, arg: _ArgT) -> _ArgT:
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
    """
    Decorator that allows method to be called as class method or instance method

    Based on https://stackoverflow.com/a/79278611
    """

    # TODO: Properly attribute Stackoverflow contributions here and elsewhere,
    #       adding to the general license info which parts of the code follow
    #       CC BY-SA 4.0

    def __init__(
        self,
        decorated_func: Callable[Concatenate[T | None, type[T], _DecoratedP], _DecoratedR],
    ):
        self._decorated_func = decorated_func

    def __get__(self, instance: T | None, cls: type[T]) -> Callable[_DecoratedP, _DecoratedR]:
        def _func(*args: _DecoratedP.args, **kwargs: _DecoratedP.kwargs) -> _DecoratedR:
            return self._decorated_func(instance, cls, *args, **kwargs)

        return _func
