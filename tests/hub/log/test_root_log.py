from datetime import datetime, timedelta
from io import StringIO
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys
import time
from typing import Annotated, TextIO

import pytest

from omnipy.api.protocols.public.hub import IsRuntime
from omnipy.api.typedefs import LocaleType
from omnipy.config.root_log import RootLogConfig
from omnipy.hub.log.root_log import RootLogObjects
from omnipy.util.helpers import get_datetime_format

from .helpers.functions import assert_log_line_from_stream, read_log_line_from_stream


def _assert_root_log_config_default(root_log: RootLogConfig, dir_path: Path):
    assert isinstance(root_log, RootLogConfig)
    assert isinstance(root_log.locale, (str, tuple))

    assert root_log.log_format_str == '[{engine}] {asctime} - {levelname}: {message} ({name})'
    assert root_log.log_to_stdout is True
    assert root_log.log_to_stderr is True
    assert root_log.log_to_file is True
    assert root_log.stdout is sys.stdout
    assert root_log.stderr is sys.stderr
    assert root_log.stdout_log_min_level == logging.INFO
    assert root_log.stderr_log_min_level == logging.ERROR
    assert root_log.file_log_min_level == logging.WARNING
    assert root_log.file_log_path == str(dir_path / 'logs' / 'omnipy.log')


def _assert_root_log_objects(root_log_objects: RootLogObjects,) -> None:
    assert isinstance(root_log_objects.formatter, logging.Formatter)
    assert isinstance(root_log_objects.stdout_handler, logging.StreamHandler)
    assert isinstance(root_log_objects.stderr_handler, logging.StreamHandler)
    assert isinstance(root_log_objects.file_handler, RotatingFileHandler)


def test_root_log_config_default() -> None:
    _assert_root_log_config_default(RootLogConfig(), Path.cwd())


def test_root_log_objects_default(
        teardown_rm_default_root_log_dir: Annotated[None, pytest.fixture]) -> None:
    _assert_root_log_objects(RootLogObjects())


def test_runtime_root_log_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    tmp_dir_path: Annotated[Path, pytest.fixture],
) -> None:
    assert isinstance(runtime.config.root_log, RootLogConfig)
    assert isinstance(runtime.objects.root_log, RootLogObjects)

    _assert_root_log_config_default(runtime.config.root_log, tmp_dir_path)
    _assert_root_log_objects(runtime.objects.root_log)


def _log_record_for_level(level: int, datetime_obj: datetime | None = None):
    test_logger = logging.getLogger('test.logger')
    record = test_logger.makeRecord(
        name=test_logger.name, level=level, fn='', lno=0, msg='my log msg', args=(), exc_info=None)
    record.engine = 'TEST'
    if datetime_obj:
        record.created = time.mktime(datetime_obj.timetuple())
    return record


def test_log_formatter(runtime: Annotated[IsRuntime, pytest.fixture]):
    locale = runtime.config.root_log.locale
    formatter = runtime.objects.root_log.formatter
    assert formatter

    fixed_datetime = datetime(2024, 1, 1, 12, 0, 0)

    record = _log_record_for_level(logging.DEBUG, datetime_obj=fixed_datetime)
    formatted_record = formatter.format(record)

    formatted_time = fixed_datetime.strftime(get_datetime_format(locale))
    assert formatted_record == f'[TEST] {formatted_time} - DEBUG: my log msg (test.logger)'


def test_log_formatter_date_localization(runtime: Annotated[IsRuntime, pytest.fixture]):
    fixed_datetime_now = datetime.now()
    prev_formatter = runtime.objects.root_log.formatter

    prev_locale = runtime.config.root_log.locale
    runtime.config.root_log.locale = ('de_DE', 'UTF-8')
    new_formatter = runtime.objects.root_log.formatter

    assert new_formatter
    assert new_formatter is not prev_formatter

    formatted_log_entry = new_formatter.format(
        _log_record_for_level(logging.INFO, datetime_obj=fixed_datetime_now))

    locale: LocaleType = runtime.config.root_log.locale
    datetime_str = fixed_datetime_now.strftime(get_datetime_format(locale))

    assert_log_line_from_stream(
        StringIO(formatted_log_entry),
        level='INFO',
        logger='test.logger',
        datetime_str=datetime_str,
    )

    runtime.config.root_log.locale = prev_locale
    newer_formatter = runtime.objects.root_log.formatter

    assert newer_formatter
    assert newer_formatter is not new_formatter


@pytest.fixture
def logger() -> logging.Logger:
    logger = logging.getLogger('tests.hub.test_root_log')
    logger.setLevel(logging.DEBUG)
    return logger


def _log_and_assert_log_line_from_stream(
        runtime: IsRuntime,
        logger: logging.Logger,
        level: int,
        stream: TextIO,
        datetime_obj: datetime = datetime.now(),
):
    logger.log(level, 'Test log message', extra={'timestamp': datetime_obj.timestamp()})
    assert_log_line_from_stream(
        stream,
        level=logging.getLevelName(level),
        logger='tests.hub.test_root_log',
        engine='TESTS',
        datetime_str=datetime_obj.strftime(get_datetime_format(runtime.config.root_log.locale)),
    )


def _log_and_assert_no_stream_output(logger: logging.Logger, level: int, stream: TextIO):
    logger.log(level, 'Test log message')
    assert read_log_line_from_stream(stream) == ''


def test_log_to_stdout_with_toggle(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    my_stdout = StringIO()
    runtime.config.root_log.stdout = my_stdout

    assert runtime.config.root_log.log_to_stdout is True
    _log_and_assert_log_line_from_stream(runtime, logger, logging.INFO, my_stdout)

    runtime.config.root_log.log_to_stdout = False
    _log_and_assert_no_stream_output(logger, logging.INFO, my_stdout)


def test_log_to_stdout_with_level_cutoff(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    my_stdout = StringIO()
    runtime.config.root_log.stdout = my_stdout

    assert runtime.config.root_log.stdout_log_min_level == logging.INFO
    _log_and_assert_no_stream_output(logger, logging.DEBUG, my_stdout)

    runtime.config.root_log.stdout_log_min_level = logging.DEBUG
    _log_and_assert_log_line_from_stream(runtime, logger, logging.DEBUG, my_stdout)


def test_log_to_stdout_with_specific_datetime(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    my_stdout = StringIO()
    runtime.config.root_log.stdout = my_stdout

    specific_date = datetime(2021, 1, 1, 12, 0, 0)
    _log_and_assert_log_line_from_stream(runtime, logger, logging.INFO, my_stdout, specific_date)


def test_do_not_log_to_stdout_if_logging_to_stderr_with_toggle(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    my_stdout = StringIO()
    runtime.config.root_log.stdout = my_stdout

    assert runtime.config.root_log.log_to_stderr is True
    _log_and_assert_no_stream_output(logger, logging.ERROR, my_stdout)

    runtime.config.root_log.log_to_stderr = False
    _log_and_assert_log_line_from_stream(runtime, logger, logging.ERROR, my_stdout)


def test_do_not_log_to_stdout_if_logging_to_stderr_with_level_cutoff(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    my_stdout = StringIO()
    runtime.config.root_log.stdout = my_stdout

    assert runtime.config.root_log.stderr_log_min_level == logging.ERROR
    _log_and_assert_no_stream_output(logger, logging.ERROR, my_stdout)

    runtime.config.root_log.stderr_log_min_level = logging.CRITICAL
    _log_and_assert_log_line_from_stream(runtime, logger, logging.ERROR, my_stdout)


def test_log_to_stderr_with_toggle(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    my_stderr = StringIO()
    runtime.config.root_log.stderr = my_stderr

    assert runtime.config.root_log.log_to_stderr is True
    _log_and_assert_log_line_from_stream(runtime, logger, logging.ERROR, my_stderr)

    runtime.config.root_log.log_to_stderr = False
    _log_and_assert_no_stream_output(logger, logging.ERROR, my_stderr)


def test_log_to_stderr_with_level_cutoff(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    my_stderr = StringIO()
    runtime.config.root_log.stderr = my_stderr

    assert runtime.config.root_log.stderr_log_min_level == logging.ERROR
    _log_and_assert_no_stream_output(logger, logging.WARNING, my_stderr)

    runtime.config.root_log.stderr_log_min_level = logging.WARNING
    _log_and_assert_log_line_from_stream(runtime, logger, logging.WARNING, my_stderr)


def test_log_to_stderr_with_specific_datetime(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    my_stderr = StringIO()
    runtime.config.root_log.stderr = my_stderr

    specific_date = datetime(2021, 1, 1, 12, 0, 0)
    _log_and_assert_log_line_from_stream(runtime, logger, logging.ERROR, my_stderr, specific_date)


def test_log_to_file_with_toggle(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    log_file_path = runtime.config.root_log.file_log_path

    assert runtime.config.root_log.log_to_file is True
    assert os.path.exists(log_file_path)
    with open(log_file_path, 'r+') as log_file:
        _log_and_assert_log_line_from_stream(runtime, logger, logging.WARNING, log_file)

    runtime.config.root_log.log_to_file = False
    with open(log_file_path, 'r+') as log_file:
        _log_and_assert_no_stream_output(logger, logging.WARNING, log_file)


def test_log_to_file_with_level_cutoff(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    log_file_path = runtime.config.root_log.file_log_path

    assert runtime.config.root_log.file_log_min_level is logging.WARNING
    assert os.path.exists(log_file_path)
    with open(log_file_path, 'r+') as log_file:
        _log_and_assert_log_line_from_stream(runtime, logger, logging.WARNING, log_file)

    runtime.config.root_log.file_log_min_level = logging.ERROR
    with open(log_file_path, 'r+') as log_file:
        _log_and_assert_no_stream_output(logger, logging.WARNING, log_file)


def test_log_to_file_with_specific_datetime(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    log_file_path = runtime.config.root_log.file_log_path

    specific_date = datetime(2021, 1, 1, 12, 0, 0)
    with open(log_file_path, 'r+') as log_file:
        _log_and_assert_log_line_from_stream(runtime,
                                             logger,
                                             logging.WARNING,
                                             log_file,
                                             specific_date)


def test_daily_log_file_rotation(
    runtime: Annotated[IsRuntime, pytest.fixture],
    logger: Annotated[logging.Logger, pytest.fixture],
):
    log_file_path = runtime.config.root_log.file_log_path

    now = datetime.now()
    log_datetimes: list[datetime] = []

    for i in range(9):
        log_datetimes.append(now + timedelta(days=i))
        logger.log(
            logging.WARNING,
            'Test log message',
            extra={'timestamp': log_datetimes[-1].timestamp()},
        )

        for j, log_datetime in enumerate(reversed(log_datetimes)):
            if j == 0:
                log_file_path_to_check = log_file_path
            else:
                log_file_path_to_check = f"{log_file_path}.{j}"

                if j % 2 == 0:
                    # Simulates that omnipy is running for two days at a time, and then restarted.
                    # Setting the log file path config resets the log file handlers, which clears
                    # any in-memory state of the log file handlers, including the current date.
                    # Hence, this tests that the log file handler correctly rolls over the log file
                    # when the date changes, even if the application is restarted.
                    runtime.config.root_log.file_log_path = log_file_path

            if j == 8:
                # The first log file should have been deleted, as backupCount is 7.
                assert not os.path.exists(log_file_path_to_check)
            else:
                with open(log_file_path_to_check, 'r+') as log_file:
                    assert_log_line_from_stream(
                        log_file,
                        level='WARNING',
                        logger='tests.hub.test_root_log',
                        engine='TESTS',
                        datetime_str=log_datetime.strftime(
                            get_datetime_format(runtime.config.root_log.locale)),
                        clear_stream=False,
                    )
