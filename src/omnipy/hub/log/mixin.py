"""Shared logging mixin for Omnipy runtime and hub objects."""

from datetime import datetime
from logging import getLogger, INFO, Logger
import time


class LogMixin:
    """Provide a module-scoped logger and timestamp-aware convenience logging."""

    def __init__(self) -> None:
        self._logger: Logger = getLogger(f'{self.__class__.__module__}.{self.__class__.__name__}')
        self._logger.setLevel(INFO)

    @property
    def logger(self) -> Logger:
        """Return the logger bound to the concrete instance type."""
        return self._logger

    def log(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None):
        """Emit a log message, optionally using an explicit event timestamp.

        Args:
            log_msg: Message text to send to the logger.
            level: Standard library logging level.
            datetime_obj: Timestamp to attach to the record instead of wall-clock time.
        """
        if self._logger is not None:
            create_time = datetime_obj.timestamp() if datetime_obj else time.time()
            self._logger.log(level, log_msg, extra=dict(timestamp=create_time))
