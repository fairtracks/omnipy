from typing import Dict


def action_func_no_params() -> None:
    # backend.do_something()
    return


def action_func_with_params(command: str, *, verbose: bool = False) -> None:  # noqa
    # backend.run(command, verbose=verbose)
    return


def data_import_func() -> str:
    return '{"my_data": [123,234,345,456]}'


def format_to_string_func(text: str, number: int) -> str:
    return '{}: {}'.format(text, number)


def power_m1_func(number: int, exponent: int, minus_one: bool = True) -> int:
    return number**exponent - (1 if minus_one else 0)


def empty_dict_func() -> Dict:
    return {}


def plus_one_dict_func(number: int) -> Dict[str, int]:
    return {'number': number + 1}


def dict_of_squared_func(number: int) -> Dict[int, int]:
    return {val: val**2 for val in range(number)}
