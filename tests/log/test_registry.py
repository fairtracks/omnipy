from copy import copy
from datetime import datetime, timedelta
from io import StringIO
import logging
from time import sleep
from typing import Annotated

import pytest

from omnipy.api.enums import RunState
from omnipy.api.protocols import IsDagFlow, IsTask
from omnipy.log.registry import RunStateRegistry
from omnipy.util.helpers import get_datetime_format

from .helpers.functions import read_log_line_from_stream, read_log_lines_from_stream


def test_job_state_transitions(
    task_a: Annotated[IsTask, pytest.fixture],
    task_b: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
    dag_flow_b: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a, job_b in [(task_a, task_b), (dag_flow_a, dag_flow_b)]:
        registry = RunStateRegistry()

        registry.set_job_state(job_a, RunState.INITIALIZED)
        assert registry.get_job_state(job_a) == RunState.INITIALIZED
        assert registry.all_jobs() == (job_a,)
        assert registry.all_jobs(RunState.INITIALIZED) == (job_a,)
        assert registry.all_jobs(RunState.RUNNING) == ()
        assert registry.all_jobs(RunState.FINISHED) == ()

        registry.set_job_state(job_a, RunState.RUNNING)
        assert registry.get_job_state(job_a) == RunState.RUNNING
        assert registry.all_jobs() == (job_a,)
        assert registry.all_jobs(RunState.INITIALIZED) == ()
        assert registry.all_jobs(RunState.RUNNING) == (job_a,)
        assert registry.all_jobs(RunState.FINISHED) == ()

        registry.set_job_state(job_b, RunState.INITIALIZED)
        assert registry.get_job_state(job_b) == RunState.INITIALIZED
        assert registry.all_jobs() == (job_a, job_b)
        assert registry.all_jobs(RunState.INITIALIZED) == (job_b,)
        assert registry.all_jobs(RunState.RUNNING) == (job_a,)
        assert registry.all_jobs(RunState.FINISHED) == ()

        registry.set_job_state(job_b, RunState.RUNNING)
        assert registry.get_job_state(job_b) == RunState.RUNNING
        assert registry.all_jobs() == (job_a, job_b)
        assert registry.all_jobs(RunState.INITIALIZED) == ()
        assert registry.all_jobs(RunState.RUNNING) == (job_a, job_b)
        assert registry.all_jobs(RunState.FINISHED) == ()

        registry.set_job_state(job_b, RunState.FINISHED)
        assert registry.get_job_state(job_b) == RunState.FINISHED
        assert registry.all_jobs() == (job_a, job_b)
        assert registry.all_jobs(RunState.INITIALIZED) == ()
        assert registry.all_jobs(RunState.RUNNING) == (job_a,)
        assert registry.all_jobs(RunState.FINISHED) == (job_b,)

        registry.set_job_state(job_a, RunState.FINISHED)
        assert registry.get_job_state(job_b) == RunState.FINISHED
        assert registry.all_jobs() == (job_a, job_b)
        assert registry.all_jobs(RunState.INITIALIZED) == ()
        assert registry.all_jobs(RunState.RUNNING) == ()
        assert registry.all_jobs(RunState.FINISHED) == (job_b, job_a)


def test_fail_job_state_transitions(
    task_a: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a in [task_a, dag_flow_a]:
        registry = RunStateRegistry()

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.FINISHED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.RUNNING)

        registry.set_job_state(job_a, RunState.INITIALIZED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.INITIALIZED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.FINISHED)

        registry.set_job_state(job_a, RunState.RUNNING)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.INITIALIZED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.RUNNING)

        registry.set_job_state(job_a, RunState.FINISHED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.INITIALIZED)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.RUNNING)

        with pytest.raises(ValueError):
            registry.set_job_state(job_a, RunState.FINISHED)


def test_datetime_of_state_change_event(
    task_a: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a in [task_a, dag_flow_a]:
        registry = RunStateRegistry()
        cur_time = datetime.now()

        sleep(0.001)
        registry.set_job_state(job_a, RunState.INITIALIZED)
        init_time = registry.get_job_state_datetime(job_a, RunState.INITIALIZED)
        assert timedelta() < init_time - cur_time < timedelta(seconds=1)

        sleep(0.001)
        registry.set_job_state(job_a, RunState.RUNNING)
        assert registry.get_job_state_datetime(job_a, RunState.INITIALIZED) == init_time
        run_time = registry.get_job_state_datetime(job_a, RunState.RUNNING)
        assert timedelta() < run_time - init_time < timedelta(seconds=1)

        sleep(0.001)
        registry.set_job_state(job_a, RunState.FINISHED)
        assert registry.get_job_state_datetime(job_a, RunState.INITIALIZED) == init_time
        assert registry.get_job_state_datetime(job_a, RunState.RUNNING) == run_time
        finish_time = registry.get_job_state_datetime(job_a, RunState.FINISHED)
        assert timedelta() < finish_time - run_time < timedelta(seconds=1)

        assert cur_time < init_time < run_time < finish_time


def test_fail_job_key_error(
    task_a: Annotated[IsTask, pytest.fixture],
    task_b: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
    dag_flow_b: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a, job_b in [(task_a, task_b), (dag_flow_a, dag_flow_b)]:
        registry = RunStateRegistry()

        with pytest.raises(KeyError):
            registry.get_job_state(job_a)

        with pytest.raises(KeyError):
            registry.get_job_state_datetime(job_a, RunState.INITIALIZED)

        registry.set_job_state(job_a, RunState.INITIALIZED)
        registry.get_job_state(job_a)
        registry.get_job_state_datetime(job_a, RunState.INITIALIZED)

        with pytest.raises(KeyError):
            registry.get_job_state(job_b)

        with pytest.raises(KeyError):
            registry.get_job_state_datetime(job_a, RunState.RUNNING)

        with pytest.raises(KeyError):
            registry.get_job_state_datetime(job_b, RunState.INITIALIZED)


def test_same_unique_name_different_job(
    task_a: Annotated[IsTask, pytest.fixture],
    task_b: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
    dag_flow_b: Annotated[IsDagFlow, pytest.fixture],
):
    for job_a, job_b in [(task_a, task_b), (dag_flow_a, dag_flow_b)]:
        job_b = copy(job_b)
        job_b.name = job_a.name
        job_b.unique_name = job_a.unique_name

        registry = RunStateRegistry()
        registry.set_job_state(job_a, RunState.INITIALIZED)
        registry.set_job_state(job_b, RunState.INITIALIZED)

        assert job_b.name == job_a.name
        assert job_b.unique_name != job_a.unique_name

        prev_unique_name = job_b.unique_name
        registry.set_job_state(job_b, RunState.RUNNING)
        assert job_b.name == job_a.name
        assert job_b.unique_name == prev_unique_name


def test_state_change_logging(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    task_a: Annotated[IsTask, pytest.fixture],
    task_b: Annotated[IsTask, pytest.fixture],
    dag_flow_a: Annotated[IsDagFlow, pytest.fixture],
    dag_flow_b: Annotated[IsDagFlow, pytest.fixture],
):
    simple_logger.addHandler(logging.StreamHandler(str_stream))

    for job_a, job_b in [(task_a, task_b), (dag_flow_a, dag_flow_b)]:
        registry = RunStateRegistry()
        registry.set_logger(simple_logger)

        events = [
            (job_a, RunState.INITIALIZED),
            (job_a, RunState.RUNNING),
            (job_b, RunState.INITIALIZED),
            (job_a, RunState.FINISHED),
            (job_b, RunState.RUNNING),
            (job_b, RunState.FINISHED),
        ]

        datetime_list = []
        for job, state in events:
            registry.set_job_state(job, state)
            datetime_list.append(registry.get_job_state_datetime(job, state))

        log_lines = read_log_lines_from_stream(str_stream)

        assert len(log_lines) == 6

        assert log_lines[0] == f'INFO (test) - ' \
                               f'{datetime_list[0].strftime(get_datetime_format())}: ' \
                               f'Initialized "{job_a.unique_name}"'
        assert log_lines[1] == f'INFO (test) - ' \
                               f'{datetime_list[1].strftime(get_datetime_format())}: ' \
                               f'Started running "{job_a.unique_name}"...'
        assert log_lines[2] == f'INFO (test) - ' \
                               f'{datetime_list[2].strftime(get_datetime_format())}: ' \
                               f'Initialized "{job_b.unique_name}"'
        assert log_lines[3] == f'INFO (test) - ' \
                               f'{datetime_list[3].strftime(get_datetime_format())}: ' \
                               f'Finished running "{job_a.unique_name}"!'
        assert log_lines[4] == f'INFO (test) - ' \
                               f'{datetime_list[4].strftime(get_datetime_format())}: ' \
                               f'Started running "{job_b.unique_name}"...'
        assert log_lines[5] == f'INFO (test) - ' \
                               f'{datetime_list[5].strftime(get_datetime_format())}: ' \
                               f'Finished running "{job_b.unique_name}"!'


def test_state_change_logging_unset(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    task_a: Annotated[IsTask, pytest.fixture],
):
    simple_logger.addHandler(logging.StreamHandler(str_stream))

    registry = RunStateRegistry()
    registry.set_logger(simple_logger)

    registry.set_job_state(task_a, RunState.INITIALIZED)
    _assert_log_lines_from_stream(1, str_stream)

    registry.set_logger(None)
    registry.set_job_state(task_a, RunState.RUNNING)
    _assert_log_lines_from_stream(0, str_stream)

    registry.set_logger(simple_logger)
    registry.set_job_state(task_a, RunState.FINISHED)
    _assert_log_lines_from_stream(1, str_stream)


def _assert_log_lines_from_stream(num_log_lines, str_stream):
    log_lines = read_log_lines_from_stream(str_stream)
    assert len(log_lines) == num_log_lines
    for log_line in log_lines:
        assert 'INFO (test)' in log_line
    return log_lines


def test_state_change_logging_handler_formatting_variants(
    str_stream: Annotated[StringIO, pytest.fixture],
    simple_logger: Annotated[logging.Logger, pytest.fixture],
    task_a: Annotated[IsTask, pytest.fixture],
):
    registry = RunStateRegistry()

    # Handler added after set_logger
    registry.set_logger(simple_logger, set_omnipy_formatter_on_handlers=True)
    simple_logger.addHandler(logging.StreamHandler(str_stream))
    registry.set_job_state(task_a, RunState.INITIALIZED)

    log_line = read_log_line_from_stream(str_stream)
    assert 'INFO (test)' not in log_line

    # Handler added before set_logger, set_omnipy_formatter_on_handlers=False
    registry.set_logger(simple_logger, set_omnipy_formatter_on_handlers=False)
    registry.set_job_state(task_a, RunState.RUNNING)

    log_line = read_log_line_from_stream(str_stream)
    assert 'INFO (test)' not in log_line

    # Handler added before set_logger, set_omnipy_formatter_on_handlers=True
    registry.set_logger(simple_logger, set_omnipy_formatter_on_handlers=True)
    registry.set_job_state(task_a, RunState.FINISHED)

    log_line = read_log_line_from_stream(str_stream)

    assert 'INFO (test)' in log_line


def test_state_change_logging_date_localization(
    str_stream: Annotated[StringIO, pytest.fixture],
    stream_logger: Annotated[logging.Logger, pytest.fixture],
    task_a: Annotated[IsTask, pytest.fixture],
):
    registry = RunStateRegistry()

    locale = ('de_DE', 'UTF-8')
    registry.set_logger(stream_logger, locale=locale)

    registry.set_job_state(task_a, RunState.INITIALIZED)

    log_lines = _assert_log_lines_from_stream(1, str_stream)

    _assert_localized_datetime_for_log_line(registry, locale, task_a, log_lines, 0)


def _assert_localized_datetime_for_log_line(registry, locale, job, log_lines, line_index):
    init_datetime = registry.get_job_state_datetime(job, RunState.INITIALIZED)
    assert init_datetime.strftime(get_datetime_format(locale)) in log_lines[line_index]
    assert 'INFO (test)' in log_lines[0]
