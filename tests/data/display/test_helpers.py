from typing import Annotated

import pytest

from omnipy.data._display.helpers import UnicodeCharWidthMap


def test_unicode_char_width_map(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]) -> None:
    map = UnicodeCharWidthMap()
    assert map['\0'] == 0
    assert map['\x1f'] == 0
    assert map[' '] == 1
    assert map['A'] == 1
    assert map['a'] == 1
    assert map['1'] == 1
    assert map['~'] == 1
    assert map['\x7f'] == 0
    assert map['\x80'] == 0
    assert map['\x9f'] == 0
    assert map['\xa0'] == 1
    assert map['中'] == 2
