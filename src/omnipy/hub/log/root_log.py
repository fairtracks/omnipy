from dataclasses import dataclass, field
import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
import os

from omnipy.api.protocols.public.config import IsRootLogConfig
from omnipy.config.root_log import RootLogConfig
from omnipy.hub.log.handlers import DailyRotatingFileHandler
from omnipy.util.helpers import get_datetime_format
from omnipy.util.publisher import RuntimeEntryPublisher


@dataclass
class RootLogConfigEntryPublisher(RootLogConfig, RuntimeEntryPublisher):
    ...


@dataclass
class RootLogObjects:
    _config: IsRootLogConfig = field(
        init=False, repr=False, default_factory=RootLogConfigEntryPublisher)

    formatter: logging.Formatter | None = None
    stdout_handler: StreamHandler | None = None
    stderr_handler: StreamHandler | None = None
    file_handler: RotatingFileHandler | None = None

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

        filters = self._configure_common_filters()
        self._add_all_handlers_to_root_logger(filters)

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

            self.stdout_handler = StreamHandler(self._config.stdout)
            self.stdout_handler.setLevel(self._config.stdout_log_min_level)
            if self._config.log_to_stderr:
                self.stdout_handler.addFilter(StdErrBasedMaxLevelFilter())
        else:
            self.stdout_handler = None

    def _configure_stderr_handler(self) -> None:
        if self._config.log_to_stderr:
            self.stderr_handler = StreamHandler(self._config.stderr)
            self.stderr_handler.setLevel(self._config.stderr_log_min_level)
        else:
            self.stderr_handler = None

    def _configure_file_handler(self) -> None:
        if self._config.log_to_file:
            log_file_path = self._config.file_log_path
            log_dir_path = os.path.dirname(log_file_path)
            if not os.path.exists(log_dir_path):
                os.makedirs(log_dir_path)

            self.file_handler = DailyRotatingFileHandler(log_file_path, backupCount=7)
            self.file_handler.setLevel(self._config.file_log_min_level)
        else:
            self.file_handler = None

    def _configure_common_filters(self):
        class ExtractEngineFilter(logging.Filter):
            def filter(self, record):
                record.engine = f"{record.name.split('.')[0].upper()}"
                if len(record.engine) < 7:
                    record.engine += ' '
                return True

        class SetTimestampFilter(logging.Filter):
            def filter(self, record):
                if hasattr(record, 'timestamp'):
                    record.created = record.timestamp
                return True

        return [ExtractEngineFilter(), SetTimestampFilter()]

    def _remove_all_handlers_from_root_logger(self):
        root_logger = logging.root
        handlersToRemove = [
            handler for handler in root_logger.handlers
            if isinstance(handler, StreamHandler) or isinstance(handler, DailyRotatingFileHandler)
        ]
        for handler in handlersToRemove:
            root_logger.removeHandler(handler)

    def _add_handler_to_root_logger(
        self,
        handler: logging.Handler | None,
        filters: list[logging.Filter],
    ):
        if handler:
            root_logger = logging.root
            if self.formatter:
                handler.setFormatter(self.formatter)
            for filter in filters:
                handler.addFilter(filter)
            root_logger.addHandler(handler)

    def _add_all_handlers_to_root_logger(self, filters: list[logging.Filter]):
        self._add_handler_to_root_logger(self.stdout_handler, filters)
        self._add_handler_to_root_logger(self.stderr_handler, filters)
        self._add_handler_to_root_logger(self.file_handler, filters)
