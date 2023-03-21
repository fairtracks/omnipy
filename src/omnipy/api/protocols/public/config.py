from __future__ import annotations

from typing import Protocol

from omnipy.api.protocols.private.config import IsJobConfigBase
from omnipy.api.protocols.private.engine import IsEngineConfig
from omnipy.api.types import LocaleType


class IsLocalRunnerConfig(IsEngineConfig, Protocol):
    """"""
    ...


class IsPrefectEngineConfig(IsEngineConfig, Protocol):
    """"""
    use_cached_results: int = False


class IsJobConfig(IsJobConfigBase, Protocol):
    """"""
    ...


class IsRootLogConfig(Protocol):
    """"""
    log_format_str: str
    locale: LocaleType
    log_to_stdout: bool
    log_to_stderr: bool
    log_to_file: bool
    stdout_log_min_level: int
    stderr_log_min_level: int
    file_log_min_level: int
    file_log_dir_path: str
