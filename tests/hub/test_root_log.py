from datetime import datetime
from io import StringIO
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
import time
from typing import Annotated, Optional, Type

import pytest

from log.helpers.functions import assert_log_lines_from_stream
import omnipy
from omnipy.api.protocols import IsRootLogConfig, IsRootLogConfigEntryPublisher, IsRuntime
from omnipy.api.types import LocaleType
from omnipy.config.root_log import RootLogConfig
from omnipy.hub.root_log import RootLogObjects
from omnipy.util.helpers import get_datetime_format


def _assert_root_log_config_default(root_log: RootLogConfig, dir_path: str):
    assert isinstance(root_log, RootLogConfig)
    assert isinstance(root_log.locale, (str, tuple))

    assert root_log.log_format_str == '%(asctime)s: %(levelname)s - %(message)s (%(name)s)'
    assert root_log.log_to_stdout is True
    assert root_log.log_to_stderr is True
    assert root_log.log_to_file is True
    assert root_log.stdout_log_min_level == logging.INFO
    assert root_log.stderr_log_min_level == logging.ERROR
    assert root_log.file_log_min_level == logging.WARNING
    assert root_log.file_log_dir_path == os.path.join(dir_path, 'logs')


def _log_record_for_level(level: int):
    test_logger = logging.getLogger('test_logger')
    return test_logger.makeRecord(
        name=test_logger.name, level=level, fn='', lno=0, msg='my log msg', args=(), exc_info=None)


def _assert_root_log_formatter(
    formatter: Optional[logging.Formatter],
    root_log_config: IsRootLogConfig,
):
    if root_log_config.log_format_str:
        assert formatter
        record = _log_record_for_level(logging.DEBUG)
        fixed_datetime_now = datetime.now()
        record.created = time.mktime(fixed_datetime_now.timetuple())

        formatted_record = formatter.format(record)

        assert 'DEBUG - my log msg (test_logger)' in formatted_record
        assert fixed_datetime_now.strftime(get_datetime_format(
            root_log_config.locale)) in formatted_record


def _assert_root_stdout_handler(root_stdout_handler: Optional[logging.StreamHandler],
                                root_log_config: IsRootLogConfig):
    if root_log_config.log_to_stdout:
        assert isinstance(root_stdout_handler, logging.StreamHandler)
        assert root_stdout_handler.stream is omnipy.hub.root_log.stdout
        assert root_stdout_handler.level == root_log_config.stdout_log_min_level

        for level in [
                logging.NOTSET,
                logging.DEBUG,
                logging.INFO,
                logging.WARNING,
                logging.ERROR,
                logging.CRITICAL
        ]:
            if root_log_config.stdout_log_min_level <= level:
                if root_log_config.log_to_stderr and root_log_config.stderr_log_min_level <= level:
                    assert root_stdout_handler.filter(_log_record_for_level(level)) is False
                else:
                    assert root_stdout_handler.filter(_log_record_for_level(level)) is True
    else:
        assert root_stdout_handler is None


def _assert_root_stderr_handler(root_stderr_handler: Optional[logging.StreamHandler],
                                root_log_config: IsRootLogConfig):
    if root_log_config.log_to_stderr:
        assert isinstance(root_stderr_handler, logging.StreamHandler)
        assert root_stderr_handler.stream is omnipy.hub.root_log.stderr
        assert root_stderr_handler.level == root_log_config.stderr_log_min_level
    else:
        assert root_stderr_handler is None


def _assert_root_file_handler(root_file_handler: Optional[TimedRotatingFileHandler],
                              root_log_config: IsRootLogConfig):
    if root_log_config.log_to_file:
        assert isinstance(root_file_handler, TimedRotatingFileHandler)
        assert root_file_handler.when == 'D'
        assert root_file_handler.interval == 60 * 60 * 24
        assert root_file_handler.backupCount == 7
        assert root_file_handler.level == root_log_config.file_log_min_level
        assert root_file_handler.baseFilename == \
               str(Path(root_log_config.file_log_dir_path).joinpath('omnipy.log'))
    else:
        assert root_file_handler is None


def _assert_root_log_objects(
    root_log_objects: RootLogObjects,
    root_log_config: IsRootLogConfig,
) -> None:
    _assert_root_log_formatter(root_log_objects.formatter, root_log_config)
    _assert_root_stdout_handler(root_log_objects.stdout_handler, root_log_config)
    _assert_root_stderr_handler(root_log_objects.stderr_handler, root_log_config)
    _assert_root_file_handler(root_log_objects.file_handler, root_log_config)

    root_handlers = logging.root.handlers
    for handler in [
            root_log_objects.stdout_handler,
            root_log_objects.stderr_handler,
            root_log_objects.file_handler,
    ]:
        if handler:
            assert handler.formatter is root_log_objects.formatter
            assert handler in root_handlers


def test_root_log_config_default(teardown_rm_root_log_dir: Annotated[None, pytest.fixture]) -> None:
    _assert_root_log_config_default(RootLogConfig(), str(Path.cwd()))


def test_root_log_objects_default(
        teardown_rm_root_log_dir: Annotated[None, pytest.fixture]) -> None:
    _assert_root_log_objects(RootLogObjects(), RootLogConfig())


def test_runtime_root_log_config(
    runtime: Annotated[IsRuntime, pytest.fixture],
    tmp_dir_path: Annotated[str, pytest.fixture],
) -> None:
    assert isinstance(runtime.config.root_log, RootLogConfig)
    assert isinstance(runtime.objects.root_log, RootLogObjects)

    _assert_root_log_config_default(runtime.config.root_log, tmp_dir_path)
    _assert_root_log_objects(runtime.objects.root_log, runtime.config.root_log)


def test_root_log_config_dependencies(runtime: Annotated[IsRuntime, pytest.fixture],
                                      tmp_dir_path: Annotated[str, pytest.fixture]) -> None:
    runtime.config.root_log.log_to_stdout = False
    runtime.config.root_log.log_to_stderr = False

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_stdout = False
    runtime.config.root_log.log_to_stderr = True
    runtime.config.root_log.stderr_log_min_level = logging.WARNING

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_stdout = True
    runtime.config.root_log.log_to_stderr = False
    runtime.config.root_log.stdout_log_min_level = logging.DEBUG

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_stdout = True
    runtime.config.root_log.log_to_stderr = True
    runtime.config.root_log.stdout_log_min_level = logging.INFO
    runtime.config.root_log.stderr_log_min_level = logging.WARNING

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_stdout = True
    runtime.config.root_log.log_to_stderr = True
    runtime.config.root_log.stdout_log_min_level = logging.WARNING
    runtime.config.root_log.stderr_log_min_level = logging.INFO

    _assert_root_stdout_handler(runtime.objects.root_log.stdout_handler, runtime.config.root_log)
    _assert_root_stderr_handler(runtime.objects.root_log.stderr_handler, runtime.config.root_log)

    runtime.config.root_log.log_to_file = True
    runtime.config.root_log.file_log_min_level = logging.INFO
    runtime.config.root_log.file_log_dir_path = str(Path(tmp_dir_path).joinpath('extra_level'))

    _assert_root_file_handler(runtime.objects.root_log.file_handler, runtime.config.root_log)


def test_log_formatter_date_localization(runtime: Annotated[IsRuntime, pytest.fixture],):
    fixed_datetime_now = datetime.now()
    prev_formatter = runtime.objects.root_log.formatter

    prev_locale = runtime.config.root_log.locale
    runtime.config.root_log.locale = ('de_DE', 'UTF-8')
    new_formatter = runtime.objects.root_log.formatter

    assert new_formatter
    assert new_formatter is not prev_formatter

    formatted_log_entry = new_formatter.format(_log_record_for_level(logging.INFO))

    log_lines = assert_log_lines_from_stream(1, StringIO(formatted_log_entry))

    locale: LocaleType = runtime.config.root_log.locale
    assert fixed_datetime_now.strftime(get_datetime_format(locale)) in log_lines[0]
    assert '(test_logger)' in log_lines[0]

    runtime.config.root_log.locale = prev_locale
    newer_formatter = runtime.objects.root_log.formatter

    assert newer_formatter
    assert newer_formatter is not new_formatter
