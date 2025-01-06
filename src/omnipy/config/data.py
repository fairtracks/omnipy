from collections import defaultdict
import shutil
from typing import Any

from omnipy.config import ConfigBase
from omnipy.shared.enums import BackoffStrategy
from omnipy.shared.protocols.config import IsHttpConfig
import omnipy.util._pydantic as pyd

_terminal_size = shutil.get_terminal_size()


class HttpConfig(ConfigBase):
    # For RateLimitingClientSession helper class
    requests_per_time_period: float = 60
    time_period_in_secs: float = 60

    # For get_*_from_api_endpoint tasks
    retry_http_statuses: tuple[int, ...] = (408, 425, 429, 500, 502, 503, 504)
    retry_attempts: int = 5
    retry_backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL


class DataConfig(ConfigBase):
    interactive_mode: bool = True
    dynamically_convert_elements_to_models: bool = False
    terminal_size_columns: int = _terminal_size.columns
    terminal_size_lines: int = _terminal_size.lines
    http_defaults: IsHttpConfig = pyd.Field(default_factory=HttpConfig)
    http_config_for_host: defaultdict[str, IsHttpConfig] = pyd.Field(
        default_factory=lambda: defaultdict(HttpConfig))

    @pyd.validator('http_config_for_host', always=True)
    def update_http_defaults(cls,
                             _http_config_for_host: defaultdict[str, HttpConfig],
                             values: dict[str, Any]) -> defaultdict[str, HttpConfig]:
        return defaultdict(lambda: values['http_defaults'].copy())
