from typing import Annotated

import pytest

from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.panel.base import Panel


class SimplePanel(Panel):
    def render_next_stage(self) -> 'SimplePanel':
        return self


def test_panel(skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture],):
    # Test with default frame
    panel = SimplePanel()
    assert panel.title == ''
    assert panel.frame == empty_frame()

    # Test with custom frame with title and fixed dimensions (by default)
    custom_frame_fixed = Frame(Dimensions(width=10, height=20))
    panel = SimplePanel(title='My panel', frame=custom_frame_fixed)
    assert panel.title == 'My panel'
    assert panel.frame is not custom_frame_fixed  # Should be a copy, not the same object
    assert panel.frame == custom_frame_fixed  # But should be equal in value

    # Test with custom frame without fixed dimensions
    custom_frame_not_fixed = Frame(
        Dimensions(width=10, height=20), fixed_width=False, fixed_height=False)
    panel = SimplePanel(title='My other panel', frame=custom_frame_not_fixed)
    assert panel.title == 'My other panel'
    assert panel.frame is not custom_frame_not_fixed  # Should be a copy, not the same object
    assert panel.frame == custom_frame_not_fixed  # But should be equal in value


def test_panel_hashable(skip_test_if_not_default_data_config_values: Annotated[None,
                                                                               pytest.fixture],):
    panel_1 = SimplePanel()
    panel_2 = SimplePanel()

    assert hash(panel_1) == hash(panel_2)

    panel_3 = SimplePanel(frame=Frame(Dimensions(width=None, height=20)))
    panel_4 = SimplePanel(frame=Frame(Dimensions(width=10, height=None)))
    panel_5 = SimplePanel(frame=Frame(Dimensions(width=10, height=20)))

    assert hash(panel_1) != hash(panel_3) != hash(panel_4) != hash(panel_5)

    panel_6 = SimplePanel(frame=Frame(Dimensions(width=10, height=20)))

    assert hash(panel_5) == hash(panel_6)

    panel_7 = SimplePanel(frame=Frame(Dimensions(10, 20), fixed_width=True, fixed_height=True))
    panel_8 = SimplePanel(frame=Frame(Dimensions(10, 20), fixed_width=True, fixed_height=False))
    panel_9 = SimplePanel(frame=Frame(Dimensions(10, 20), fixed_width=False, fixed_height=True))
    panel_10 = SimplePanel(frame=Frame(Dimensions(10, 20), fixed_width=False, fixed_height=False))

    assert hash(panel_6) == hash(panel_7) != hash(panel_8) != hash(panel_9) != hash(panel_10)

    panel_11 = SimplePanel(title='My panel')
    panel_12 = SimplePanel(title='My other panel')

    assert hash(panel_2) != hash(panel_11) != hash(panel_12)


# noinspection PyDataclass
def test_fail_panel_no_assignments(
        skip_test_if_not_default_data_config_values: Annotated[None, pytest.fixture]):

    panel = SimplePanel()

    with pytest.raises(AttributeError):
        panel.title = 'My panel'  # type: ignore[misc]

    new_frame = Frame(Dimensions(width=30, height=40))
    with pytest.raises(AttributeError):
        panel.frame = new_frame  # type: ignore[misc]
