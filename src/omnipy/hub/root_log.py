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


@dataclass
class RootLogConfigEntryPublisher(RootLogConfig, RuntimeEntryPublisher):
    ...


@dataclass
class RootLogObjects:
    _config: IsRootLogConfig = field(
        init=False, repr=False, default_factory=RootLogConfigEntryPublisher)
    stdout_handler: Optional[StreamHandler] = None
    stderr_handler: Optional[StreamHandler] = None
    file_handler: Optional[TimedRotatingFileHandler] = None

    def __post_init__(self):
        self._configure_all_handlers()

    def set_config(self, config: IsRootLogConfig):
        self._remove_all_handlers_from_root_logger()
        self._config = config
        self._configure_all_handlers()

    def _configure_all_handlers(self):
        self._configure_stdout_handler()
        self._configure_stderr_handler()
        self._configure_file_handler()

        self._add_all_handlers_to_root_logger()

    def _remove_all_handlers_from_root_logger(self):
        root_logger = logging.root
        root_logger.removeHandler(self.stdout_handler)
        root_logger.removeHandler(self.stderr_handler)
        root_logger.removeHandler(self.file_handler)

    def _add_all_handlers_to_root_logger(self):
        root_logger = logging.root
        root_logger.addHandler(self.stdout_handler)
        root_logger.addHandler(self.stderr_handler)
        root_logger.addHandler(self.file_handler)

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
