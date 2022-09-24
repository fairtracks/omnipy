import asyncio
from time import sleep

# Synchronous function: sync_power()


def sync_power(number: int, exponent: int):
    return number**exponent


# Synchronous function: sync_wait_a_bit()


def sync_wait_a_bit(seconds: float) -> float:
    sleep(seconds)
    return seconds


# Asynchronous coroutine: async_wait_a_bit()


async def async_wait_a_bit(seconds: float) -> float:
    await asyncio.sleep(seconds)
    return seconds


# Synchronous generator: range()


def sync_range(num: int):
    for i in range(num):
        yield i


# Asynchronous generator: range()


async def async_range(num: int):
    for i in range(num):
        yield i


# Synchronous generator coroutine: sync_wait_for_send_twice()


def sync_wait_for_send_twice():
    for i in range(2):
        value = yield
        yield i, value


# Asynchronous generator coroutine: async_wait_for_send_twice()


async def async_wait_for_send_twice():
    for i in range(2):
        value = yield
        yield i, value
