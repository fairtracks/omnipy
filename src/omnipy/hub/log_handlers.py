from datetime import date, datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class DailyRotatingFileHandler(RotatingFileHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._last_log_date_file_path: str = str(
            Path(self.baseFilename).parent / '_last_log_date.txt')
        self._last_log_date: date | None = self._read_log_date()

    @staticmethod
    def _get_date_from_created(record: logging.LogRecord) -> date:
        return datetime.fromtimestamp(record.created).date()

    def _store_log_date(self, log_date: date) -> None:
        self._last_log_date = log_date
        with open(self._last_log_date_file_path, 'w') as cur_date_file:
            cur_date_file.write(self._last_log_date.isoformat())

    def _read_log_date(self) -> date | None:
        try:
            with open(self._last_log_date_file_path, 'r') as cur_date_file:
                return date.fromisoformat(cur_date_file.read())
        except FileNotFoundError:
            return None

    def shouldRollover(self, record: logging.LogRecord) -> bool:
        if super().shouldRollover(record):
            return True

        log_date = self._get_date_from_created(record)
        if log_date != self._last_log_date:
            do_rollover = self._last_log_date is not None
            self._store_log_date(log_date)
            return do_rollover
        return False
