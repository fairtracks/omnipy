import asyncio
from typing import AsyncGenerator, AsyncIterator, Generator

from omnipy.compute.task import TaskTemplate


## Sync scalar tasks: unary int -> int


@TaskTemplate()
def add_one(number: int) -> int:
    return number + 1


@TaskTemplate()
def add_two(number: int) -> int:
    return number + 2


@TaskTemplate()
def double_number(number: int) -> int:
    return number * 2


@TaskTemplate()
def square_number(number: int) -> int:
    return number * number


## Sync scalar tasks: binary (int, int) -> int


@TaskTemplate()
def add_two_numbers(left_value: int, right_value: int) -> int:
    return left_value + right_value


@TaskTemplate()
def subtract_numbers(minuend: int, subtrahend: int) -> int:
    return minuend - subtrahend


@TaskTemplate()
def multiply_numbers(left_value: int, right_value: int) -> int:
    return left_value * right_value


## Sync reducer tasks: Generator -> int


@TaskTemplate()
def sum_values(values: Generator) -> int:
    return sum(values)


## Sync adapter tasks: structural special cases


@TaskTemplate()
def pass_async_values_through(values: AsyncGenerator) -> AsyncIterator[int]:
    return values


@TaskTemplate()
def compute_base(number: int) -> dict[str, int]:
    return {'base': number + 1}


## Sync generator tasks


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
def generate_window(start: int, window_size: int) -> Generator:
    for value in range(start, start + window_size):
        yield value


## Async scalar tasks: unary int -> int


@TaskTemplate()
async def async_double_number(number: int) -> int:
    await asyncio.sleep(0)
    return number * 2


## Async scalar tasks: timing-sensitive


@TaskTemplate()
async def wait_and_double_milliseconds(milliseconds: int) -> int:
    await asyncio.sleep(milliseconds / 1000)
    return milliseconds * 2


@TaskTemplate()
async def wait_and_return_milliseconds(milliseconds: int) -> int:
    await asyncio.sleep(milliseconds / 1000)
    return milliseconds + 1


@TaskTemplate()
async def multiply_milliseconds_after_wait(wait_milliseconds: int, multiplier: int) -> int:
    await asyncio.sleep(wait_milliseconds / 1000)
    return wait_milliseconds * multiplier


## Async reducer tasks


@TaskTemplate()
async def sum_async_values(values: AsyncGenerator) -> int:
    total = 0
    async for value in values:
        total += value
    return total


@TaskTemplate()
async def sum_async_values_with_offset(values: AsyncGenerator, offset: int) -> int:
    total = 0
    async for value in values:
        total += value
    return total + offset


@TaskTemplate()
async def sum_values_async(values: Generator) -> int:
    await asyncio.sleep(0)
    return sum(values) * 2


## Async generator tasks: int -> AsyncGenerator


@TaskTemplate()
async def emit_async_values(number: int) -> AsyncGenerator:
    for value in range(number, number + 3):
        await asyncio.sleep(0)
        yield value


@TaskTemplate()
async def emit_offset_series(limit: int) -> AsyncGenerator:
    for value in range(limit):
        await asyncio.sleep(0)
        yield value + 100


@TaskTemplate()
async def emit_stepped_series(start: int, step: int) -> AsyncGenerator:
    for index in range(4):
        await asyncio.sleep(0)
        yield start + step * index


## Async generator tasks: stream transforms


@TaskTemplate()
async def emit_async_values_with_offset(values: AsyncGenerator, offset: int) -> AsyncGenerator:
    async for value in values:
        await asyncio.sleep(0)
        yield value + offset


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
