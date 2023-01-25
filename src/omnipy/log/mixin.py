from datetime import datetime
import logging
import sys
from typing import Optional, Tuple, Union

from omnipy.api.constants import OMNIPY_LOG_FORMAT_STR
from omnipy.util.helpers import get_datetime_format


class LogDynMixin:
    def __init__(self) -> None:
        if not logging.root.handlers:
            pass
        self._datetime_format: str = get_datetime_format()
        self._logger: Optional[logging.Logger] = logging.getLogger(
            f'{self.__class__.__module__}.{self.__class__.__name__}')
        self._logger.addHandler(logging.StreamHandler(sys.stderr))
        self._set_omnipy_formatter_on_handlers()

    # def log(self, msg: str, level: int = logging.INFO):
    #     logger = getLogger(__name__)
    #     logger.log(level, f'{msg} {self.__class__.__module__}.{self.__class__.__name__}')

    def log(self, log_msg: str, level: int = logging.INFO, datetime_obj: Optional[datetime] = None):
        if self._logger is not None:
            if datetime_obj is None:
                datetime_obj = datetime.now()

            datetime_str = datetime_obj.strftime(self._datetime_format)
            self._logger.log(level, f'{datetime_str}: {log_msg}')
            # self._logger.info(f'{datetime_str}: {log_msg}')

    def set_logger(self,
                   logger: Optional[logging.Logger],
                   set_omnipy_formatter_on_handlers=True,
                   locale: Union[str, Tuple[str, str]] = '') -> None:

        self._logger = logger
        if locale:
            self._datetime_format = get_datetime_format(locale)

        if self._logger is not None:
            if set_omnipy_formatter_on_handlers:
                self._set_omnipy_formatter_on_handlers()

    def _set_omnipy_formatter_on_handlers(self):
        formatter = logging.Formatter(OMNIPY_LOG_FORMAT_STR)
        for handler in self._logger.handlers:
            handler.setFormatter(formatter)

    @property
    def logger(self):
        return self._logger
