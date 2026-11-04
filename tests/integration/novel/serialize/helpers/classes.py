"""Helper classes for serializer tests."""

from datetime import datetime
from logging import INFO

from typing_extensions import override

from omnipy.hub.log.mixin import LogMixin


class SilentLog(LogMixin):
    """Log object that discards all log messages."""

    @override
    def log_message(
        self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None
    ) -> None:
        pass
