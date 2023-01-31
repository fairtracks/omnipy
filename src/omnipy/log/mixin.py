from datetime import datetime
from logging import Formatter, getLogger, Handler, INFO, Logger, root, StreamHandler, WARN
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
import sys
from typing import Optional, Tuple, Union

from omnipy.api.constants import OMNIPY_LOG_FORMAT_STR
from omnipy.util.helpers import get_datetime_format


class LogMixin:
    _added_root_handler = False

    def __init__(self, *, log_dir_path: str = None) -> None:
        if log_dir_path and not self._added_root_handler:
            #
            # log_file_path = Path(log_dir_path).joinpath('omnipy.log')
            #
            # if not os.path.exists(log_dir_path):
            #     os.makedirs(log_dir_path)
            #
            # for handler in root.handlers:
            #     if handler.__class__.__name__ == 'PrefectConsoleHandler':
            #         root.removeHandler(handler)
            #
            # fileHandler = TimedRotatingFileHandler(
            #     log_file_path, when='d', interval=1, backupCount=7)
            # fileHandler.setLevel(WARN)
            # self._set_omnipy_formatter_on_handler(fileHandler)
            #
            # root.addHandler(fileHandler)

            self._added_root_handler = True

        self._datetime_format: str = get_datetime_format()
        self._logger: Optional[Logger] = getLogger(
            f'{self.__class__.__module__}.{self.__class__.__name__}')
        self._logger.setLevel(INFO)

        handler = StreamHandler(sys.stderr)
        # handler.setLevel(INFO)
        if not any(isinstance(h, StreamHandler) for h in self._logger.handlers):
            self._logger.addHandler(handler)
            self._set_omnipy_formatter_on_handlers()

    # def log(self, msg: str, level: int = INFO):
    #     logger = getLogger(__name__)
    #     logger.log(level, f'{msg} {self.__class__.__module__}.{self.__class__.__name__}')

    def log(self, log_msg: str, level: int = INFO, datetime_obj: Optional[datetime] = None):
        if self._logger is not None:
            if datetime_obj is None:
                datetime_obj = datetime.now()

            datetime_str = datetime_obj.strftime(self._datetime_format)
            self._logger.log(level, f'{datetime_str}: {log_msg}')
            # self._logger.info(f'{datetime_str}: {log_msg}')

    def set_logger(self,
                   logger: Optional[Logger],
                   set_omnipy_formatter_on_handlers=True,
                   locale: Union[str, Tuple[str, str]] = '') -> None:

        self._logger = logger
        if locale:
            self._datetime_format = get_datetime_format(locale)

        if self._logger is not None:
            if set_omnipy_formatter_on_handlers:
                self._set_omnipy_formatter_on_handlers()

    def _set_omnipy_formatter_on_handlers(self):
        for handler in self._logger.handlers:
            self._set_omnipy_formatter_on_handler(handler)

    def _set_omnipy_formatter_on_handler(self, handler: Handler):
        formatter = Formatter(OMNIPY_LOG_FORMAT_STR)
        handler.setFormatter(formatter)

    @property
    def logger(self):
        return self._logger
