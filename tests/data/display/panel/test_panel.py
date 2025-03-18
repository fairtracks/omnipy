from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import Frame
from omnipy.data._display.panel.draft import Panel


def test_panel():
    # Test with default frame
    panel = Panel()
    assert panel.frame == Frame()

    # Test with custom frame
    custom_frame = Frame(Dimensions(width=10, height=20))
    panel = Panel(frame=custom_frame)
    assert panel.frame is not custom_frame  # Should be a copy, not the same object
    assert panel.frame == custom_frame  # But should be equal in value

    # Test frame validator works for assignment
    new_frame = Frame(Dimensions(width=30, height=40))
    panel.frame = new_frame
    assert panel.frame is not new_frame  # Should be a copy
    assert panel.frame == new_frame  # But equal in value
