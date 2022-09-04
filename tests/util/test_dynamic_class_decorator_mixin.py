from typing import Any, Callable, Dict, Type

import pytest

from unifair.util.mixins import DynamicClassDecoratorMixin


@pytest.fixture()
def MockClass():  # noqa
    class MockClass(DynamicClassDecoratorMixin):
        def __init__(self, func: Callable, *args: Any, **kwargs: Any) -> None:
            self.func = func
            self.args = args
            self.kwargs = kwargs

    return MockClass


def test_plain_decorator(MockClass: Type) -> None:  # noqa
    @MockClass
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    assert my_func.args == ()
    assert my_func.kwargs == {}
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_kwargs(MockClass: Type) -> None:  # noqa
    @MockClass(param=123, other=True)
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    assert my_func.args == ()
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_with_args_and_kwargs(MockClass: Type) -> None:  # noqa
    @MockClass(123, True, param=123, other=True)
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    assert type(my_func) == MockClass
    assert my_func.args == (123, True)
    assert my_func.kwargs == dict(param=123, other=True)
    assert my_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_decorator_as_function(MockClass: Type) -> None:  # noqa
    def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return dict(args=args, kwargs=kwargs)

    my_decorated_func = MockClass(my_func, 123, True, param=123, other=True)

    assert type(my_decorated_func) == MockClass
    assert my_decorated_func.args == (123, True)
    assert my_decorated_func.kwargs == dict(param=123, other=True)
    assert my_decorated_func.func(1, 'b', c=True) == dict(args=(1, 'b'), kwargs=dict(c=True))


def test_double_decorator(MockClass: Type) -> None:  # noqa
    def extra_decorator(func: Callable) -> Callable:
        return func

    with pytest.raises(TypeError):

        @MockClass(extra_decorator, 123, True, param=123, other=True)
        def my_func(*args: Any, **kwargs: Any) -> Dict[str, Any]:
            return dict(args=args, kwargs=kwargs)
