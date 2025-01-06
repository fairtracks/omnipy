from io import TextIOBase
import locale as pkg_locale
import logging
from pathlib import Path
import sys

from omnipy.config import ConfigBase
from omnipy.shared.typedefs import LocaleType
import omnipy.util._pydantic as pyd


def _get_log_path() -> str:
    return str(Path.cwd() / 'logs' / 'omnipy.log')


class RootLogConfig(ConfigBase):
    log_format_str: str = '[{engine}] {asctime} - {levelname}: {message} ({name})'
    locale: LocaleType = pkg_locale.getlocale()
    log_to_stdout: bool = True
    log_to_stderr: bool = True
    log_to_file: bool = True
    stdout: TextIOBase = pyd.Field(default_factory=lambda: sys.stdout)
    stderr: TextIOBase = pyd.Field(default_factory=lambda: sys.stderr)
    stdout_log_min_level: int = logging.INFO
    stderr_log_min_level: int = logging.ERROR
    file_log_min_level: int = logging.WARNING
    file_log_path: str = pyd.Field(default_factory=_get_log_path)
