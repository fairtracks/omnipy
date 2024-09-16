from contextlib import suppress
import sys
from textwrap import dedent
from typing import Callable, TypeAlias

import pytest

from omnipy.util.contexts import (hold_and_reset_prev_attrib_value,
                                  LastErrorHolder,
                                  print_exception,
                                  setup_and_teardown_callback_context)

StateAndSetupTeardownFuncs: TypeAlias = tuple[list[int],
                                              Callable[[int], None],
                                              Callable[[int], None],
                                              Callable[[int], None]]


@pytest.fixture
def state_and_callback_funcs() -> StateAndSetupTeardownFuncs:
    state = []
    default_num = 123

    def setup(number: int = default_num) -> int:
        state.append(number)
        return number

    def exception(number: int = default_num):
        state.append(-number)

    def teardown(number: int = default_num):
        assert state[0] == number
        del state[0]

    return state, setup, exception, teardown


def test_setup_and_teardown_callback_context_no_args(state_and_callback_funcs) -> None:
    state, setup, exception, teardown = state_and_callback_funcs

    with setup_and_teardown_callback_context(
            setup_func=setup,
            exception_func=exception,
            teardown_func=teardown,
    ) as number:
        assert number == 123
        assert state == [123]

    assert state == []


def test_setup_and_teardown_callback_context_with_exception(state_and_callback_funcs) -> None:
    state, setup, exception, teardown = state_and_callback_funcs

    try:
        with setup_and_teardown_callback_context(
                setup_func=setup,
                exception_func=exception,
                teardown_func=teardown,
        ) as number:
            assert number == 123
            assert state == [123]
            raise RuntimeError('Whoops! Something went wrong...')
    except RuntimeError:
        pass

    assert state == [-123]


def test_setup_and_teardown_callback_context_args_with_exception(state_and_callback_funcs) -> None:
    state, setup, exception, teardown = state_and_callback_funcs

    try:
        with setup_and_teardown_callback_context(
                setup_func=setup,
                setup_func_args=(234,),
                exception_func=exception,
                exception_func_args=(234,),
                teardown_func=teardown,
                teardown_func_args=(234,),
        ) as number:
            assert number == 234
            assert state == [234]
            raise RuntimeError('Whoops! Something went wrong...')
    except RuntimeError:
        pass

    assert state == [-234]


def test_setup_and_teardown_callback_context_kwargs_with_exception(
        state_and_callback_funcs) -> None:
    state, setup, exception, teardown = state_and_callback_funcs

    try:
        with setup_and_teardown_callback_context(
                setup_func=setup,
                setup_func_kwargs=dict(number=345),
                exception_func=exception,
                exception_func_kwargs=dict(number=345),
                teardown_func=teardown,
                teardown_func_kwargs=dict(number=345),
        ) as number:
            assert number == 345
            assert state == [345]
            raise RuntimeError('Whoops! Something went wrong...')
    except RuntimeError:
        pass

    assert state == [-345]


def test_setup_and_teardown_callback_context_only_setup_func(state_and_callback_funcs) -> None:
    state, setup, exception, teardown = state_and_callback_funcs

    try:
        with setup_and_teardown_callback_context(
                setup_func=setup,
                setup_func_args=(234,),
        ) as number:
            assert number == 234
            assert state == [234]
            raise RuntimeError('Whoops! Something went wrong...')
    except RuntimeError:
        pass

    assert state == [234]


def test_setup_and_teardown_callback_context_only_exception_func(state_and_callback_funcs) -> None:
    state, setup, exception, teardown = state_and_callback_funcs

    try:
        with setup_and_teardown_callback_context(
                exception_func=exception,
                exception_func_args=(234,),
        ) as number:
            assert number is None
            assert state == []
            raise RuntimeError('Whoops! Something went wrong...')
    except RuntimeError:
        pass

    assert state == [-234]


def test_setup_and_teardown_callback_context_only_teardown_func(state_and_callback_funcs) -> None:
    state, setup, exception, teardown = state_and_callback_funcs

    state.append(234)

    try:
        with setup_and_teardown_callback_context(
                teardown_func=teardown,
                teardown_func_args=(234,),
        ) as number:
            assert number is None
            assert state == [234]
            raise RuntimeError('Whoops! Something went wrong...')
    except RuntimeError:
        pass

    assert state == []


def test_setup_and_teardown_callback_context_as_decorator(state_and_callback_funcs) -> None:
    state, setup, exception, teardown = state_and_callback_funcs

    @setup_and_teardown_callback_context(
        setup_func=setup,
        setup_func_kwargs=dict(number=75),
        exception_func=exception,
        exception_func_args=(100,),
        teardown_func=teardown,
        teardown_func_kwargs=dict(number=75),
    )
    def in_range(max: int, min: int = 0) -> bool:
        ok = min <= state[-1] <= max
        if not ok:
            raise RuntimeError(f'{state[-1]} not in range {min} to {max}')
        return ok

    assert in_range(100, min=50)
    assert state == []

    try:
        assert in_range(200, min=100)
    except RuntimeError:
        assert state == [-100]


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


def test_hold_and_reset_prev_attrib_value_at_teardown_and_exception() -> None:
    class A:
        ...

    class B:
        def __init__(self, num: int) -> None:
            self.num = num

    a = A()
    with pytest.raises(AttributeError):
        with hold_and_reset_prev_attrib_value(a, 'num'):
            pass

    b = B(5)
    with hold_and_reset_prev_attrib_value(b, 'num'):
        b.num = 7
    assert b.num == 5

    with suppress(RuntimeError):
        b.num = 5
        with hold_and_reset_prev_attrib_value(b, 'num'):
            b.num = 7
            raise RuntimeError()
    assert b.num == 5


def test_hold_and_reset_prev_attrib_value_at_exception_deepcopy() -> None:
    class B:
        def __init__(self, numbers: list[list[int]]) -> None:
            self.numbers = numbers

    b = B([[5]])

    with suppress(RuntimeError):
        with hold_and_reset_prev_attrib_value(b, 'numbers'):
            b.numbers[0][0] += 2
            assert b.numbers == [[7]]
            raise RuntimeError()
    assert b.numbers == [[7]]

    with suppress(RuntimeError):
        b.numbers = [[5]]
        with hold_and_reset_prev_attrib_value(b, 'numbers', copy_attr=True):
            b.numbers[0][0] += 2
            assert b.numbers == [[7]]
            raise RuntimeError()
    assert b.numbers == [[5]]
