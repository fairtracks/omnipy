from typing import Callable

import pytest

from omnipy.util.contexts import AttribHolder
from omnipy.util.decorators import add_callback_after_call, apply_decorator_to_property


def test_callback_after_func_call() -> None:
    def my_appender(a: list[int], b: int) -> list[int]:
        a.append(b)
        return a

    def my_callback_after_call(x: list[int], *, y: int) -> None:
        x.append(y)

    my_list = [1, 2, 3]

    decorated_my_appender = add_callback_after_call(
        my_appender, my_callback_after_call, my_list, y=0)

    ret_list = decorated_my_appender(my_list, 4)
    assert ret_list == my_list == [1, 2, 3, 4, 0]


def test_callback_after_func_call_with_attrib_holder_error_in_func() -> None:
    class A:
        def __init__(self, numbers: list[int]) -> None:
            self.numbers = numbers

    def my_appender(a: A, b: int) -> list[int]:
        a.numbers.append(b)
        raise RuntimeError()

    def my_callback_after_call(x: A, *, y: int) -> None:
        x.numbers.append(y)

    my_a = A([1, 2, 3])

    restore_numbers = AttribHolder(my_a, 'numbers', copy_attr=True)
    decorated_my_appender = add_callback_after_call(
        my_appender, my_callback_after_call, my_a, y=0, with_context=restore_numbers)

    try:
        decorated_my_appender(my_a, 4)
    except RuntimeError:
        pass

    assert my_a.numbers == [1, 2, 3]


def test_callback_after_func_call_with_attrib_holder_error_in_callback_func() -> None:
    class A:
        def __init__(self, numbers: list[int]) -> None:
            self.numbers = numbers

    def my_appender(a: A, b: int) -> list[int]:
        a.numbers.append(b)
        return a

    def my_callback_after_call(x: A, *, y: int) -> None:
        x.numbers.append(y)
        raise RuntimeError()

    my_a = A([1, 2, 3])

    restore_numbers = AttribHolder(my_a, 'numbers', copy_attr=True)
    decorated_my_appender = add_callback_after_call(
        my_appender, my_callback_after_call, my_a, y=0, with_context=restore_numbers)

    try:
        decorated_my_appender(my_a, 4)
    except RuntimeError:
        pass

    assert my_a.numbers == [1, 2, 3]


def test_apply_decorator_to_property():
    class MyDataGetter:
        def __init__(self) -> None:
            self._data: str | None = None

        @property
        def data(self):
            """data property documentation"""
            return self._data

    class MyDataSetter(MyDataGetter):
        @MyDataGetter.data.setter
        def data(self, value: str):
            self._data = value

    class MyDataDeleter(MyDataSetter):
        @MyDataSetter.data.deleter
        def data(self):
            self._data = None

    call_counter = [0]

    def my_decorator(func: Callable) -> Callable:
        def _inner(*args: object, **kwargs: object) -> None:
            call_counter[0] += 1
            return func(*args, **kwargs)

        return _inner

    MyDataGetter.data = apply_decorator_to_property(MyDataGetter.data, my_decorator)
    MyDataSetter.data = apply_decorator_to_property(MyDataSetter.data, my_decorator)
    MyDataDeleter.data = apply_decorator_to_property(MyDataDeleter.data, my_decorator)

    assert MyDataGetter.data.__doc__ == 'data property documentation'
    assert MyDataSetter.data.__doc__ == 'data property documentation'
    assert MyDataDeleter.data.__doc__ == 'data property documentation'

    data_getter = MyDataGetter()
    assert call_counter == [0]

    assert data_getter.data is None
    assert call_counter == [1]

    with pytest.raises(AttributeError):
        data_getter.data = 'data'
    assert call_counter == [1]

    data_setter = MyDataSetter()
    data_setter.data = 'data'
    assert call_counter == [2]

    assert data_setter.data == 'data'
    assert call_counter == [3]

    with pytest.raises(AttributeError):
        del data_getter.data
    assert call_counter == [3]

    data_deleter = MyDataDeleter()
    data_deleter.data = 'data'
    assert call_counter == [4]

    assert data_setter.data == 'data'
    assert call_counter == [5]

    del data_deleter.data
    assert call_counter == [6]

    assert data_deleter.data is None
    assert call_counter == [7]
