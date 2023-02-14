from datetime import datetime
from io import StringIO
import os
from typing import List, Optional

from omnipy.util.helpers import get_datetime_format


def read_log_lines_from_stream(str_stream: StringIO) -> List[str]:
    str_stream.seek(0)
    log_lines = [line.rstrip(os.linesep) for line in str_stream.readlines()]
    str_stream.seek(0)
    str_stream.truncate(0)
    return log_lines


def read_log_line_from_stream(str_stream: StringIO) -> str:
    log_lines = read_log_lines_from_stream(str_stream)
    if len(log_lines) == 1:
        return log_lines[0]
    else:
        assert len(log_lines) == 0
        return ''


def assert_log_lines_from_stream(num_log_lines, str_stream):
    log_lines = read_log_lines_from_stream(str_stream)
    assert len(log_lines) == num_log_lines
    for log_line in log_lines:
        assert 'INFO' in log_line
        assert '[test_logger]' in log_line
    return log_lines


def assert_log_line_from_stream(str_stream,
                                msg: str,
                                level: Optional[str] = None,
                                logger: Optional[str] = None):
    log_line = read_log_line_from_stream(str_stream)
    assert msg in log_line
    assert level in log_line if level else level not in log_line
    assert logger in log_line if logger else logger not in log_line
