"""Helper functions for engine tests."""

import asyncio
from time import sleep
from typing import AsyncGenerator, Generator

# Synchronous function: sync_power()


def sync_power(number: int, exponent: int):
    """Run sync power."""
    return number**exponent


# Synchronous function: sync_wait_a_bit()


def sync_wait_a_bit(seconds: float) -> float:
    """Run sync wait a bit."""
    sleep(seconds)
    return seconds


# Asynchronous coroutine: async_wait_a_bit()


async def async_wait_a_bit(seconds: float) -> float:
    await asyncio.sleep(seconds)
    return seconds


# Synchronous generator: range()


def sync_range(num: int) -> Generator:
    """Run sync range."""
    for i in range(num):
        yield i


# Asynchronous generator: range()


async def async_range(num: int) -> AsyncGenerator:
    for i in range(num):
        await asyncio.sleep(0.01)
        yield i


# Synchronous generator coroutine: sync_wait_for_send_twice()


def sync_wait_for_send_twice() -> Generator:
    """Run sync wait for send twice."""
    for i in range(2):
        value = yield
        yield i, value


# Asynchronous generator coroutine: async_wait_for_send_twice()


async def async_wait_for_send_twice() -> AsyncGenerator:
    for i in range(2):
        value = yield
        await asyncio.sleep(0.01)
        yield i, value
