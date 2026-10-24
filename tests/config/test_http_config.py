"""Test the configuration of HTTP requests."""

from typing import Any

import pytest

from omnipy.config.data import HttpConfig, HttpRequestsConfig


def test_http_requests_config_rate_limiting_defaults() -> None:
    config = HttpRequestsConfig()
    assert config.requests_per_time_period == 60
    assert type(config.requests_per_time_period) is int
    assert config.time_period_in_secs == 60
    assert config.burst_ratio == 0.5


@pytest.mark.parametrize('value', [10, 10.0, '10'])
def test_http_requests_config_accepts_whole_numbers_of_requests(value: Any) -> None:
    config = HttpRequestsConfig(requests_per_time_period=value)
    assert config.requests_per_time_period == 10
    assert type(config.requests_per_time_period) is int

    config = HttpRequestsConfig()
    config.requests_per_time_period = value
    assert config.requests_per_time_period == 10


@pytest.mark.parametrize(
    'field, value',
    [
        ('requests_per_time_period', 0),
        ('requests_per_time_period', -1),
        # Not truncated to 2
        ('requests_per_time_period', 2.5),
        ('requests_per_time_period', '2.5'),
        ('time_period_in_secs', 0),
        ('time_period_in_secs', -1),
        ('burst_ratio', 0),
        ('burst_ratio', 1),
        ('burst_ratio', 1.5),
        ('burst_ratio', -0.1),
    ],
)
def test_http_requests_config_rejects_invalid_rate_limiting_values(
    field: str, value: object
) -> None:
    with pytest.raises(ValueError):
        kwargs: dict[str, Any] = {field: value}
        HttpRequestsConfig(**kwargs)

    config = HttpRequestsConfig()
    with pytest.raises(ValueError):
        setattr(config, field, value)


def test_http_config_for_host_copies_burst_ratio_from_defaults() -> None:
    config = HttpConfig()
    config.defaults.burst_ratio = 0.3
    assert config.for_host['example.org'].burst_ratio == 0.3

    config.for_host['example.org'].burst_ratio = 0.7
    assert config.defaults.burst_ratio == 0.3
