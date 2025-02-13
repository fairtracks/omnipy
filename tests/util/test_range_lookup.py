from typing import Annotated

import pytest

from omnipy.util.range_lookup import RangeLookup


def test_range_lookup(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:

    range_lookup = RangeLookup((range(0, 5), range(10, 15)))
    assert 0 in range_lookup
    assert 4 in range_lookup
    assert 5 not in range_lookup
    assert 9 not in range_lookup
    assert 10 in range_lookup
    assert 14 in range_lookup
    assert 15 not in range_lookup


def test_empty_range_lookup(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    empty_range_lookup = RangeLookup(())
    assert 0 not in empty_range_lookup
    assert 1 not in empty_range_lookup


def test_fail_range_lookup_negative_numbers(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    with pytest.raises(ValueError):
        RangeLookup((range(-1, 1),))

    with pytest.raises(ValueError):
        RangeLookup((range(1, -1, -1),))

    range_lookup = RangeLookup((range(0, 5),))

    with pytest.raises(ValueError):
        -1 in range_lookup
