"""Helper functions for compute tests."""

import asyncio
from random import random
import time

from omnipy.data.dataset import Dataset
from omnipy.data.model import Model


def action_func_no_params() -> None:
    # backend.do_something()
    """Return action func no parameters."""
    return


def action_func_with_params(command: str, verbose: bool = False) -> None:  # noqa
    # backend.run(command, verbose=verbose)
    """Return action func with parameters."""
    return


def data_import_func() -> str:
    """Return data import func."""
    return '{"my_data": [123,234,345,456]}'


def format_to_string_func(text: str, number: int) -> str:
    """Format to string func."""
    return '{}: {}'.format(text, number)


def power_m1_func(number: int | Model[int], exponent: int, minus_one: bool = True) -> int:
    """Return power m1 func."""
    return number**exponent - (1 if minus_one else 0)  # type: ignore[operator]


def empty_dict_func() -> dict:
    """Return empty dict func."""
    return {}


def plus_one_dict_func(number: int) -> dict[str, int]:
    """Return plus one dict func."""
    return {'number': number + 1}


def dict_of_squared_func(number: int) -> dict[int, int]:
    """Return dict of squared func."""
    return {val: val**2 for val in range(number)}


def kwargs_func(**kwargs: object) -> str:
    """Return kwargs func."""
    return repr(kwargs)


def args_func(*args: object) -> tuple[object, ...]:
    """Return args func."""
    return args


def all_int_dataset_plus_int_return_str_dataset_func(
    dataset: Dataset[Model[int]],
    number: int,
) -> Dataset[Model[str]]:
    """Return all int dataset plus int return string dataset func."""
    out_dataset = Dataset[Model[str]]()
    for title, data_file in dataset.items():
        out_dataset[title] = data_file + number
    return out_dataset


async def async_all_int_dataset_plus_int_return_str_dataset_func(
        dataset: Dataset[Model[int]], number: int) -> Dataset[Model[str]]:
    """Run async all int dataset plus int return string dataset func."""
    await asyncio.sleep(0.1)
    return all_int_dataset_plus_int_return_str_dataset_func(dataset, number)


def single_int_model_plus_int_return_str_model_func(
    data_number: Model[int],
    number: int,
) -> Model[str]:
    """Return single int model plus int return string model func."""
    return str(data_number.content + number)  # type: ignore[return-value]


def single_int_model_plus_default_int_pair_return_str_model_func(
    data_number: Model[int],
    number: int = 0,
    other_number: int = 0,
) -> Model[str]:
    """Return single int model plus default int pair return string model func."""
    return str(data_number.content + number + other_number)  # type: ignore[return-value]


def single_int_plus_int_return_str_func(data_number: int, number: int) -> str:
    """Return single int plus int return string func."""
    return str(data_number + number)


def single_int_plus_int_return_str_model_with_output_str_dataset_func(
    data_number: int,
    number: int,
    output_dataset: Dataset[Model[str]],
) -> Model[str]:
    """Return single int plus int return string model with output string dataset func."""
    return str(data_number + number)  # type: ignore[return-value]


def single_int_plus_int_return_str_with_output_int_dataset_func(
    data_number: int,
    number: int,
    output_dataset: Dataset[Model[int]],
) -> str:
    """Return single int plus int return string with output int dataset func."""
    return str(data_number + number)


async def async_single_int_model_plus_int_return_str_model_func(
    data_number: Model[int],
    number: int,
) -> Model[str]:
    """Run async single int model plus int return string model func."""
    await asyncio.sleep(random() / 10.0)
    return str(data_number.content + number)  # type: ignore[return-value]


async def async_single_int_plus_int_return_str_func(data_number: int, number: int) -> str:
    """Run async single int plus int return string func."""
    await asyncio.sleep(random() / 10.0)
    return str(data_number + number)


async def async_single_int_plus_future_return_alphanum_string_func(
    data_number: int,
    number: int,
) -> str:
    """Run async single int plus future return alphanum string func."""
    await asyncio.sleep(random() / 10.0)
    return f'Answer: {data_number + number}'


async def async_single_int_plus_int_return_str_model_with_output_str_dataset_func(
    data_number: int,
    number: int,
    output_dataset: Dataset[Model[str]],
) -> Model[str]:
    """Run async single int plus int return string model with output string dataset func."""
    await asyncio.sleep(random() / 10.0)
    return str(data_number + number)  # type: ignore[return-value]


async def async_single_int_plus_future_int_return_str_func(
    data_number: int,
    number: asyncio.Future[int],
) -> str:
    """Run async single int plus future int return string func."""
    await number
    return str(data_number + number.result())


async def async_single_int_plus_future_int_fail_func(
    data_number: int,
    number: asyncio.Future[int],
) -> str:
    """Run async single int plus future int fail func."""
    await number
    raise RuntimeError('Boom!')


async def async_sleep_random_time_func() -> float:
    """Run async sleep random time func."""
    seconds: float = random() / 10
    await asyncio.sleep(seconds)
    return seconds


def sync_sleep_random_time_func() -> float:
    """Run sync sleep random time func."""
    seconds: float = random() / 10
    time.sleep(seconds)
    return seconds
