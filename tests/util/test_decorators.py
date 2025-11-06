from typing import Callable

import pytest

from omnipy.util.contexts import hold_and_reset_prev_attrib_value
from omnipy.util.decorators import (add_callback_after_call,
                                    add_callback_if_exception,
                                    apply_decorator_to_property,
                                    call_super_if_available,
                                    class_or_instance_method,
                                    no_context)


def test_exception_callback_with_args() -> None:
    def concatenate(a: list[int], b: list[int]) -> list[int]:
        if a == [42]:
            raise ValueError('Not enough compute power')
        if a == [666]:
            raise RuntimeError('The End is Nigh!')
        return a + b

    def defensive_reverse_concatenator(a: list[int], b: list[int]) -> list[int]:
        return list(b) + list(a)

    concatenate_reverse_if_error = add_callback_if_exception(concatenate,
                                                             defensive_reverse_concatenator)
    assert concatenate_reverse_if_error([1, 2], [3, 4]) == [1, 2, 3, 4]
    assert concatenate_reverse_if_error((1, 2), [3, 4]) == [3, 4, 1, 2]  # type: ignore[arg-type]
    assert concatenate_reverse_if_error([42], [3, 4]) == [3, 4, 42]
    assert concatenate_reverse_if_error([666], [3, 4]) == [3, 4, 666]

    concatenate_reverse_if_error = add_callback_if_exception(concatenate,
                                                             defensive_reverse_concatenator,
                                                             (TypeError, ValueError))
    assert concatenate_reverse_if_error([1, 2], [3, 4]) == [1, 2, 3, 4]
    assert concatenate_reverse_if_error((1, 2), [3, 4]) == [3, 4, 1, 2]  # type: ignore[arg-type]
    assert concatenate_reverse_if_error([42], [3, 4]) == [3, 4, 42]
    with pytest.raises(RuntimeError):
        assert concatenate_reverse_if_error([666], [3, 4])


def test_callback_after_func_call() -> None:
    def my_appender(a: list[int], b: int) -> list[int]:
        a.append(b)
        return a

    def my_callback_after_call(ret: list[int] | None, x: int, *, y: int) -> list[int] | None:
        if ret is not None:
            ret.append(x)
            ret.append(y)
        return ret

    my_list = [1, 2, 3]

    decorated_my_appender = add_callback_after_call(
        my_appender, my_callback_after_call, no_context, 5, y=6)

    ret_list = decorated_my_appender(my_list, 4)
    assert ret_list == my_list == [1, 2, 3, 4, 5, 6]


def test_callback_after_func_call_with_attrib_holder_error_in_func() -> None:
    class A:
        def __init__(self, numbers: list[int]) -> None:
            self.numbers = numbers

    def my_appender(a: A, b: int) -> A:
        a.numbers.append(b)
        raise RuntimeError()

    def my_callback_after_call(ret: A | None, x: A, *, y: int) -> None:
        assert ret is None
        x.numbers.append(y)

    my_a = A([1, 2, 3])

    restore_numbers_context = hold_and_reset_prev_attrib_value(my_a, 'numbers', copy_attr=True)
    decorated_my_appender = add_callback_after_call(
        my_appender, my_callback_after_call, restore_numbers_context, my_a, y=0)

    try:
        decorated_my_appender(my_a, 4)
    except RuntimeError:
        pass

    assert my_a.numbers == [1, 2, 3]


def test_callback_after_func_call_with_attrib_holder_error_in_callback_func() -> None:
    class A:
        def __init__(self, numbers: list[int]) -> None:
            self.numbers = numbers

    def my_appender(a: A, b: int) -> A:
        a.numbers.append(b)
        return a

    def my_callback_after_call(ret: A | None, x: A, *, y: int) -> None:
        if ret is not None:
            ret.numbers.append(y)
        x.numbers.append(y)
        raise RuntimeError()

    my_a = A([1, 2, 3])
    my_other_a = A([1, 2, 3])

    restore_numbers_context = hold_and_reset_prev_attrib_value(my_a, 'numbers', copy_attr=True)
    decorated_my_appender = add_callback_after_call(
        my_appender, my_callback_after_call, restore_numbers_context, my_other_a, y=4)

    try:
        decorated_my_appender(my_a, 4)
    except RuntimeError:
        pass

    assert my_a.numbers == [1, 2, 3]
    assert my_other_a.numbers == [1, 2, 3, 4]


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

    MyDataGetter.data = apply_decorator_to_property(  # pyright: ignore
        MyDataGetter.data, my_decorator)
    MyDataSetter.data = apply_decorator_to_property(  # pyright: ignore
        MyDataSetter.data, my_decorator)
    MyDataDeleter.data = apply_decorator_to_property(  # pyright: ignore
        MyDataDeleter.data, my_decorator)

    assert MyDataGetter.data.__doc__ == 'data property documentation'
    assert MyDataSetter.data.__doc__ == 'data property documentation'
    assert MyDataDeleter.data.__doc__ == 'data property documentation'

    data_getter = MyDataGetter()
    assert call_counter == [0]

    assert data_getter.data is None
    assert call_counter == [1]

    with pytest.raises(AttributeError):
        data_getter.data = 'data'  # pyright: ignore
    assert call_counter == [1]

    data_setter = MyDataSetter()
    data_setter.data = 'data'
    assert call_counter == [2]

    assert data_setter.data == 'data'
    assert call_counter == [3]

    with pytest.raises(AttributeError):
        del data_getter.data  # pyright: ignore
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


def test_call_super_if_available() -> None:
    class MyClassWithoutSuper:
        @call_super_if_available(call_super_before_method=True)
        def my_method(self, number: int) -> int:
            return number + 1

        @call_super_if_available(call_super_before_method=False)
        def my_other_method(self, number: int) -> int:
            return number + 1

        @call_super_if_available(call_super_before_method=False)
        @classmethod
        def my_class_method(cls, number: int) -> int:
            return number + 1

    assert MyClassWithoutSuper().my_method(1) == 2
    assert MyClassWithoutSuper().my_other_method(1) == 2
    assert MyClassWithoutSuper.my_class_method(1) == 2

    class MyClassWithSuper(MyClassWithoutSuper):
        @call_super_if_available(call_super_before_method=True)
        def my_method(self, number: int) -> int:
            return number * 10

        @call_super_if_available(call_super_before_method=False)
        def my_other_method(self, number: int) -> int:
            return number * 10

        @call_super_if_available(call_super_before_method=False)
        @classmethod
        def my_class_method(cls, number: int) -> int:
            return number * 5

    #
    assert MyClassWithSuper().my_method(1) == 20
    assert MyClassWithSuper().my_other_method(1) == 11
    assert MyClassWithSuper.my_class_method(1) == 6


def test_class_or_instance_method() -> None:
    class MyClass:
        def __init__(self, a: int) -> None:
            self._a = a

        @class_or_instance_method
        def foo(self: 'MyClass | None', cls: 'type[MyClass]', b: int, c: int = 42) -> int:
            if self:
                return self._a + b + c
            else:
                return b + c

    assert MyClass.foo(10) == 52
    assert MyClass.foo(10, 10) == 20
    assert MyClass(48).foo(10) == 100
    assert MyClass(48).foo(10, 10) == 68
