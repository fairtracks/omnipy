from collections import defaultdict
from copy import copy
from dataclasses import dataclass, field
import shutil

from omnipy.api.enums import BackoffStrategy
from omnipy.api.protocols.public.config import IsHttpConfig

_terminal_size = shutil.get_terminal_size()


@dataclass
class HttpConfig:
    # For RateLimitingClientSession helper class
    requests_per_time_period: float = 60
    time_period_in_secs: float = 60

    # For get_*_from_api_endpoint tasks
    retry_http_statuses: tuple[int, ...] = (408, 425, 429, 500, 502, 503, 504)
    retry_attempts: int = 5
    retry_backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL


@dataclass
class DataConfig:
    interactive_mode: bool = True
    dynamically_convert_elements_to_models: bool = False
    terminal_size_columns: int = _terminal_size.columns
    terminal_size_lines: int = _terminal_size.lines
    http_defaults: IsHttpConfig = field(default_factory=HttpConfig)
    http_config_for_host: defaultdict[str, IsHttpConfig] = field(
        default_factory=lambda: defaultdict(HttpConfig))

    def __post_init__(self):
        self.http_config_for_host = defaultdict(lambda: copy(self.http_defaults))
