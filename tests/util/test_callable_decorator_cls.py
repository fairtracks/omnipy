import inspect
from typing import Any, Callable, Dict, Union

import pytest

from omnipy.util.callable_decorator_cls import callable_decorator_cls

# Note:
#
# Due to the following bug:
#
# https://github.com/python/mypy/issues/3135
#
# mypy is not correctly considering the types of the class decorator. As a consequence, it reports
# a bunch of errors on MockClass and MockClassNotCallableArg that should clear up once bug is fixed


@callable_decorator_cls
class MockClass:
    def __init__(self, func: Callable, *args: object, **kwargs: object) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args: object, **kwargs: object) -> Dict:
        return dict(call_args=args, call_kwargs=kwargs)


def test_fail_plain_decorator_not_callable_arg() -> None:
    @callable_decorator_cls
    class MockClassNoCallableArg:
        def __init__(self) -> None:
            ...

    with pytest.raises(TypeError):

        @MockClassNoCallableArg
        def my_func(*args: object, **kwargs: object) -> Dict[str, Any]:
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
    def my_func(*args: object, **kwargs: object) -> Dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) is MockClass
    _assert_func_decoration(my_func)  # noqa
    _assert_call_func(my_func)

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_plain_decorator_parentheses() -> None:
    @MockClass()
    def my_func(*args: object, **kwargs: object) -> Dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) is MockClass
    _assert_func_decoration(my_func)  # noqa
    _assert_call_func(my_func)

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_kwargs() -> None:
    @MockClass(param=123, other=True)
    def my_func(*args: object, **kwargs: object) -> Dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) is MockClass
    _assert_func_decoration(my_func)  # noqa
    _assert_call_func(my_func)

    assert my_func.args == ()
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs() -> None:
    @MockClass(123, True, param=123, other=True)
    def my_func(*args: object, **kwargs: object) -> Dict[str, object]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) is MockClass
    _assert_func_decoration(my_func)  # noqa
    _assert_call_func(my_func)

    assert my_func.args == (123, True)
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs_first_arg_func() -> None:
    def other_func():
        pass

    @MockClass(other_func, 123, True, param=123, other=True)
    def my_func(*args: object, **kwargs: object) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) is MockClass
    _assert_func_decoration(my_func)  # noqa
    _assert_call_func(my_func)

    assert my_func.args == (other_func, 123, True)
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_double_decorator_with_args_and_kwargs() -> None:
    @MockClass(234, False, param=234, other=False)
    @MockClass(123, True, param=123, other=True)
    def my_func(*args: object, **kwargs: object) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) is MockClass
    _assert_func_decoration(my_func)  # noqa
    _assert_call_func(my_func)

    assert my_func.args == (234, False)
    assert my_func.kwargs == dict(param=234, other=False)
    assert my_func.func(1, 'b', c=True) == dict(call_args=(1, 'b'), call_kwargs=dict(c=True))


def test_fail_decorator_with_single_callable_arg() -> None:
    @callable_decorator_cls
    class MockClassSingleCallableArg:
        def __init__(self, decorated_func: Callable, other_func: Callable) -> None:
            ...

    def extra_func():
        ...

    with pytest.raises(TypeError):

        @MockClassSingleCallableArg(extra_func)
        def my_func(*args: object, **kwargs: object) -> Dict[str, Any]:
            return dict(args=args, kwargs=kwargs)


def my_fancy_func(*args: Union[int, str], **kwargs: bool) -> Dict[str, Any]:
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
