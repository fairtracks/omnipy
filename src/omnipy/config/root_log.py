from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Optional

from omnipy.api.types import LocaleType


def _get_log_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('logs')))


@dataclass
class RootLogConfig:
    log_format_str: str = '%(levelname)s - %(message)s (%(name)s)'
    locale: Optional[LocaleType] = None
    log_to_stdout: bool = True
    log_to_stderr: bool = True
    log_to_file: bool = True
    stdout_log_min_level: int = logging.INFO
    stderr_log_min_level: int = logging.ERROR
    file_log_min_level: int = logging.WARNING
    file_log_dir_path: str = field(default_factory=_get_log_dir_path)
