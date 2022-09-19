import asyncio
from typing import Annotated

from aiostream.stream import enumerate as aenumerate
import pytest

from engine.helpers.functions import assert_task_state, async_wait_for_task_state
from engine.helpers.mocks import AssertLocalRunner, MockRunStateRegistry, MockTask, MockTaskTemplate
from unifair.engine.constants import RunState


def test_local_runner_sync_function(
        mock_run_state_registry: Annotated[MockRunStateRegistry, pytest.fixture],
        assert_local_runner_with_mock_registry: Annotated[AssertLocalRunner, pytest.fixture],
        sync_power_task_template: Annotated[MockTaskTemplate, pytest.fixture]) -> None:

    sync_power_task_template.set_engine(assert_local_runner_with_mock_registry)
    sync_power_task_template.set_registry(mock_run_state_registry)

    power = sync_power_task_template.apply()
    assert power(number=3, exponent=5) == 243

    assert_task_state(power, RunState.FINISHED)


def test_local_runner_sync_generator_coroutine(
        mock_run_state_registry: Annotated[MockRunStateRegistry, pytest.fixture],
        assert_local_runner_with_mock_registry: Annotated[AssertLocalRunner, pytest.fixture],
        sync_wait_for_send_twice_task_template: Annotated[MockTaskTemplate,
                                                          pytest.fixture]) -> None:

    sync_wait_for_send_twice_task_template.set_engine(assert_local_runner_with_mock_registry)
    sync_wait_for_send_twice_task_template.set_registry(mock_run_state_registry)

    sync_wait_for_send_twice = sync_wait_for_send_twice_task_template.apply()

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
    mock_run_state_registry: Annotated[MockRunStateRegistry, pytest.fixture],
    assert_local_runner_with_mock_registry: Annotated[AssertLocalRunner, pytest.fixture],
    async_wait_a_bit_task_template: Annotated[MockTaskTemplate, pytest.fixture],
) -> None:

    async_wait_a_bit_task_template.set_engine(assert_local_runner_with_mock_registry)
    async_wait_a_bit_task_template.set_registry(mock_run_state_registry)

    async_wait_a_bit = async_wait_a_bit_task_template.apply()

    async def async_assert_results_wait_a_bit(seconds: float) -> None:
        assert await async_wait_a_bit(seconds) == seconds

    await asyncio.gather(
        async_assert_results_wait_a_bit(0.005),
        async_wait_for_task_state(async_wait_a_bit, RunState.RUNNING))

    assert_task_state(async_wait_a_bit, RunState.FINISHED)


@pytest.mark.asyncio
async def test_mock_task_run_states_async_generator_coroutine(
        mock_run_state_registry: Annotated[MockRunStateRegistry, pytest.fixture],
        assert_local_runner_with_mock_registry: Annotated[AssertLocalRunner, pytest.fixture],
        async_wait_for_send_twice_task_template: Annotated[MockTaskTemplate,
                                                           pytest.fixture]) -> None:

    async_wait_for_send_twice_task_template.set_engine(assert_local_runner_with_mock_registry)
    async_wait_for_send_twice_task_template.set_registry(mock_run_state_registry)

    async_wait_for_send_twice = async_wait_for_send_twice_task_template.apply()

    generator_obj = async_wait_for_send_twice()
    assert_task_state(async_wait_for_send_twice, RunState.RUNNING)

    i = 0
    async for i, aresult in aenumerate(generator_obj):
        assert aresult is None
        assert await generator_obj.asend('content') == (i, 'content')
    assert i == 1

    assert_task_state(async_wait_for_send_twice, RunState.FINISHED)
