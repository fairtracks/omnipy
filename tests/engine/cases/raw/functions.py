import asyncio
from time import sleep
from typing import Awaitable, Generator

# Synchronous function: sync_power()


def sync_power(number: int, exponent: int):
    return number**exponent


# Synchronous function: sync_wait_a_bit()


def sync_wait_a_bit(seconds: float) -> float:
    sleep(seconds)
    return seconds


# Asynchronous coroutine: async_wait_a_bit()


async def async_wait_a_bit(seconds: float) -> Awaitable[float]:
    await asyncio.sleep(seconds)
    return seconds


# Synchronous generator: range()


def sync_range(num: int) -> Generator:
    for i in range(num):
        yield i


# Asynchronous generator: range()


async def async_range(num: int) -> Awaitable[Generator]:
    for i in range(num):
        yield i


# Synchronous generator coroutine: sync_wait_for_send_twice()


def sync_wait_for_send_twice() -> Generator:
    for i in range(2):
        value = yield
        yield i, value


# Asynchronous generator coroutine: async_wait_for_send_twice()


async def async_wait_for_send_twice() -> Awaitable[Generator]:
    for i in range(2):
        value = yield
        yield i, value
