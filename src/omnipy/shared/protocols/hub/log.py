"""Protocols for objects that expose Omnipy logging helpers."""

from datetime import datetime
from logging import INFO, Logger
from typing import Protocol


class CanLog(Protocol):
    """Protocol for objects that expose a logger and log helper."""

    @property
    def logger(self) -> Logger:
        ...

    def log(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None):
        ...
