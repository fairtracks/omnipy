from omnipy.util.decorators import add_callback_after_call


def test_callback_after_func_call() -> None:
    def my_appender(a: list[int], b: int) -> list[int]:
        a.append(b)
        return a

    def my_callback_after_call(x: list[int], *, y: int) -> None:
        x.append(0)

    my_list = [1, 2, 3]

    decorated_func = add_callback_after_call(my_appender, my_callback_after_call, my_list, y=0)

    ret_list = decorated_func(my_list, 4)
    assert ret_list == my_list == [1, 2, 3, 4, 0]
