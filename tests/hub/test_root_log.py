import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
from typing import Annotated, Optional

import pytest

import omnipy
from omnipy.api.protocols import IsRuntime
from omnipy.config.root_log import RootLogConfig
from omnipy.hub.root_log import RootLogObjects


def _assert_root_log_config_default(root_log: RootLogConfig, dir_path: str):
    assert isinstance(root_log, RootLogConfig)

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


def _assert_root_stdout_handler(root_stdout_handler: Optional[logging.StreamHandler],
                                root_log_config: RootLogConfig):
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
                                root_log_config: RootLogConfig):
    if root_log_config.log_to_stderr:
        assert isinstance(root_stderr_handler, logging.StreamHandler)
        assert root_stderr_handler.stream is omnipy.hub.root_log.stderr
        assert root_stderr_handler.level == root_log_config.stderr_log_min_level
    else:
        assert root_stderr_handler is None


def _assert_root_file_handler(root_file_handler: Optional[TimedRotatingFileHandler],
                              root_log_config: RootLogConfig):
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


def _assert_root_log_objects(root_log_objects: RootLogObjects,
                             root_log_config: RootLogConfig) -> None:
    _assert_root_stdout_handler(root_log_objects.stdout_handler, root_log_config)
    _assert_root_stderr_handler(root_log_objects.stderr_handler, root_log_config)
    _assert_root_file_handler(root_log_objects.file_handler, root_log_config)

    root_handlers = logging.root.handlers
    assert root_log_objects.stdout_handler in root_handlers
    assert root_log_objects.stderr_handler in root_handlers
    assert root_log_objects.file_handler in root_handlers


def test_root_log_config_default(teardown_rm_root_log_dir: Annotated[None, pytest.fixture]) -> None:
    _assert_root_log_config_default(RootLogConfig(), str(Path.cwd()))


def test_root_log_objects_default(
        teardown_rm_root_log_dir: Annotated[None, pytest.fixture]) -> None:
    _assert_root_log_objects(RootLogObjects(), RootLogConfig())


def test_runtime_root_log_config(runtime: Annotated[IsRuntime, pytest.fixture],
                                 tmp_dir_path: Annotated[str, pytest.fixture]) -> None:
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
