from dataclasses import dataclass, field
from pathlib import Path


def _get_log_dir_path() -> str:
    return str(Path.cwd().joinpath(Path('logs')))


@dataclass
class RunStateRegistryConfig:
    verbose: bool = True
    log_dir_path: str = field(default_factory=_get_log_dir_path)


# TODO: Add support for verbose in RunStateRegistry
