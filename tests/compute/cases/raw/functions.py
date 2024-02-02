from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


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


def power_m1_func(number: int | Model[int], exponent: int, minus_one: bool = True) -> int:
    return number**exponent - (1 if minus_one else 0)


def empty_dict_func() -> dict:
    return {}


def plus_one_dict_func(number: int) -> dict[str, int]:
    return {'number': number + 1}


def dict_of_squared_func(number: int) -> dict[int, int]:
    return {val: val**2 for val in range(number)}


def kwargs_func(**kwargs: object) -> str:
    return repr(kwargs)


def all_data_files_plus_str_func(dataset: Dataset[Model[int]], number: int) -> Dataset[Model[str]]:
    out_dataset = Dataset[Model[str]]()
    for title, data_file in dataset.items():
        out_dataset[title] = data_file + number
    return out_dataset


def single_data_file_plus_str_func(data_number: Model[int], number: int) -> str:
    return str(data_number + number)
