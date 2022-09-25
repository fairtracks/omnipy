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
