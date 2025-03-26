from typing import Annotated

import pytest

from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.panel.draft import Panel


def test_panel(skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],):
    # Test with default frame
    panel = Panel()
    assert panel.frame == empty_frame()

    # Test with custom frame
    custom_frame = Frame(Dimensions(width=10, height=20))
    panel = Panel(frame=custom_frame)
    assert panel.frame is not custom_frame  # Should be a copy, not the same object
    assert panel.frame == custom_frame  # But should be equal in value


def test_panel_hashable(skip_test_if_not_default_data_config_values: Annotated[None,
                                                                               pytest.fixture],):
    panel_1 = Panel()
    panel_2 = Panel()

    assert hash(panel_1) == hash(panel_2)

    panel_3 = Panel(frame=Frame(Dimensions(width=None, height=20)))
    panel_4 = Panel(frame=Frame(Dimensions(width=10, height=None)))
    panel_5 = Panel(frame=Frame(Dimensions(width=10, height=20)))

    assert hash(panel_1) != hash(panel_3) != hash(panel_4) != hash(panel_5)

    panel_6 = Panel(frame=Frame(Dimensions(width=10, height=20)))

    assert hash(panel_5) == hash(panel_6)


# noinspection PyDataclass
def test_fail_panel_no_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]):

    panel = Panel()
    new_frame = Frame(Dimensions(width=30, height=40))

    with pytest.raises(AttributeError):
        panel.frame = new_frame  # type: ignore[misc]
