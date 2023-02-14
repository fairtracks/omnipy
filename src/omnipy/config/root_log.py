from dataclasses import dataclass, field
import locale as pkg_locale
import logging
from pathlib import Path

from omnipy.api.types import LocaleType


def _get_log_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('logs')))


@dataclass
class RootLogConfig:
    log_format_str: str = '{engine} {asctime} - {levelname}: {message} [{name}]'
    locale: LocaleType = pkg_locale.getlocale()
    log_to_stdout: bool = True
    log_to_stderr: bool = True
    log_to_file: bool = True
    stdout_log_min_level: int = logging.INFO
    stderr_log_min_level: int = logging.ERROR
    file_log_min_level: int = logging.WARNING
    file_log_dir_path: str = field(default_factory=_get_log_dir_path)
