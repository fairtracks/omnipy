"""Shared logging mixin for Omnipy runtime, hub and data objects."""

from datetime import datetime
from logging import getLogger, INFO, Logger
import time


class LogMixin:
    """Provide a logger named after the concrete class and timestamp-aware convenience logging.

    The mixin keeps no instance state, so that it can also be used by pydantic-based classes,
    such as Model and Dataset.
    """

    def get_logger(self) -> Logger:
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CANLOG_GET_LOGGER_SUMMARY}}
        #
        # {{CANLOG_GET_LOGGER_DETAILS}}
        """Return the logger bound to the concrete instance type.

        Returns:
            Logger: Logger used by the object for Omnipy log messages.
        """
        logger = getLogger(f'{self.__class__.__module__}.{self.__class__.__name__}')
        logger.setLevel(INFO)
        return logger

    def log_message(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None):
        # %% Original docstring (managed by expand_docstr_macros.py) %%
        # {{CANLOG_LOG_MESSAGE_SUMMARY}}
        #
        # {{CANLOG_LOG_MESSAGE_DETAILS}}
        """Emit a log message, optionally using an explicit event timestamp.

        Args:
            log_msg: Message text to send to the logger.
            level: Standard library logging level.
            datetime_obj: Timestamp to attach to the record instead of wall-clock time.
        """
        create_time = datetime_obj.timestamp() if datetime_obj else time.time()
        self.get_logger().log(level, log_msg, extra=dict(timestamp=create_time))
