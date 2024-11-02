import asyncio
from random import random
import time

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


def all_int_dataset_plus_int_return_str_dataset_func(
    dataset: Dataset[Model[int]],
    number: int,
) -> Dataset[Model[str]]:
    out_dataset = Dataset[Model[str]]()
    for title, data_file in dataset.items():
        out_dataset[title] = data_file + number
    return out_dataset


async def async_all_int_dataset_plus_int_return_str_dataset_func(
        dataset: Dataset[Model[int]], number: int) -> Dataset[Model[str]]:
    await asyncio.sleep(0.1)
    return all_int_dataset_plus_int_return_str_dataset_func(dataset, number)


def single_int_model_plus_int_return_str_model_func(
    data_number: Model[int],
    number: int,
) -> Model[str]:
    return str(data_number.contents + number)


def single_int_plus_int_return_str_func(data_number: int, number: int) -> str:
    return str(data_number + number)


def single_int_plus_int_return_str_model_with_output_str_dataset_func(
    data_number: int,
    number: int,
    output_dataset: Dataset[Model[str]],
) -> Model[str]:
    return str(data_number + number)


def single_int_plus_int_return_str_with_output_int_dataset_func(
    data_number: int,
    number: int,
    output_dataset: Dataset[Model[int]],
) -> str:
    return str(data_number + number)


async def async_single_int_model_plus_int_return_str_model_func(
    data_number: Model[int],
    number: int,
) -> Model[str]:
    await asyncio.sleep(random() / 10.0)
    return str(data_number.contents + number)


async def async_single_int_plus_int_return_str_func(data_number: int, number: int) -> str:
    await asyncio.sleep(random() / 10.0)
    return str(data_number + number)


async def async_single_int_plus_future_return_alphanum_string_func(
    data_number: int,
    number: int,
) -> str:
    await asyncio.sleep(random() / 10.0)
    return f'Answer: {data_number + number}'


async def async_single_int_plus_int_return_str_model_with_output_str_dataset_func(
    data_number: int,
    number: int,
    output_dataset: Dataset[Model[str]],
) -> Model[str]:
    await asyncio.sleep(random() / 10.0)
    return str(data_number + number)


async def async_single_int_plus_future_int_return_str_func(
    data_number: int,
    number: asyncio.Future[int],
) -> str:
    await number
    return str(data_number + number.result())


async def async_single_int_plus_future_int_fail_func(
    data_number: int,
    number: asyncio.Future[int],
) -> str:
    await number
    raise RuntimeError('Boom!')


async def async_sleep_random_time_func() -> float:
    seconds: float = random() / 10
    await asyncio.sleep(seconds)
    return seconds


def sync_sleep_random_time_func() -> float:
    seconds: float = random() / 10
    time.sleep(seconds)
    return seconds
