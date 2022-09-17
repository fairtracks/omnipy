from copy import copy
from datetime import datetime, timedelta
from io import StringIO
import logging
from time import sleep
from typing import Annotated

import pytest

from engine.helpers.functions import read_log_line_from_stream, read_log_lines_from_stream
from unifair.engine.constants import RunState
from unifair.engine.protocols import TaskProtocol
from unifair.engine.stats import RunStats
from unifair.util.helpers import get_datetime_format


def test_task_state_transitions(task_a: Annotated[TaskProtocol, pytest.fixture],
                                task_b: Annotated[TaskProtocol, pytest.fixture]):
    run_stats = RunStats()

    run_stats.set_task_state(task_a, RunState.INITIALIZED)
    assert run_stats.get_task_state(task_a) == RunState.INITIALIZED
    assert run_stats.all_tasks() == (task_a,)
    assert run_stats.all_tasks(RunState.INITIALIZED) == (task_a,)
    assert run_stats.all_tasks(RunState.RUNNING) == ()
    assert run_stats.all_tasks(RunState.FINISHED) == ()

    run_stats.set_task_state(task_a, RunState.RUNNING)
    assert run_stats.get_task_state(task_a) == RunState.RUNNING
    assert run_stats.all_tasks() == (task_a,)
    assert run_stats.all_tasks(RunState.INITIALIZED) == ()
    assert run_stats.all_tasks(RunState.RUNNING) == (task_a,)
    assert run_stats.all_tasks(RunState.FINISHED) == ()

    run_stats.set_task_state(task_b, RunState.INITIALIZED)
    assert run_stats.get_task_state(task_b) == RunState.INITIALIZED
    assert run_stats.all_tasks() == (task_a, task_b)
    assert run_stats.all_tasks(RunState.INITIALIZED) == (task_b,)
    assert run_stats.all_tasks(RunState.RUNNING) == (task_a,)
    assert run_stats.all_tasks(RunState.FINISHED) == ()

    run_stats.set_task_state(task_b, RunState.RUNNING)
    assert run_stats.get_task_state(task_b) == RunState.RUNNING
    assert run_stats.all_tasks() == (task_a, task_b)
    assert run_stats.all_tasks(RunState.INITIALIZED) == ()
    assert run_stats.all_tasks(RunState.RUNNING) == (task_a, task_b)
    assert run_stats.all_tasks(RunState.FINISHED) == ()

    run_stats.set_task_state(task_b, RunState.FINISHED)
    assert run_stats.get_task_state(task_b) == RunState.FINISHED
    assert run_stats.all_tasks() == (task_a, task_b)
    assert run_stats.all_tasks(RunState.INITIALIZED) == ()
    assert run_stats.all_tasks(RunState.RUNNING) == (task_a,)
    assert run_stats.all_tasks(RunState.FINISHED) == (task_b,)

    run_stats.set_task_state(task_a, RunState.FINISHED)
    assert run_stats.get_task_state(task_b) == RunState.FINISHED
    assert run_stats.all_tasks() == (task_a, task_b)
    assert run_stats.all_tasks(RunState.INITIALIZED) == ()
    assert run_stats.all_tasks(RunState.RUNNING) == ()
    assert run_stats.all_tasks(RunState.FINISHED) == (task_b, task_a)


def test_fail_task_state_transitions(task_a: Annotated[TaskProtocol, pytest.fixture],
                                     task_b: Annotated[TaskProtocol, pytest.fixture]):
    run_stats = RunStats()

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.FINISHED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.RUNNING)

    run_stats.set_task_state(task_a, RunState.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.FINISHED)

    run_stats.set_task_state(task_a, RunState.RUNNING)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.RUNNING)

    run_stats.set_task_state(task_a, RunState.FINISHED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.RUNNING)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_a, RunState.FINISHED)


def test_datetime_of_state_change_event(task_a: Annotated[TaskProtocol, pytest.fixture],
                                        task_b: Annotated[TaskProtocol, pytest.fixture]):
    run_stats = RunStats()
    cur_time = datetime.now()

    sleep(0.001)
    run_stats.set_task_state(task_a, RunState.INITIALIZED)
    init_time = run_stats.get_task_state_datetime(task_a, RunState.INITIALIZED)
    assert timedelta() < init_time - cur_time < timedelta(seconds=1)

    sleep(0.001)
    run_stats.set_task_state(task_a, RunState.RUNNING)
    assert run_stats.get_task_state_datetime(task_a, RunState.INITIALIZED) == init_time
    run_time = run_stats.get_task_state_datetime(task_a, RunState.RUNNING)
    assert timedelta() < run_time - init_time < timedelta(seconds=1)

    sleep(0.001)
    run_stats.set_task_state(task_a, RunState.FINISHED)
    assert run_stats.get_task_state_datetime(task_a, RunState.INITIALIZED) == init_time
    assert run_stats.get_task_state_datetime(task_a, RunState.RUNNING) == run_time
    finish_time = run_stats.get_task_state_datetime(task_a, RunState.FINISHED)
    assert timedelta() < finish_time - run_time < timedelta(seconds=1)

    assert cur_time < init_time < run_time < finish_time


def test_fail_task_key_error(task_a: Annotated[TaskProtocol, pytest.fixture],
                             task_b: Annotated[TaskProtocol, pytest.fixture]):
    run_stats = RunStats()

    with pytest.raises(KeyError):
        run_stats.get_task_state(task_a)

    with pytest.raises(KeyError):
        run_stats.get_task_state_datetime(task_a, RunState.INITIALIZED)

    run_stats.set_task_state(task_a, RunState.INITIALIZED)
    run_stats.get_task_state(task_a)
    run_stats.get_task_state_datetime(task_a, RunState.INITIALIZED)

    with pytest.raises(KeyError):
        run_stats.get_task_state(task_b)

    with pytest.raises(KeyError):
        run_stats.get_task_state_datetime(task_a, RunState.RUNNING)

    with pytest.raises(KeyError):
        run_stats.get_task_state_datetime(task_b, RunState.INITIALIZED)


def test_fail_task_same_name_different_task(task_a: Annotated[TaskProtocol, pytest.fixture],
                                            task_b: Annotated[TaskProtocol, pytest.fixture]):
    task_b = copy(task_b)
    task_b.name = task_a.name

    run_stats = RunStats()
    run_stats.set_task_state(task_a, RunState.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_b, RunState.INITIALIZED)

    with pytest.raises(ValueError):
        run_stats.set_task_state(task_b, RunState.RUNNING)


def test_state_change_logging(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    task_a: Annotated[TaskProtocol, pytest.fixture],
    task_b: Annotated[TaskProtocol, pytest.fixture],
):
    run_stats = RunStats()

    simple_logger.addHandler(logging.StreamHandler(str_stream))
    run_stats.set_logger(simple_logger)

    events = [
        (task_a, RunState.INITIALIZED),
        (task_a, RunState.RUNNING),
        (task_b, RunState.INITIALIZED),
        (task_a, RunState.FINISHED),
        (task_b, RunState.RUNNING),
        (task_b, RunState.FINISHED),
    ]

    datetime_list = []
    for task, state in events:
        run_stats.set_task_state(task, state)
        datetime_list.append(run_stats.get_task_state_datetime(task, state))

    log_lines = read_log_lines_from_stream(str_stream)

    assert len(log_lines) == 6

    assert log_lines[0] == f'INFO (test) - ' \
                           f'{datetime_list[0].strftime(get_datetime_format())}: ' \
                           f'Initialized task "a"'
    assert log_lines[1] == f'INFO (test) - ' \
                           f'{datetime_list[1].strftime(get_datetime_format())}: ' \
                           f'Started running task "a"...'
    assert log_lines[2] == f'INFO (test) - ' \
                           f'{datetime_list[2].strftime(get_datetime_format())}: ' \
                           f'Initialized task "b"'
    assert log_lines[3] == f'INFO (test) - ' \
                           f'{datetime_list[3].strftime(get_datetime_format())}: ' \
                           f'Task "a" finished!'
    assert log_lines[4] == f'INFO (test) - ' \
                           f'{datetime_list[4].strftime(get_datetime_format())}: ' \
                           f'Started running task "b"...'
    assert log_lines[5] == f'INFO (test) - ' \
                           f'{datetime_list[5].strftime(get_datetime_format())}: ' \
                           f'Task "b" finished!'


def test_state_change_logging_handler_formatting_variants(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    task_a: Annotated[TaskProtocol, pytest.fixture],
):
    run_stats = RunStats()

    # Handler added after set_logger
    run_stats.set_logger(simple_logger, set_unifair_formatter_on_handlers=True)
    simple_logger.addHandler(logging.StreamHandler(str_stream))
    run_stats.set_task_state(task_a, RunState.INITIALIZED)

    log_line = read_log_line_from_stream(str_stream)
    assert 'INFO (test)' not in log_line

    # Handler added before set_logger, set_unifair_formatter_on_handlers=False
    run_stats.set_logger(simple_logger, set_unifair_formatter_on_handlers=False)
    run_stats.set_task_state(task_a, RunState.RUNNING)

    log_line = read_log_line_from_stream(str_stream)
    assert 'INFO (test)' not in log_line

    # Handler added before set_logger, set_unifair_formatter_on_handlers=True
    run_stats.set_logger(simple_logger, set_unifair_formatter_on_handlers=True)
    run_stats.set_task_state(task_a, RunState.FINISHED)

    log_line = read_log_line_from_stream(str_stream)

    assert 'INFO (test)' in log_line


def test_state_change_logging_date_localization(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    task_a: Annotated[TaskProtocol, pytest.fixture],
):
    run_stats = RunStats()

    simple_logger.addHandler(logging.StreamHandler(str_stream))

    locale = ('no_NO', 'UTF-8')
    run_stats.set_logger(simple_logger, locale=locale)

    run_stats.set_task_state(task_a, RunState.INITIALIZED)
    init_datetime = run_stats.get_task_state_datetime(task_a, RunState.INITIALIZED)

    log_line = read_log_line_from_stream(str_stream)

    assert init_datetime.strftime(get_datetime_format(locale)) in log_line
    assert 'INFO (test)' in log_line
