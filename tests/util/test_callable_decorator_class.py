from typing import Any, Callable, Dict, Protocol, runtime_checkable, TypeVar

import pytest

from unifair.util.decorators import callable_decorator_class

# Note:
#
# Due to the following bug:
#
# https://github.com/python/mypy/issues/3135
#
# mypy is not correctly considering the types of the class decorator. As a consequence, it reports
# a bunch of errors on MockClass and MockClassNotCallableArg that should clear up once bug is fixed


@callable_decorator_class
class MockClass:
    def __init__(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs


def test_fail_plain_decorator_not_callable_arg() -> None:
    @callable_decorator_class
    class MockClassNoCallableArg:
        def __init__(self) -> None:
            ...

    with pytest.raises(TypeError):

        @MockClassNoCallableArg
        def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            return dict(args=args, kwargs=kwargs) @ callable_decorator_class


def test_plain_decorator() -> None:
    @MockClass
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()  # type: ignore # noqa

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_plain_decorator_parentheses() -> None:
    @MockClass()
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()  # type: ignore # noqa

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_kwargs() -> None:
    @MockClass(param=123, other=True)
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()  # type: ignore # noqa

    assert my_func.args == ()
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs() -> None:
    @MockClass(123, True, param=123, other=True)
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()  # type: ignore # noqa

    assert my_func.args == (123, True)
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_fail_callable_decorator_no_args() -> None:
    with pytest.raises(TypeError):

        @callable_decorator_class
        class MockClassCallable:
            def __init__(self, func: Callable, *args: Any, **kwargs: Any) -> None:
                ...

            def __call__(self, *args, **kwargs):
                ...


def test_fail_callable_decorator_no_args_parentheses() -> None:
    with pytest.raises(TypeError):

        @callable_decorator_class()
        class MockClassCallable:
            def __init__(self, func: Callable, *args: Any, **kwargs: Any) -> None:
                ...

            def __call__(self, *args, **kwargs):
                ...


def test_fail_callable_decorator_args_kwargs() -> None:
    with pytest.raises(TypeError):

        @callable_decorator_class(123, True, param=123, other=True)
        class MockClassCallable:
            def __init__(self, func: Callable, *args: Any, **kwargs: Any) -> None:
                ...

            def __call__(self, *args, **kwargs):
                ...


def test_decorator_as_function() -> None:
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    my_decorated_func = MockClass(my_func)

    assert type(my_decorated_func) == MockClass
    with pytest.raises(TypeError):
        my_decorated_func()  # type: ignore # noqa

    assert my_decorated_func.args == ()
    assert my_decorated_func.kwargs == {}
    assert my_decorated_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_as_function_args_kwargs() -> None:
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    my_decorated_func = MockClass(my_func, 123, True, param=123, other=True)

    assert type(my_decorated_func) == MockClass
    with pytest.raises(TypeError):
        my_decorated_func()  # type: ignore # noqa

    assert my_decorated_func.args == (123, True)
    assert my_decorated_func.kwargs == dict(param=123, other=True)
    assert my_decorated_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_fail_decorator_as_function_no_args_no_func() -> None:
    my_func = MockClass()

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()  # type: ignore # noqa
    with pytest.raises(AttributeError):
        assert my_func.args == ()
    with pytest.raises(AttributeError):
        assert my_func.kwargs == {}


def test_fail_decorator_as_function_args_and_kwargs_no_func() -> None:
    my_func = MockClass(123, True, param=123, other=True)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()  # type: ignore # noqa
    with pytest.raises(AttributeError):
        assert my_func.args == ()
    with pytest.raises(AttributeError):
        assert my_func.kwargs == {}


def test_fail_double_decorator() -> None:
    def extra_decorator(func: Callable) -> Callable:
        return func

    with pytest.raises(TypeError):

        @MockClass(extra_decorator, 123, True, param=123, other=True)
        def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            return dict(args=args, kwargs=kwargs)
