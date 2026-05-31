"""Protocols for objects that expose Omnipy logging helpers."""

from datetime import datetime
from logging import INFO, Logger
import os
from textwrap import dedent
from typing import Protocol

from omnipy.util.helpers import is_package_editable

if is_package_editable('omnipy'):
    os.environ['OMNIPY_MACRO_CANLOG_LOGGER_SUMMARY'] = (
        'Return the logger bound to the concrete instance type.')
    os.environ['OMNIPY_MACRO_CANLOG_LOGGER_DETAILS'] = dedent("""\
        Returns:
            Logger: Logger used by the object for Omnipy log messages.
    """)

    os.environ['OMNIPY_MACRO_CANLOG_LOG_SUMMARY'] = (
        'Emit a log message, optionally using an explicit event timestamp.')
    os.environ['OMNIPY_MACRO_CANLOG_LOG_DETAILS'] = dedent("""\
        Args:
            log_msg: Message text to send to the logger.
            level: Standard library logging level.
            datetime_obj: Timestamp to attach to the record instead of wall-clock time.
    """)


class CanLog(Protocol):
    """Protocol for objects that expose a logger and log helper."""
    @property
    def logger(self) -> Logger:
        """{{CANLOG_LOGGER_SUMMARY}}

        {{CANLOG_LOGGER_DETAILS}}"""
        ...

    def log(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None):
        """{{CANLOG_LOG_SUMMARY}}

        {{CANLOG_LOG_DETAILS}}"""
        ...
