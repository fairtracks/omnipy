import inspect
from typing import Any, Callable, cast, Generic, ParamSpec

import pytest
from typing_extensions import reveal_type, TypeVar

from omnipy.util.callable_decorator import callable_decorator_cls

# Note:
#
# Due to the following bug:
#
# https://github.com/python/mypy/issues/3135
#
# mypy is not correctly considering the types of the class decorator. As a consequence, it reports
# a bunch of errors on MockClass and MockClassNotCallableArg that should clear up once bug is fixed

InitP = ParamSpec('InitP')
CallP = ParamSpec('CallP')
RetT = TypeVar('RetT', bound=dict)


class MockClassBase(Generic[InitP, CallP, RetT]):
    def __init__(self, func: Callable[CallP, RetT], *args: InitP.args,
                 **kwargs: InitP.kwargs) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args: CallP.args, **kwargs: CallP.kwargs) -> RetT:
        return cast(RetT, dict(call_args=args, call_kwargs=kwargs))


MockClass = callable_decorator_cls(MockClassBase)


def test_fail_plain_decorator_not_callable_arg() -> None:
    @callable_decorator_cls
    class MockClassNoCallableArg:
        def __init__(self) -> None:
            ...

    with pytest.raises(TypeError):

        @MockClassNoCallableArg
        def my_func(*args: object, **kwargs: object) -> dict[str, Any]:
            return dict(args=args, kwargs=kwargs)


def _assert_func_decoration(my_func):
    assert my_func.__name__ == my_func.func.__name__
    assert my_func.__qualname__ == my_func.func.__qualname__
    assert my_func.__module__ == my_func.func.__module__
    assert my_func.__doc__ == my_func.func.__doc__
    assert my_func.__annotations__ == my_func.func.__annotations__

    assert inspect.signature(my_func) == inspect.signature(my_func.func)


def _assert_call_func(my_func):
    assert my_func(1, 'b', c=True) == dict(call_args=(1, 'b'), call_kwargs=dict(c=True))


def test_plain_decorator() -> None:
    @MockClass
    def my_func_1(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    reveal_type(my_func_1)
    reveal_type(my_func_1.__call__)

    assert type(my_func_1) is MockClass
    _assert_func_decoration(my_func_1)  # noqa
    _assert_call_func(my_func_1)

    assert my_func_1.args == ()
    assert my_func_1.kwargs == {}
    assert my_func_1.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_plain_decorator_parentheses() -> None:
    @MockClass()
    def my_func_2(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    reveal_type(my_func_2)
    reveal_type(my_func_2.__call__)

    assert type(my_func_2) is MockClass
    _assert_func_decoration(my_func_2)  # noqa
    _assert_call_func(my_func_2)

    assert my_func_2.args == ()
    assert my_func_2.kwargs == {}
    assert my_func_2.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_kwargs() -> None:
    @MockClass(param=123, other=True)
    def my_func_3(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_3) is MockClass
    _assert_func_decoration(my_func_3)  # noqa
    _assert_call_func(my_func_3)

    assert my_func_3.args == ()
    assert my_func_3.kwargs == dict(param=123, other=True)
    assert my_func_3.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs() -> None:
    @MockClass(123, True, param=123, other=True)
    def my_func_4(*args: object, **kwargs: object) -> dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_4) is MockClass
    _assert_func_decoration(my_func_4)  # noqa
    _assert_call_func(my_func_4)

    assert my_func_4.args == (123, True)
    assert my_func_4.kwargs == dict(param=123, other=True)
    assert my_func_4.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs_first_arg_func() -> None:
    def other_func():
        pass

    @MockClass(other_func, 123, True, param=123, other=True)
    def my_func_5(*args: object, **kwargs: object) -> dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_5) is MockClass
    _assert_func_decoration(my_func_5)  # noqa
    _assert_call_func(my_func_5)

    assert my_func_5.args == (other_func, 123, True)
    assert my_func_5.kwargs == dict(param=123, other=True)
    assert my_func_5.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_double_decorator_with_args_and_kwargs() -> None:
    @MockClass(234, False, param=234, other=False)
    @MockClass(123, True, param=123, other=True)
    def my_func_6(*args: object, **kwargs: object) -> dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func_6) is MockClass
    _assert_func_decoration(my_func_6)  # noqa
    _assert_call_func(my_func_6)

    assert my_func_6.args == (234, False)
    assert my_func_6.kwargs == dict(param=234, other=False)
    assert my_func_6.func(1, 'b', c=True) == dict(call_args=(1, 'b'), call_kwargs=dict(c=True))


def test_fail_decorator_with_single_callable_arg() -> None:
    @callable_decorator_cls
    class MockClassSingleCallableArg:
        def __init__(self, decorated_func: Callable, other_func: Callable) -> None:
            ...

    def extra_func():
        ...

    with pytest.raises(TypeError):

        @MockClassSingleCallableArg(extra_func)
        def my_func(*args: object, **kwargs: object) -> dict[str, Any]:
            return dict(args=args, kwargs=kwargs)


def my_fancy_func(*args: int | str, **kwargs: bool) -> dict[str, Any]:
    """
    Documentation of myfunc()
    """
    return dict(args=args, kwargs=kwargs)


def test_decorator_as_function_fancy_func() -> None:
    my_func = MockClass(my_fancy_func)

    assert type(my_func) is MockClass
    _assert_func_decoration(my_func)  # noqa
    _assert_call_func(my_func)

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_as_function_fancy_func_args_kwargs() -> None:
    my_func = MockClass(123, True, param=123, other=True)(my_fancy_func)

    assert type(my_func) is MockClass
    _assert_func_decoration(my_func)  # noqa
    _assert_call_func(my_func)

    assert my_func.args == (123, True)
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_fail_decorator_as_function_no_args_no_func() -> None:
    my_func = MockClass()

    assert type(my_func) is MockClass

    with pytest.raises(TypeError):
        my_func()  # type: ignore # noqa
    with pytest.raises(AttributeError):
        assert my_func.args == ()
    with pytest.raises(AttributeError):
        assert my_func.kwargs == {}


def test_fail_decorator_as_function_args_and_kwargs_no_func() -> None:
    my_func = MockClass(123, True, param=123, other=True)

    assert type(my_func) is MockClass

    with pytest.raises(TypeError):
        my_func()
    with pytest.raises(AttributeError):
        assert my_func.args == ()
    with pytest.raises(AttributeError):
        assert my_func.kwargs == {}
