import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import threading
from types import NoneType
from typing import Awaitable, Callable, Generator, Tuple

from aiostream.stream import enumerate as aenumerate
import pytest
import pytest_cases as pc

from engine.helpers.functions import (assert_task_state,
                                      async_wait_for_task_state,
                                      check_engine_cls,
                                      get_async_assert_results_wait_a_bit_func,
                                      get_sync_assert_results_wait_a_bit_func,
                                      resolve,
                                      sync_wait_for_task_state)
from unifair.engine.constants import RunState
from unifair.engine.protocols import IsTask

from .raw.functions import (async_range,
                            async_wait_a_bit,
                            async_wait_for_send_twice,
                            sync_power,
                            sync_range,
                            sync_wait_a_bit,
                            sync_wait_for_send_twice)

#
# Single thread
#

# Synchronous function: power()

RunTaskAndAssertType = Callable[[IsTask], None]
AsyncRunTaskAndAssertType = Callable[[IsTask], Awaitable[None]]


@pc.case(
    id='sync-function-power(4,2)==16',
    tags=['sync', 'function', 'singlethread', 'success', 'power'],
)
def case_sync_power_args() -> Tuple[str, Callable[[int, int], int], RunTaskAndAssertType]:
    def run_and_assert_results(task: IsTask) -> None:
        assert task(4, 2) == 16
        assert_task_state(task, [RunState.FINISHED])

    return 'power', sync_power, run_and_assert_results


@pc.case(
    id='sync-function-power(number=3,exponent=5)==245',
    tags=['sync', 'function', 'singlethread', 'success', 'power'],
)
def case_sync_power_kwargs() -> Tuple[str, Callable[[int, int], int], RunTaskAndAssertType]:
    def run_and_assert_results(task: IsTask) -> None:
        assert task(number=3, exponent=5) == 243
        assert_task_state(task, [RunState.FINISHED])

    return 'power', sync_power, run_and_assert_results


# Synchronous/Asynchronous generator: range()


@pc.case(
    id='sync-generator-range',
    tags=['sync', 'generator', 'singlethread', 'success'],
)
def case_sync_range() -> Tuple[str, Callable[[int], Generator], RunTaskAndAssertType]:
    def run_and_assert_results(task: IsTask) -> None:
        generator = task(5)
        assert_task_state(task, [RunState.RUNNING, RunState.FINISHED])

        assert tuple(_ for _ in generator) == (0, 1, 2, 3, 4)
        assert_task_state(task, [RunState.FINISHED])

    return 'range', sync_range, run_and_assert_results


@pc.case(
    id='async-generator-range',
    tags=['async', 'generator', 'singlethread', 'localsuccess'],
)
def case_async_range() -> \
        Tuple[str, Callable[[int], Awaitable[Generator]], AsyncRunTaskAndAssertType]:
    async def run_and_assert_results(task: IsTask) -> None:
        from unifair.engine.prefect import PrefectEngine
        if check_engine_cls(task, PrefectEngine):
            pytest.xfail("TypeError: cannot pickle 'async_generator' object")

        generator = task(5)
        assert_task_state(task, [RunState.RUNNING, RunState.FINISHED])

        li = []
        async for i in generator:
            li.append(i)
        assert li == [0, 1, 2, 3, 4]

        assert_task_state(task, [RunState.FINISHED])

    return 'range', async_range, run_and_assert_results


# Synchronous/Asynchronous generator coroutine: wait_for_send_twice()


@pc.case(
    id='sync-generator-coroutine-wait_for_send_twice()',
    tags=['sync', 'generator-coroutine', 'singlethread', 'localsuccess'],
)
def case_sync_wait_for_send_twice() -> Tuple[str, Callable[[], Generator], RunTaskAndAssertType]:
    def run_and_assert_results(task: IsTask) -> None:
        from unifair.engine.prefect import PrefectEngine
        if check_engine_cls(task, PrefectEngine):
            pytest.xfail("AttributeError: 'list' object has no attribute 'send'")

        generator_obj = task()
        assert_task_state(task, [RunState.RUNNING, RunState.FINISHED])

        i = 0
        for i, result in enumerate(generator_obj):
            assert result is None
            assert generator_obj.send('content') == (i, 'content')
        assert i == 1

        assert_task_state(task, [RunState.FINISHED])

    return 'wait_for_send_twice', sync_wait_for_send_twice, run_and_assert_results


@pc.case(
    id='async-generator-coroutine-wait_for_send_twice()',
    tags=['async', 'generator-coroutine', 'singlethread', 'localsuccess'],
)
def case_async_wait_for_send_twice() -> \
        Tuple[str, Callable[[], Awaitable[Generator]], AsyncRunTaskAndAssertType]:
    async def run_and_assert_results(task: IsTask) -> None:
        from unifair.engine.prefect import PrefectEngine
        if check_engine_cls(task, PrefectEngine):
            pytest.xfail("TypeError: cannot pickle 'async_generator' object")

        generator_obj = task()
        assert_task_state(task, [RunState.RUNNING])

        i = 0
        async for i, aresult in aenumerate(generator_obj):
            assert aresult is None
            assert await generator_obj.asend('content') == (i, 'content')
        assert i == 1

        assert_task_state(task, [RunState.FINISHED])

    return 'wait_for_send_twice', async_wait_for_send_twice, run_and_assert_results


#  Asynchronous coroutine: wait_a_bit()


@pc.case(
    id='async-coroutine-wait_a_bit(0.005)==0.005',
    tags=['async', 'coroutine', 'singlethread', 'success'],
)
def case_async_wait_a_bit() -> \
        Tuple[str, Callable[[float], Awaitable[float]], AsyncRunTaskAndAssertType]:
    async def run_and_assert_results(task: IsTask) -> None:
        async_assert_results_wait_a_bit: Callable[[float], Awaitable] = \
            get_async_assert_results_wait_a_bit_func(task)

        await asyncio.gather(
            async_assert_results_wait_a_bit(0.05),
            async_wait_for_task_state(task, [RunState.RUNNING, RunState.FINISHED]),
        )

        assert_task_state(task, [RunState.FINISHED])

    return 'wait_a_bit', async_wait_a_bit, run_and_assert_results


#
# Multiple threads
#

# Synchronous function: wait_a_bit()


@pc.case(
    id='sync-function-threading-wait_a_bit(0.005)==0.005',
    tags=['sync', 'function', 'multithread', 'success'],
)
def case_sync_wait_a_bit_multithreaded_threading() -> \
        Tuple[str, Callable[[float],float], RunTaskAndAssertType]:
    def run_and_assert_results(task: IsTask) -> None:
        sync_assert_results_wait_a_bit: Callable[[float], NoneType] = \
            get_sync_assert_results_wait_a_bit_func(task)
        thread = threading.Thread(target=sync_assert_results_wait_a_bit, args=(0.005,))

        thread.start()
        sync_wait_for_task_state(task, [RunState.RUNNING])

        thread.join()
        assert_task_state(task, [RunState.FINISHED])

    return 'wait_a_bit', sync_wait_a_bit, run_and_assert_results


@pc.case(
    id='sync-function-futures-wait_a_bit(0.005)==0.005',
    tags=['sync', 'function', 'multithread', 'success'],
)
def case_sync_wait_a_bit_multithreaded_futures() -> \
        Tuple[str, Callable[[float], float], RunTaskAndAssertType]:
    def run_and_assert_results(task: IsTask) -> None:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(task, 0.005)
            sync_wait_for_task_state(task, [RunState.RUNNING])

            assert future.result() == 0.005
            assert_task_state(task, [RunState.FINISHED])

    return 'wait_a_bit', sync_wait_a_bit, run_and_assert_results


# Asynchronous coroutine: wait_a_bit()


@pc.case(
    id='async-coroutine-threading-wait_a_bit(0.005)==0.005',
    tags=['async', 'coroutine', 'multithread', 'success'],
)
def case_async_wait_a_bit_multithreaded_threading() -> \
        Tuple[str, Callable[[float], Awaitable[float]], RunTaskAndAssertType]:
    def run_and_assert_results(task: IsTask) -> None:
        async_assert_results_wait_a_bit: Callable[[float], Awaitable] = \
            get_async_assert_results_wait_a_bit_func(task)

        def async_run_assert_results_wait_a_bit(seconds: float) -> None:
            asyncio.run(async_assert_results_wait_a_bit(seconds))

        thread = threading.Thread(target=async_run_assert_results_wait_a_bit, args=(0.005,))

        thread.start()
        sync_wait_for_task_state(task, [RunState.RUNNING])

        thread.join()
        assert_task_state(task, [RunState.FINISHED])

    return 'wait_a_bit', async_wait_a_bit, run_and_assert_results


@pc.case(
    id='async-coroutine-futures-wait_a_bit(0.005)==0.005',
    tags=['async', 'coroutine', 'multithread', 'success'],
)
def case_async_wait_a_bit_multithreaded_futures() -> \
        Tuple[str, Callable[[float], Awaitable[float]], AsyncRunTaskAndAssertType]:
    async def run_and_assert_results(task: IsTask) -> None:

        future = await asyncio.get_event_loop().run_in_executor(None, task, 0.005)
        sync_wait_for_task_state(task, [RunState.RUNNING, RunState.FINISHED])

        assert await resolve(future) == 0.005
        assert_task_state(task, [RunState.FINISHED])

    return 'wait_a_bit', async_wait_a_bit, run_and_assert_results


#
# Multiple processors
#

# Synchronous function: wait_a_bit()


@pc.case(
    id='fail-sync-function-futures-wait_a_bit(0.005)==0.005',
    tags=['sync', 'function', 'multiprocess', 'fail'])
def case_sync_wait_a_bit_multiprocessing_futures() -> \
        Tuple[str, Callable[[float], float], RunTaskAndAssertType]:

    pytest.xfail("Can't pickle function")

    def run_and_assert_results(task: IsTask) -> None:
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(task, 0.005)
            assert future.result() == 0.005

    return 'wait_a_bit', sync_wait_a_bit, run_and_assert_results


# Asynchronous coroutine: wait_a_bit()


@pc.case(
    id='fail-async-coroutine-futures-wait_a_bit(0.005)==0.005',
    tags=['async', 'coroutine', 'multiprocess', 'fail'],
)
def case_async_wait_a_bit_multiprocessing() -> \
        Tuple[str, Callable[[float], Awaitable[float]], AsyncRunTaskAndAssertType]:

    pytest.xfail("Can't pickle function")

    async def run_and_assert_results(task: IsTask) -> None:
        async_assert_results_wait_a_bit: Callable[[float], Awaitable] = \
            get_async_assert_results_wait_a_bit_func(task)

        with ProcessPoolExecutor(max_workers=1) as executor:
            loop = asyncio.get_event_loop()
            future = await loop.run_in_executor(
                executor,
                async_assert_results_wait_a_bit,
                0.005,
            )
            await future

    return 'wait_a_bit', async_wait_a_bit, run_and_assert_results
