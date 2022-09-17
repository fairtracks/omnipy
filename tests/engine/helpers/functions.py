import asyncio
from datetime import datetime, timedelta
from io import StringIO
import os
from time import sleep
from typing import List

from engine.helpers.mocks import MockTask
from unifair.engine.constants import RunState


def read_log_lines_from_stream(str_stream: StringIO) -> List[str]:
    str_stream.seek(0)
    log_lines = [line.rstrip(os.linesep) for line in str_stream.readlines()]
    str_stream.truncate(0)
    return log_lines


def read_log_line_from_stream(str_stream: StringIO) -> str:
    log_lines = read_log_lines_from_stream(str_stream)
    assert len(log_lines) == 1
    return log_lines[0]


def extract_run_state(task: MockTask):
    return task.runtime.registry.get_task_state(task)


def assert_task_state(task: MockTask, state: RunState):
    assert extract_run_state(task) == state, state


def _check_timeout(start_time: datetime, timeout_secs: float, task: MockTask, state: RunState):
    if datetime.now() - start_time >= timedelta(seconds=timeout_secs):
        raise TimeoutError(f'Run state of "{task.name}" not set to {state.name} '
                           f'until timeout: {timeout_secs} sec(s). '
                           f'Current state: {extract_run_state(task).name}')


def sync_wait_for_task_state(task: MockTask, state: RunState, timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_run_state(task) != state:
        sleep(0.001)
        _check_timeout(start_time, timeout_secs, task, state)


async def async_wait_for_task_state(task: MockTask, state: RunState, timeout_secs: float = 1):
    start_time = datetime.now()
    while extract_run_state(task) != state:
        await asyncio.sleep(0.001)
        _check_timeout(start_time, timeout_secs, task, state)