import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import threading
from typing import Annotated, Awaitable, Callable

from aiostream.stream import enumerate as aenumerate
import pytest

from unifair.engine.constants import RunState
from unifair.engine.protocols import IsTaskRunnerEngine

from .helpers.functions import (assert_task_state,
                                async_wait_for_task_state,
                                sync_wait_for_task_state)
from .helpers.mocks import MockEngineConfig, MockTask, MockTaskRunnerEngine, MockTaskTemplate


def test_engine_init() -> None:
    engine = MockTaskRunnerEngine()
    assert engine.backend_verbose is True

    engine = MockTaskRunnerEngine()
    engine.set_config(MockEngineConfig(backend_verbose=True))
    assert engine.backend_verbose is True

    engine = MockTaskRunnerEngine()
    engine.set_config(MockEngineConfig(backend_verbose=False))
    assert engine.backend_verbose is False


def test_mock_task_run(
    mock_task_runner_engine_no_verbose: Annotated[IsTaskRunnerEngine, pytest.fixture],
    sync_power_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> None:

    power = sync_power_task_template.apply()

    assert power(4, 2) == 16
    assert power.name == 'power'
    assert power.engine.backend_task.backend_verbose is False
    assert power.engine.backend_task.finished


def test_mock_task_run_states_sync_function(
    mock_task_runner_engine_no_verbose: Annotated[IsTaskRunnerEngine, pytest.fixture],
    sync_power_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> None:

    power = sync_power_task_template.apply()
    assert_task_state(power, RunState.INITIALIZED)

    assert power(4, 2) == 16
    assert_task_state(power, RunState.FINISHED)


def test_mock_task_run_states_sync_function_multithreaded_threading(
    sync_wait_a_bit: Annotated[MockTask, pytest.fixture],
    sync_assert_results_wait_a_bit: Annotated[Callable[[float], None], pytest.fixture],
) -> None:
    assert_task_state(sync_wait_a_bit, RunState.INITIALIZED)

    wait_a_bit_thread = threading.Thread(target=sync_assert_results_wait_a_bit, args=(0.005,))

    wait_a_bit_thread.start()
    sync_wait_for_task_state(sync_wait_a_bit, RunState.RUNNING)

    wait_a_bit_thread.join()
    assert_task_state(sync_wait_a_bit, RunState.FINISHED)


def test_mock_task_run_states_sync_function_multithreaded_futures(
        sync_wait_a_bit: Annotated[MockTask, pytest.fixture]) -> None:

    assert_task_state(sync_wait_a_bit, RunState.INITIALIZED)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(sync_wait_a_bit, 0.005)

        sync_wait_for_task_state(sync_wait_a_bit, RunState.RUNNING)

        assert future.result() == 0.005
        assert_task_state(sync_wait_a_bit, RunState.FINISHED)


def test_fail_mock_task_run_states_sync_function_multiprocessing_futures(
        sync_wait_a_bit: Annotated[MockTask, pytest.fixture]) -> None:

    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(sync_wait_a_bit, 0.005)
        with pytest.raises(AttributeError):  # Can't pickle decorated function
            future.result()


def test_mock_task_run_states_sync_generator_coroutine(
        sync_wait_for_send_twice: Annotated[MockTask, pytest.fixture]) -> None:
    assert_task_state(sync_wait_for_send_twice, RunState.INITIALIZED)

    generator_obj = sync_wait_for_send_twice()
    assert_task_state(sync_wait_for_send_twice, RunState.RUNNING)

    i = 0
    for i, result in enumerate(generator_obj):
        assert result is None
        assert generator_obj.send('content') == (i, 'content')
    assert i == 1

    assert_task_state(sync_wait_for_send_twice, RunState.FINISHED)


@pytest.mark.asyncio
async def test_mock_task_run_states_async_coroutine(
    async_wait_a_bit: Annotated[MockTask, pytest.fixture],
    async_assert_results_wait_a_bit: Annotated[Callable[[float], Awaitable[None]], pytest.fixture],
) -> None:
    assert_task_state(async_wait_a_bit, RunState.INITIALIZED)

    await asyncio.gather(
        async_assert_results_wait_a_bit(0.005),
        async_wait_for_task_state(async_wait_a_bit, RunState.RUNNING))

    assert_task_state(async_wait_a_bit, RunState.FINISHED)


@pytest.mark.asyncio
async def test_mock_task_run_states_async_coroutine_multithreaded_threading(
    async_wait_a_bit: Annotated[MockTask, pytest.fixture],
    async_run_assert_results_wait_a_bit: Annotated[Callable[[float], Awaitable[None]],
                                                   pytest.fixture],
) -> None:
    assert_task_state(async_wait_a_bit, RunState.INITIALIZED)

    wait_a_bit_thread = threading.Thread(target=async_run_assert_results_wait_a_bit, args=(0.005,))

    wait_a_bit_thread.start()
    sync_wait_for_task_state(async_wait_a_bit, RunState.RUNNING)

    wait_a_bit_thread.join()
    assert_task_state(async_wait_a_bit, RunState.FINISHED)


@pytest.mark.asyncio
async def test_mock_task_run_states_async_coroutine_multithreaded_futures(
    async_wait_a_bit: Annotated[MockTask, pytest.fixture],
    async_assert_results_wait_a_bit: Annotated[Callable[[float], Awaitable[None]], pytest.fixture],
) -> None:
    assert_task_state(async_wait_a_bit, RunState.INITIALIZED)

    future = await asyncio.get_event_loop().run_in_executor(None, async_wait_a_bit, 0.005)
    sync_wait_for_task_state(async_wait_a_bit, RunState.RUNNING)

    assert await future == 0.005
    assert_task_state(async_wait_a_bit, RunState.FINISHED)


@pytest.mark.asyncio
async def test_fail_mock_task_run_states_async_coroutine_multiprocessing_futures(
    async_wait_a_bit: Annotated[MockTask, pytest.fixture],
    async_assert_results_wait_a_bit: Annotated[Callable[[float], Awaitable[None]], pytest.fixture],
) -> None:
    assert_task_state(async_wait_a_bit, RunState.INITIALIZED)

    with ProcessPoolExecutor(max_workers=1) as executor:
        loop = asyncio.get_event_loop()
        with pytest.raises(AttributeError):  # Can't pickle decorated function
            future = await loop.run_in_executor(executor, async_assert_results_wait_a_bit, 0.005)
            await future


@pytest.mark.asyncio
async def test_mock_task_run_states_async_generator_coroutine(
        async_wait_for_send_twice: Annotated[MockTask, pytest.fixture]) -> None:
    assert_task_state(async_wait_for_send_twice, RunState.INITIALIZED)

    generator_obj = async_wait_for_send_twice()
    assert_task_state(async_wait_for_send_twice, RunState.RUNNING)

    i = 0
    async for i, aresult in aenumerate(generator_obj):
        assert aresult is None
        assert await generator_obj.asend('content') == (i, 'content')
    assert i == 1

    assert_task_state(async_wait_for_send_twice, RunState.FINISHED)
