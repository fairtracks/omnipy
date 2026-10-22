"""Tests for range lookups."""

import pytest

from omnipy.util.range_lookup import RangeLookup


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
def test_range_lookup() -> None:
    range_lookup = RangeLookup((range(0, 5), range(10, 15)))
    assert 0 in range_lookup
    assert 4 in range_lookup
    assert 5 not in range_lookup
    assert 9 not in range_lookup
    assert 10 in range_lookup
    assert 14 in range_lookup
    assert 15 not in range_lookup


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
def test_empty_range_lookup() -> None:
    empty_range_lookup = RangeLookup(())
    assert 0 not in empty_range_lookup
    assert 1 not in empty_range_lookup


@pytest.mark.usefixtures('skip_test_if_not_default_data_config_values')
def test_fail_range_lookup_negative_numbers() -> None:
    with pytest.raises(ValueError):
        RangeLookup((range(-1, 1),))

    with pytest.raises(ValueError):
        RangeLookup((range(1, -1, -1),))

    range_lookup = RangeLookup((range(0, 5),))

    with pytest.raises(ValueError):
        -1 in range_lookup
