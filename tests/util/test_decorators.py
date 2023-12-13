from omnipy.util.contexts import AttribHolder
from omnipy.util.decorators import add_callback_after_call


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
