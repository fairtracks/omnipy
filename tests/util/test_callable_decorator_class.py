from typing import Any, Callable, Dict

import pytest

from unifair.util.decorators import callable_decorator_class


@callable_decorator_class
class MockClass:
    def __init__(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs


def test_fail_plain_decorator_not_callable_arg() -> None:  # noqa
    with pytest.raises(AttributeError):

        @callable_decorator_class
        class MockClassNotCallableArg:  # noqa
            def __init__(self, text: str, *args: Any, **kwargs: Any) -> None:  # noqa
                self.text = text


def test_plain_decorator() -> None:  # noqa
    @MockClass
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()  # noqa

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_plain_decorator_parentheses() -> None:  # noqa
    @MockClass()
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()

    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_kwargs() -> None:  # noqa
    @MockClass(param=123, other=True)
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()

    assert my_func.args == ()
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs() -> None:  # noqa
    @MockClass(123, True, param=123, other=True)
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()

    assert my_func.args == (123, True)
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_as_function() -> None:  # noqa
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    my_decorated_func = MockClass(my_func)

    assert type(my_decorated_func) == MockClass
    with pytest.raises(TypeError):
        my_decorated_func()

    assert my_decorated_func.args == ()
    assert my_decorated_func.kwargs == {}
    assert my_decorated_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_as_function_args_kwargs() -> None:  # noqa
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    my_decorated_func = MockClass(my_func, 123, True, param=123, other=True)

    assert type(my_decorated_func) == MockClass
    with pytest.raises(TypeError):
        my_decorated_func()

    assert my_decorated_func.args == (123, True)
    assert my_decorated_func.kwargs == dict(param=123, other=True)
    assert my_decorated_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_fail_decorator_as_function_no_args_no_func() -> None:  # noqa
    my_func = MockClass()

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()
    with pytest.raises(AttributeError):
        assert my_func.args == ()
    with pytest.raises(AttributeError):
        assert my_func.kwargs == {}


def test_fail_decorator_as_function_args_and_kwargs_no_func() -> None:  # noqa
    my_func = MockClass(123, True, param=123, other=True)

    assert type(my_func) == MockClass
    with pytest.raises(TypeError):
        my_func()
    with pytest.raises(AttributeError):
        assert my_func.args == ()
    with pytest.raises(AttributeError):
        assert my_func.kwargs == {}


def test_fail_double_decorator() -> None:  # noqa
    def extra_decorator(func: Callable) -> Callable:
        return func

    with pytest.raises(TypeError):

        @MockClass(extra_decorator, 123, True, param=123, other=True)
        def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            return dict(args=args, kwargs=kwargs)
