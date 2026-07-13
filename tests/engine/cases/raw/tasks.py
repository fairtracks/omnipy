import asyncio
from typing import AsyncGenerator, AsyncIterator, Generator

from omnipy.compute.task import TaskTemplate


@TaskTemplate()
def add_one(number: int) -> int:
    return number + 1


@TaskTemplate()
def add_two(number: int) -> int:
    return number + 2


@TaskTemplate()
def add_three(number: int) -> int:
    return number + 3


@TaskTemplate()
def add_four(number: int) -> int:
    return number + 4


@TaskTemplate()
def add_five(number: int) -> int:
    return number + 5


@TaskTemplate()
def add_ten(number: int) -> int:
    return number + 10


@TaskTemplate()
def subtract_one(number: int) -> int:
    return number - 1


@TaskTemplate()
def subtract_two(number: int) -> int:
    return number - 2


@TaskTemplate()
def subtract_three(number: int) -> int:
    return number - 3


@TaskTemplate()
def double_number(number: int) -> int:
    return number * 2


@TaskTemplate()
def square_number(number: int) -> int:
    return number * number


@TaskTemplate()
def multiply_by_three(number: int) -> int:
    return number * 3


@TaskTemplate()
def multiply_by_four(number: int) -> int:
    return number * 4


@TaskTemplate()
def add_two_numbers(left_value: int, right_value: int) -> int:
    return left_value + right_value


@TaskTemplate()
def subtract_numbers(minuend: int, subtrahend: int) -> int:
    return minuend - subtrahend


@TaskTemplate()
def multiply_numbers(left_value: int, right_value: int) -> int:
    return left_value * right_value


@TaskTemplate()
def sum_values(values: Generator) -> int:
    return sum(values)


@TaskTemplate()
def pass_async_values_through(values: AsyncGenerator) -> AsyncIterator[int]:
    return values


@TaskTemplate()
def compute_base_dict(number: int) -> dict[str, int]:
    return {'base': number + 1}


@TaskTemplate()
def emit_three_values(number: int) -> Generator:
    for value in range(number, number + 3):
        yield value


@TaskTemplate()
def emit_sync_doubled_values(values: Generator) -> Generator:
    for value in values:
        yield value * 2


@TaskTemplate()
def emit_sync_wrapped_async_values(values: AsyncGenerator) -> Generator:
    yield values


@TaskTemplate()
def generate_square_sequence(count: int) -> Generator:
    for value in range(count):
        yield value * value


@TaskTemplate()
async def async_double_number(number: int) -> int:
    await asyncio.sleep(0)
    return number * 2


@TaskTemplate()
async def async_add_five(number: int) -> int:
    await asyncio.sleep(0)
    return number + 5


@TaskTemplate()
async def async_add_ten(number: int) -> int:
    await asyncio.sleep(0)
    return number + 10


@TaskTemplate()
async def wait_and_double_milliseconds(milliseconds: int) -> int:
    await asyncio.sleep(milliseconds / 1000)
    return milliseconds * 2


@TaskTemplate()
async def sum_async_values(values: AsyncGenerator) -> int:
    total = 0
    async for value in values:
        total += value
    return total


@TaskTemplate()
async def sum_values_async(values: Generator) -> int:
    await asyncio.sleep(0)
    return sum(values) * 2


@TaskTemplate()
async def emit_async_values(number: int) -> AsyncGenerator:
    for value in range(number, number + 3):
        await asyncio.sleep(0)
        yield value


@TaskTemplate()
async def emit_doubled_async_values(values: AsyncGenerator) -> AsyncGenerator:
    async for value in values:
        await asyncio.sleep(0)
        yield value * 2


@TaskTemplate()
async def emit_doubled_sync_values_as_async(values: Generator) -> AsyncGenerator:
    for value in values:
        await asyncio.sleep(0)
        yield value * 2
