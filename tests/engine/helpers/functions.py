import asyncio
from datetime import datetime, timedelta
from inspect import isawaitable
from io import StringIO
import logging
import os
from time import sleep
from typing import Awaitable, Callable, List, Optional

from unifair.engine.base import Engine
from unifair.engine.constants import RunState
from unifair.engine.protocols import IsRunStateRegistry, IsTask, IsTaskRunnerEngine, IsTaskTemplate


def read_log_lines_from_stream(str_stream: StringIO) -> List[str]:
    str_stream.seek(0)
    log_lines = [line.rstrip(os.linesep) for line in str_stream.readlines()]
    str_stream.seek(0)
    str_stream.truncate(0)
    return log_lines


def read_log_line_from_stream(str_stream: StringIO) -> str:
    log_lines = read_log_lines_from_stream(str_stream)
    if len(log_lines) == 1:
        return log_lines[0]
    else:
        assert len(log_lines) == 0
        return ''


def extract_run_state(task: IsTask):
    if hasattr(task, 'extrack_registry'):
        registry = task.extrack_registry()
        if registry:
            return registry.get_task_state(task)
    else:
        assert False, 'TODO: Fix for Task objects'


def assert_task_state(task: IsTask, states: List[RunState]):
    task_state = extract_run_state(task)
    if task_state:
        assert task_state in states, task_state


def _check_timeout(start_time: datetime, timeout_secs: float, task: IsTask, states: List[RunState]):
    if datetime.now() - start_time >= timedelta(seconds=timeout_secs):
        raise TimeoutError(
            f'Run state of "{task.name}" not set to {[state.name for state in states]} '
            f'until timeout: {timeout_secs} sec(s). '
            f'Current state: {extract_run_state(task).name}')


def sync_wait_for_task_state(task: IsTask, states: List[RunState], timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_run_state(task) not in states:
        sleep(0.001)
        _check_timeout(start_time, timeout_secs, task, states)


async def async_wait_for_task_state(task: IsTask, states: List[RunState], timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_run_state(task) not in states:
        await asyncio.sleep(0.001)
        _check_timeout(start_time, timeout_secs, task, states)


async def resolve(val):
    if isawaitable(val):
        return await val
    else:
        return val


def get_sync_assert_results_wait_a_bit_func(task: IsTask):
    def sync_assert_results_wait_a_bit(seconds: float) -> None:
        assert task(seconds) == seconds

    return sync_assert_results_wait_a_bit


def get_async_assert_results_wait_a_bit_func(task: IsTask):
    async def async_assert_results_wait_a_bit(seconds: float) -> Awaitable:
        assert await resolve(task(seconds)) == seconds

    return async_assert_results_wait_a_bit


def check_engine_cls(task: IsTask, engine_cls: type[Engine]):
    engine = getattr(task, 'engine')
    if not engine:
        engine = getattr(task, '_engine')

    if hasattr(engine, '_engine'):  # TaskRunnerStateChecker
        engine = engine._engine  # noqa

    return isinstance(engine, engine_cls)


def add_logger_to_registry(registry: IsRunStateRegistry) -> IsRunStateRegistry:
    logger = logging.getLogger('uniFAIR')
    logger.setLevel(logging.INFO)
    registry.set_logger(logger)
    return registry


def convert_func_to_task(
    name: str,
    func: Callable,
    task_template_cls: type(IsTaskTemplate),
    engine: IsTaskRunnerEngine,
    registry: Optional[IsRunStateRegistry],
) -> IsTask:
    task_template = task_template_cls(name, func)
    if registry:
        engine.set_registry(registry)
    task_template.set_engine(engine)
    return task_template.apply()


async def run_task_test(task_case):
    task, run_and_assert_results = task_case
    result = run_and_assert_results(task)
    if result and isawaitable(result):
        await result
