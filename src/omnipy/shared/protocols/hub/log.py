from datetime import datetime
from logging import INFO, Logger
from typing import Protocol


class CanLog(Protocol):
    """"""
    @property
    def logger(self) -> Logger:
        ...

    def log(self, log_msg: str, level: int = INFO, datetime_obj: datetime | None = None):
        ...
