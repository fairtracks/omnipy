import sys
from textwrap import dedent
from typing import Annotated, Callable, TypeAlias

import pytest

from omnipy.util.contexts import (AttribHolder,
                                  LastErrorHolder,
                                  print_exception,
                                  setup_and_teardown_callback_context)

StateAndSetupTeardownFuncs: TypeAlias = tuple[list[int],
                                              Callable[[int], None],
                                              Callable[[int], None]]


@pytest.fixture
def state_and_setup_teardown_funcs() -> StateAndSetupTeardownFuncs:
    state = []
    default_num = 123

    def setup(number: int = default_num):
        state.append(number)

    def teardown(number: int = default_num):
        assert state[0] == number
        del state[0]

    return state, setup, teardown


def test_setup_and_teardown_callback_context_no_args(
        state_and_setup_teardown_funcs: Annotated[StateAndSetupTeardownFuncs,
                                                  pytest.fixture]) -> None:
    state, setup, teardown = state_and_setup_teardown_funcs

    with setup_and_teardown_callback_context(
            setup_func=setup,
            teardown_func=teardown,
    ):
        assert state == [123]

    assert state == []


def test_setup_and_teardown_callback_context_with_exception(
        state_and_setup_teardown_funcs: Annotated[StateAndSetupTeardownFuncs,
                                                  pytest.fixture]) -> None:
    state, setup, teardown = state_and_setup_teardown_funcs
    try:
        with setup_and_teardown_callback_context(
                setup_func=setup,
                teardown_func=teardown,
        ):
            assert state == [123]
            raise RuntimeError("Whoops! Something went wrong...")
    except RuntimeError:
        pass

    assert state == []


def test_setup_and_teardown_callback_context_args(
        state_and_setup_teardown_funcs: Annotated[StateAndSetupTeardownFuncs,
                                                  pytest.fixture]) -> None:
    state, setup, teardown = state_and_setup_teardown_funcs

    with setup_and_teardown_callback_context(
            setup_func=setup,
            setup_func_args=(234,),
            teardown_func=teardown,
            teardown_func_args=(234,),
    ):
        assert state == [234]

    assert state == []


def test_setup_and_teardown_callback_context_kwargs(
        state_and_setup_teardown_funcs: Annotated[StateAndSetupTeardownFuncs,
                                                  pytest.fixture]) -> None:
    state, setup, teardown = state_and_setup_teardown_funcs

    with setup_and_teardown_callback_context(
            setup_func=setup,
            setup_func_kwargs=dict(number=345),
            teardown_func=teardown,
            teardown_func_kwargs=dict(number=345),
    ):
        assert state == [345]

    assert state == []


def test_setup_and_teardown_callback_context_no_teardown_func(
        state_and_setup_teardown_funcs: Annotated[StateAndSetupTeardownFuncs,
                                                  pytest.fixture]) -> None:
    state, setup, teardown = state_and_setup_teardown_funcs

    with setup_and_teardown_callback_context(
            setup_func=setup,
            setup_func_args=(234,),
    ):
        assert state == [234]

    assert state == [234]


def test_setup_and_teardown_callback_context_no_setup_func(
        state_and_setup_teardown_funcs: Annotated[StateAndSetupTeardownFuncs,
                                                  pytest.fixture]) -> None:
    state, setup, teardown = state_and_setup_teardown_funcs

    state.append(234)

    with setup_and_teardown_callback_context(
            teardown_func=teardown,
            teardown_func_args=(234,),
    ):
        assert state == [234]

    assert state == []


def test_capture_stdout_stderr(capsys: pytest.CaptureFixture) -> None:
    print('To be or not to be, that is the question', end='')
    print('Something is rotten in the state of Denmark', end='', file=sys.stderr)

    captured = capsys.readouterr()
    assert captured.out == 'To be or not to be, that is the question'
    assert captured.err == 'Something is rotten in the state of Denmark'


def test_print_exception(capsys: pytest.CaptureFixture) -> None:
    with print_exception:
        'a' + 1  # type: ignore

    captured = capsys.readouterr()
    assert captured.out == 'TypeError: can only concatenate str (not "int") to str'

    with print_exception:
        raise NotImplementedError(
            dedent("""\
            Multi-line error!
            - More info here..
            - And here are the nitty gritty details..."""))

    captured = capsys.readouterr()  # type: ignore
    assert captured.out == 'NotImplementedError: Multi-line error!'


def _raise_if_even_for_range(count: int):
    def raise_if_even(a: int):
        if a % 2 == 0:
            raise ValueError(f'a={a} is even')

    iterable = range(count)

    last_error_holder = LastErrorHolder()
    for item in iterable:
        with last_error_holder:
            raise_if_even(item)

    last_error_holder.raise_derived(EOFError(f'No more numbers, last was: {item}'))


def test_with_last_error() -> None:
    with pytest.raises(EOFError, match='last was: 0') as exc_info:
        _raise_if_even_for_range(1)

    assert 'a=0 is even' in str(exc_info.getrepr())

    with pytest.raises(EOFError, match='last was: 2') as exc_info:
        _raise_if_even_for_range(3)

    assert 'a=2 is even' in str(exc_info.getrepr())

    with pytest.raises(EOFError, match='last was: 5') as exc_info:
        _raise_if_even_for_range(6)

    assert 'a=4 is even' in str(exc_info.getrepr())


def test_attrib_holder_init() -> None:
    class A:
        def __init__(self, num: int) -> None:
            self.num = num

    a = A(5)

    with pytest.raises(AssertionError):
        AttribHolder(a, 'num', reset_to_other=True)

    with pytest.raises(AssertionError):
        AttribHolder(a, 'num', switch_to_other=True)

    with pytest.raises(AssertionError):
        AttribHolder(a, 'num', 9)

    with pytest.raises(AssertionError):
        AttribHolder(a, 'num', 9, reset_to_other=True, switch_to_other=True)


def test_with_class_attrib_holder_reset_attr_if_exception() -> None:
    class A:
        ...

    class B:
        def __init__(self, num: int) -> None:
            self.num = num

    a = A()
    with AttribHolder(a, 'num') as ms:
        assert ms._prev_value is None

    b = B(5)
    with AttribHolder(b, 'num') as ms:
        b.num = 7
        assert ms._prev_value == 5
    assert b.num == 7

    try:
        b.num = 5
        with AttribHolder(b, 'num') as ms:
            b.num = 7
            assert ms._prev_value == 5
            raise RuntimeError()
    except RuntimeError:
        pass
    assert b.num == 5


def test_with_class_attrib_holder_set_attr_to_other_if_exception() -> None:
    class A:
        def __init__(self, num: int) -> None:
            self.num = num

    a = A(5)

    try:
        a.num = 5
        with AttribHolder(a, 'num', 9, reset_to_other=True) as ms:
            a.num = 7
            assert ms._prev_value is None
            raise RuntimeError()
    except RuntimeError:
        pass
    assert a.num == 9


def test_with_class_attrib_holder_reset_attr_if_exception_deepcopy() -> None:
    class B:
        def __init__(self, numbers: list[list[int]]) -> None:
            self.numbers = numbers

    b = B([[5]])
    try:
        with AttribHolder(b, 'numbers') as ms:
            b.numbers[0][0] += 2
            assert b.numbers == [[7]]
            assert ms._prev_value == [[7]]
            raise RuntimeError()
    except RuntimeError:
        pass
    assert b.numbers == [[7]]

    try:
        b.numbers = [[5]]
        with AttribHolder(b, 'numbers', copy_attr=True) as ms:
            b.numbers[0][0] += 2
            assert b.numbers == [[7]]
            assert ms._prev_value == [[5]]
            raise RuntimeError()
    except RuntimeError:
        pass
    assert b.numbers == [[5]]


def test_with_class_attrib_holder_method_switching() -> None:
    class A:
        ...

    class B:
        def method(self):
            return 'method'

    def other_method(self):
        return 'other_method'

    a = A()
    with AttribHolder(a, 'method', other_method, switch_to_other=True, on_class=True) as ms:
        assert ms._prev_value is None
        with pytest.raises(AttributeError):
            a.method()  # type: ignore

    A.method = other_method

    a = A()
    with AttribHolder(a, 'method', other_method, switch_to_other=True, on_class=True) as ms:
        assert a.method() == 'other_method'  # type: ignore
        assert ms._prev_value is None

    b = B()
    with AttribHolder(b, 'method', other_method, switch_to_other=True, on_class=True) as ms:
        assert b.method() == 'other_method'
        assert ms._prev_value.__name__ == 'method'
    assert b.method() == 'method'

    b = B()
    try:
        with AttribHolder(b, 'method', other_method, switch_to_other=True, on_class=True) as ms:
            assert b.method() == 'other_method'
            assert ms._prev_value.__name__ == 'method'
            raise RuntimeError()
    except RuntimeError:
        pass
    assert b.method() == 'method'
