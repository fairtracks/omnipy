from datetime import datetime
from logging import Formatter, getLogger, Handler, INFO, Logger, root, StreamHandler, WARN
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
import sys
from typing import Optional, Tuple, Union

from omnipy.log.constants import OMNIPY_LOG_FORMAT_STR
from omnipy.util.helpers import get_datetime_format


class LogMixin:
    def __init__(self) -> None:
        self._datetime_format: str = get_datetime_format()
        self._logger: Optional[Logger] = getLogger(
            f'{self.__class__.__module__}.{self.__class__.__name__}')
        self._logger.setLevel(INFO)

    def log(self, log_msg: str, level: int = INFO, datetime_obj: Optional[datetime] = None):
        if self._logger is not None:
            if datetime_obj is None:
                datetime_obj = datetime.now()

            datetime_str = datetime_obj.strftime(self._datetime_format)
            self._logger.log(level, f'{datetime_str}: {log_msg}')

    @property
    def logger(self):
        return self._logger
