from datetime import datetime
import logging
from logging import getLogger, INFO, Logger, LogRecord, makeLogRecord
import time
from typing import Optional


class LogMixin:
    def __init__(self) -> None:
        self._logger: Optional[Logger] = getLogger(
            f'{self.__class__.__module__}.{self.__class__.__name__}')
        self._logger.setLevel(INFO)

    def log(self, log_msg: str, level: int = INFO, datetime_obj: Optional[datetime] = None):
        if self._logger is not None:
            create_time = time.mktime(datetime_obj.timetuple()) if datetime_obj else time.time()
            _former_log_record_factory = logging.getLogRecordFactory()
            if _former_log_record_factory.__name__ != '_log_record_editor':

                def _log_record_editor(*args, **kwargs):
                    record = _former_log_record_factory(*args, **kwargs)
                    record.created = create_time
                    record.engine = f"[{record.name.split('.')[0].upper()}]"
                    if len(record.engine) < 9:
                        record.engine += ' '
                    return record

                logging.setLogRecordFactory(_log_record_editor)

            self._logger.log(level, log_msg)

    @property
    def logger(self):
        return self._logger
