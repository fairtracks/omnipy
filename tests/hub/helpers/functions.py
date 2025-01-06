from datetime import datetime
from io import TextIOBase
import os

from omnipy.shared.protocols.public.hub import IsRuntime
from omnipy.util.helpers import get_datetime_format


def read_log_lines_from_stream(stream: TextIOBase, clear_stream: bool = True) -> list[str]:
    stream.seek(0)
    log_lines = [line.rstrip(os.linesep) for line in stream.readlines()]
    stream.seek(0)
    if clear_stream:
        stream.truncate(0)
    return log_lines


def read_log_line_from_stream(stream: TextIOBase, clear_stream: bool = True) -> str:
    log_lines = read_log_lines_from_stream(stream, clear_stream)
    if len(log_lines) == 1:
        return log_lines[0]
    else:
        assert len(log_lines) == 0
        return ''


def assert_log_line_from_stream(
    stream,
    msg: str | None = None,
    level: str | None = None,
    logger: str | None = None,
    engine: str | None = None,
    datetime_str: str | None = None,
    clear_stream: bool = True,
):
    log_line = read_log_line_from_stream(stream, clear_stream)
    assert msg in log_line if msg else True
    assert level in log_line if level else True
    assert logger in log_line if logger else True
    assert engine in log_line if engine else True
    assert datetime_str in log_line if datetime_str else True


def format_datetime_obj(datetime_obj: datetime, runtime: IsRuntime):
    return datetime_obj.strftime(get_datetime_format(runtime.config.root_log.locale))
