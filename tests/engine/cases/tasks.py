import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import threading
from types import NoneType
from typing import Awaitable, Callable, Generator

from aiostream.stream import enumerate as aenumerate
import pytest
import pytest_cases as pc

from omnipy.shared.enums.job import RunState
from omnipy.shared.protocols.compute._job import IsJob
from omnipy.util.helpers import resolve

from ..helpers.classes import JobCase
from ..helpers.functions import (assert_job_state,
                                 async_wait_for_job_state,
                                 check_engine_cls,
                                 get_async_assert_results_wait_a_bit_func,
                                 get_sync_assert_results_wait_a_bit_func,
                                 sync_wait_for_job_state)
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

RunTaskAndAssertType = Callable[[IsJob], None]
AsyncRunTaskAndAssertType = Callable[[IsJob], Awaitable[None]]


@pc.case(
    id='sync-function-power(4,2)==16',
    tags=['sync', 'function', 'singlethread', 'success', 'power'],
)
def case_sync_power_args() -> JobCase[[int, int], int]:
    def run_and_assert_results(job: IsJob) -> None:
        assert job(4, 2) == 16
        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[int, int], int]('power', sync_power, run_and_assert_results)


@pc.case(
    id='sync-function-power(number=3,exponent=5)==245',
    tags=['sync', 'function', 'singlethread', 'success', 'power'],
)
def case_sync_power_kwargs() -> JobCase[[int, int], int]:
    def run_and_assert_results(job: IsJob) -> None:
        assert job(number=3, exponent=5) == 243
        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[int, int], int]('power', sync_power, run_and_assert_results)


# # Synchronous/Asynchronous generator: range()


@pc.case(
    id='sync-generator-range',
    tags=['sync', 'generator', 'singlethread', 'success'],
)
def case_sync_range() -> JobCase[[int], Generator]:
    def run_and_assert_results(job: IsJob) -> None:
        generator = job(5)
        assert_job_state(job, [RunState.RUNNING, RunState.FINISHED])

        assert tuple(_ for _ in generator) == (0, 1, 2, 3, 4)
        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[int], Generator]('range', sync_range, run_and_assert_results)


@pc.case(
    id='async-generator-range',
    tags=['async', 'generator', 'singlethread', 'localsuccess'],
)
def case_async_range() -> JobCase[[int], Awaitable[Generator]]:
    async def run_and_assert_results(job: IsJob) -> None:
        generator = job(5)
        assert_job_state(job, [RunState.RUNNING, RunState.FINISHED])

        li = []
        async for i in generator:
            li.append(i)
        assert li == [0, 1, 2, 3, 4]

        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[int], Awaitable[Generator]]('range', async_range, run_and_assert_results)


# Synchronous/Asynchronous generator coroutine: wait_for_send_twice()


@pc.case(
    id='sync-generator-coroutine-wait_for_send_twice()',
    tags=['sync', 'generator-coroutine', 'singlethread', 'localsuccess'],
)
def case_sync_wait_for_send_twice() -> JobCase[[], Generator]:
    def run_and_assert_results(job: IsJob) -> None:
        from omnipy.components.prefect.engine.prefect import PrefectEngine
        if check_engine_cls(job, PrefectEngine):
            pytest.xfail('Synchronous generators stopped working with prefect v2.6.0 (before that,'
                         'they were running eagerly, returning lists of all yielded values).'
                         'Seems to be partly a pydantic bug:'
                         'https://github.com/PrefectHQ/prefect/issues/7692'
                         'https://github.com/PrefectHQ/prefect/pull/7714')

        generator_obj = job()
        assert_job_state(job, [RunState.RUNNING, RunState.FINISHED])

        i = 0
        for i, result in enumerate(generator_obj):
            assert result is None
            assert generator_obj.send('content') == (i, 'content')
        assert i == 1

        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[], Generator]('wait_for_send_twice',
                                  sync_wait_for_send_twice,
                                  run_and_assert_results)


@pc.case(
    id='async-generator-coroutine-wait_for_send_twice()',
    tags=['async', 'generator-coroutine', 'singlethread', 'localsuccess'],
)
def case_async_wait_for_send_twice() -> JobCase[[], Awaitable[Generator]]:
    async def run_and_assert_results(job: IsJob) -> None:
        generator_obj = job()
        assert_job_state(job, [RunState.RUNNING])

        i = 0
        async for i, aresult in aenumerate(generator_obj):
            assert aresult is None
            assert await generator_obj.asend('content') == (i, 'content')
        assert i == 1

        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[], Awaitable[Generator]]('wait_for_send_twice',
                                             async_wait_for_send_twice,
                                             run_and_assert_results)


#  Asynchronous coroutine: wait_a_bit()


@pc.case(
    id='async-coroutine-wait_a_bit(0.005)==0.005',
    tags=['async', 'coroutine', 'singlethread', 'success'],
)
def case_async_wait_a_bit() -> JobCase[[float], Awaitable[float]]:
    async def run_and_assert_results(job: IsJob) -> None:
        async_assert_results_wait_a_bit: Callable[[float], Awaitable] = \
            get_async_assert_results_wait_a_bit_func(job)

        await asyncio.gather(
            async_assert_results_wait_a_bit(0.05),
            async_wait_for_job_state(job, [RunState.RUNNING, RunState.FINISHED]),
        )

        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[float], Awaitable[float]]('wait_a_bit',
                                              async_wait_a_bit,
                                              run_and_assert_results)


#
# Multiple threads
#

# TODO: Allow local config changes for multithreaded jobs (or only allow multiprocessing)

# Synchronous function: wait_a_bit()


@pc.case(
    id='sync-function-threading-wait_a_bit(0.005)==0.005',
    tags=['sync', 'function', 'multithread', 'success'],
)
def case_sync_wait_a_bit_multithreaded_threading() -> JobCase[[float], float]:
    def run_and_assert_results(job: IsJob) -> None:
        sync_assert_results_wait_a_bit: Callable[[float], NoneType] = \
            get_sync_assert_results_wait_a_bit_func(job)
        thread = threading.Thread(target=sync_assert_results_wait_a_bit, args=(0.005,))

        thread.start()
        sync_wait_for_job_state(job, [RunState.RUNNING])

        thread.join()
        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[float], float]('wait_a_bit', sync_wait_a_bit, run_and_assert_results)


@pc.case(
    id='sync-function-futures-wait_a_bit(0.005)==0.005',
    tags=['sync', 'function', 'multithread', 'success'],
)
def case_sync_wait_a_bit_multithreaded_futures() -> JobCase[[float], float]:
    def run_and_assert_results(job: IsJob) -> None:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(job, 0.005)
            sync_wait_for_job_state(job, [RunState.RUNNING])

            assert future.result() == 0.005
            assert_job_state(job, [RunState.FINISHED])

    return JobCase[[float], float]('wait_a_bit', sync_wait_a_bit, run_and_assert_results)


# Asynchronous coroutine: wait_a_bit()


@pc.case(
    id='async-coroutine-threading-wait_a_bit(0.005)==0.005',
    tags=['async', 'coroutine', 'multithread', 'success'],
)
def case_async_wait_a_bit_multithreaded_threading() -> JobCase[[float], Awaitable[float]]:
    def run_and_assert_results(job: IsJob) -> None:
        async_assert_results_wait_a_bit: Callable[[float], Awaitable] = \
            get_async_assert_results_wait_a_bit_func(job)

        def async_run_assert_results_wait_a_bit(seconds: float) -> None:
            asyncio.run(async_assert_results_wait_a_bit(seconds))

        thread = threading.Thread(target=async_run_assert_results_wait_a_bit, args=(0.005,))

        thread.start()
        sync_wait_for_job_state(job, [RunState.RUNNING])

        thread.join()
        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[float], Awaitable[float]]('wait_a_bit',
                                              async_wait_a_bit,
                                              run_and_assert_results)


@pc.case(
    id='async-coroutine-futures-wait_a_bit(0.005)==0.005',
    tags=['async', 'coroutine', 'multithread', 'success'],
)
def case_async_wait_a_bit_multithreaded_futures() -> JobCase[[float], Awaitable[float]]:
    async def run_and_assert_results(job: IsJob) -> None:
        from omnipy.components.prefect.engine.prefect import PrefectEngine
        if any(_ in job.__class__.__name__ for _ in ['LinearFlow', 'DagFlow']) \
                and check_engine_cls(job, PrefectEngine):
            pytest.xfail('Stopped working in some Prefect version between 2.10.10 and 2.13.3.'
                         '(Unclear if the above comment is specific to this test case, as all'
                         'tests in test_all_engines.py were disabled).')
        future = await asyncio.get_event_loop().run_in_executor(None, job, 0.005)
        sync_wait_for_job_state(job, [RunState.RUNNING, RunState.FINISHED])

        assert await resolve(future) == 0.005
        assert_job_state(job, [RunState.FINISHED])

    return JobCase[[float], Awaitable[float]]('wait_a_bit',
                                              async_wait_a_bit,
                                              run_and_assert_results)


#
# Multiple processors
#

# Synchronous function: wait_a_bit()


@pc.case(
    id='fail-sync-function-multiproc-futures-wait_a_bit(0.005)==0.005',
    tags=['sync', 'function', 'multiprocess', 'fail'])
def case_sync_wait_a_bit_multiprocessing_futures() -> JobCase[[float], float]:

    pytest.xfail("Can't pickle function")

    def run_and_assert_results(job: IsJob) -> None:
        with ProcessPoolExecutor(max_workers=1) as executor:
            future = executor.submit(job, 0.005)
            assert future.result() == 0.005

    return JobCase[[float], float]('wait_a_bit', sync_wait_a_bit, run_and_assert_results)


# Asynchronous coroutine: wait_a_bit()


@pc.case(
    id='fail-async-coroutine-multiproc-futures-wait_a_bit(0.005)==0.005',
    tags=['async', 'coroutine', 'multiprocess', 'fail'],
)
def case_async_wait_a_bit_multiprocessing() -> JobCase[[float], Awaitable[float]]:

    pytest.xfail("Can't pickle function")

    async def run_and_assert_results(job: IsJob) -> None:
        async_assert_results_wait_a_bit: Callable[[float], Awaitable] = \
            get_async_assert_results_wait_a_bit_func(job)

        with ProcessPoolExecutor(max_workers=1) as executor:
            loop = asyncio.get_event_loop()
            future = await loop.run_in_executor(
                executor,
                async_assert_results_wait_a_bit,
                0.005,
            )
            await future

    return JobCase[[float], Awaitable[float]]('wait_a_bit',
                                              async_wait_a_bit,
                                              run_and_assert_results)
