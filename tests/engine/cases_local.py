import asyncio
from typing import Awaitable, Generator

from aiostream.stream import enumerate as aenumerate
import pytest_cases as pc

from engine.helpers.functions import assert_task_state, async_wait_for_task_state
from engine.helpers.mocks import MockTask
from unifair.engine.constants import RunState
from unifair.engine.protocols import IsTask


class CallableTaskCases:
    @pc.case(id='power(number=3, exponent=5)==245', tags='sync function')
    def case_sync_power(self):
        def power(number: int, exponent: int):
            return number**exponent

        def assert_result(_task: IsTask, result: int):
            assert result == 243

        return 'power', power, (), dict(number=3, exponent=5), assert_result

    @pc.case(id='wait_for_send_twice', tags='sync generator-coroutine')
    def case_sync_wait_for_send_twice(self):
        def wait_for_send_twice():
            for i in range(2):
                value = yield
                yield i, value

        def assert_result(task: MockTask, generator_obj: Generator):
            assert_task_state(task, RunState.RUNNING)

            i = 0
            for i, result in enumerate(generator_obj):
                assert result is None
                assert generator_obj.send('content') == (i, 'content')
            assert i == 1

            assert_task_state(task, RunState.FINISHED)

        return 'wait_for_send_twice', wait_for_send_twice, (), {}, assert_result

    @pc.case(id='wait_a_bit', tags='async coroutine')
    def case_async_wait_a_bit(self):
        async def async_wait_a_bit(seconds: float) -> float:
            await asyncio.sleep(seconds)
            return seconds

        async def assert_result(task: MockTask, result_awaitable: Awaitable):
            async def async_assert_results_wait_a_bit(seconds: float) -> None:
                assert await result_awaitable == seconds

            await asyncio.gather(
                async_assert_results_wait_a_bit(0.005),
                async_wait_for_task_state(task, RunState.RUNNING))

            assert_task_state(task, RunState.FINISHED)

        return 'wait_a_bit', async_wait_a_bit, (0.005,), {}, assert_result

    @pc.case(id='wait_for_send_twice', tags='async generator-coroutine')
    def case_async_wait_for_send_twice(self):
        async def wait_for_send_twice():
            for i in range(2):
                value = yield
                yield i, value

        async def assert_result(task: MockTask, generator_obj: Generator):
            assert_task_state(task, RunState.RUNNING)

            i = 0
            async for i, aresult in aenumerate(generator_obj):
                assert aresult is None
                assert await generator_obj.asend('content') == (i, 'content')
            assert i == 1

            assert_task_state(task, RunState.FINISHED)

        return 'wait_for_send_twice', wait_for_send_twice, (), {}, assert_result
