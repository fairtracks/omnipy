from typing import Callable

import pytest


@pytest.fixture(scope='module')
def action_func_no_params() -> Callable[[], None]:
    def action_func_no_params() -> None:
        # backend.do_something()
        return

    return action_func_no_params


@pytest.fixture(scope='module')
def action_func_with_params() -> Callable[[str, bool], None]:
    def action_func_with_params(command: str, *, verbose: bool = False) -> None:  # noqa
        # backend.run(command, verbose=verbose)
        return

    return action_func_with_params


@pytest.fixture(scope='module')
def data_import_func() -> Callable[[], str]:
    def data_import_func() -> str:
        return '{"my_data": [123,234,345,456]}'

    return data_import_func


@pytest.fixture(scope='module')
def format_to_string_func() -> Callable[[str, int], str]:
    def format_to_string_func(text: str, number: int) -> str:
        return '{}: {}'.format(text, number)

    return format_to_string_func


@pytest.fixture(scope='module')
def power_m1_func() -> Callable[[int, int, bool], int]:
    def power_m1_func(number: int, exponent: int, minus_one: bool = True) -> int:
        return number**exponent - (1 if minus_one else 0)

    return power_m1_func
