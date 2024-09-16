from datetime import datetime
from logging import getLogger, INFO, Logger
import time


class LogMixin:
    def __init__(self) -> None:
        self._logger: Logger = getLogger(f'{self.__class__.__module__}.{self.__class__.__name__}')
        self._logger.setLevel(INFO)

    @property
    def logger(self) -> Logger:
        return self._logger

    def log(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None):
        if self._logger is not None:
            create_time = datetime_obj.timestamp() if datetime_obj else time.time()
            self._logger.log(level, log_msg, extra=dict(timestamp=create_time))
