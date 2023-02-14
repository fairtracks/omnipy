from dataclasses import dataclass, field
import logging
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
from sys import stderr, stdout
from typing import Optional

from omnipy.api.protocols import IsRootLogConfig
from omnipy.config.root_log import RootLogConfig
from omnipy.hub.entry import RuntimeEntryPublisher
from omnipy.util.helpers import get_datetime_format


@dataclass
class RootLogConfigEntryPublisher(RootLogConfig, RuntimeEntryPublisher):
    ...


@dataclass
class RootLogObjects:
    _config: IsRootLogConfig = field(
        init=False, repr=False, default_factory=RootLogConfigEntryPublisher)

    formatter: Optional[logging.Formatter] = None
    stdout_handler: Optional[StreamHandler] = None
    stderr_handler: Optional[StreamHandler] = None
    file_handler: Optional[TimedRotatingFileHandler] = None

    def __post_init__(self):
        self._configure_all_objects()

    def set_config(self, config: IsRootLogConfig):
        self._config = config
        self._configure_all_objects()

    def _configure_all_objects(self):
        self._remove_all_handlers_from_root_logger()

        self._configure_formatter()
        self._configure_stdout_handler()
        self._configure_stderr_handler()
        self._configure_file_handler()

        self._add_all_handlers_to_root_logger()

    def _configure_formatter(self):
        if self._config.log_format_str:
            datetime_fmt = get_datetime_format(self._config.locale)
            self.formatter = logging.Formatter(self._config.log_format_str, datetime_fmt, style='{')
        else:
            self.formatter = None

    def _configure_stdout_handler(self):
        if self._config.log_to_stdout:
            config = self._config

            class StdErrBasedMaxLevelFilter(logging.Filter):
                def filter(self, record):
                    return record.levelno < config.stderr_log_min_level

            self.stdout_handler = StreamHandler(stdout)
            self.stdout_handler.setLevel(self._config.stdout_log_min_level)
            if self._config.log_to_stderr:
                self.stdout_handler.addFilter(StdErrBasedMaxLevelFilter())
        else:
            self.stdout_handler = None

    def _configure_stderr_handler(self) -> Optional[StreamHandler]:
        if self._config.log_to_stderr:
            self.stderr_handler = StreamHandler(stderr)
            self.stderr_handler.setLevel(self._config.stderr_log_min_level)
        else:
            self.stderr_handler = None

    def _configure_file_handler(self) -> Optional[TimedRotatingFileHandler]:
        if self._config.log_to_file:
            log_dir_path = self._config.file_log_dir_path
            if not os.path.exists(log_dir_path):
                os.makedirs(log_dir_path)

            log_file_path = Path(log_dir_path).joinpath('omnipy.log')
            self.file_handler = TimedRotatingFileHandler(
                log_file_path, when='d', interval=1, backupCount=7)
            self.file_handler.setLevel(self._config.file_log_min_level)
        else:
            self.file_handler = None

    def _remove_all_handlers_from_root_logger(self):
        root_logger = logging.root
        handlersToRemove = [
            handler for handler in root_logger.handlers
            if isinstance(handler, StreamHandler) or isinstance(handler, TimedRotatingFileHandler)
        ]
        for handler in handlersToRemove:
            root_logger.removeHandler(handler)

    def _add_handler_to_root_logger(self, handler: Optional[logging.Handler]):
        if handler:
            root_logger = logging.root
            if self.formatter:
                handler.setFormatter(self.formatter)
            root_logger.addHandler(handler)

    def _add_all_handlers_to_root_logger(self):
        self._add_handler_to_root_logger(self.stdout_handler)
        self._add_handler_to_root_logger(self.stderr_handler)
        self._add_handler_to_root_logger(self.file_handler)
