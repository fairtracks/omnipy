import dataclasses

from omnipy.data._display.dimensions import Dimensions, has_height, has_width
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import FrameT
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel


def flow_layout_subpanels_inside_frame(
        layout_panel: DraftPanel[Layout, FrameT]) -> ResizedLayoutDraftPanel[FrameT]:

    if layout_panel.frame is None or (layout_panel.frame.dims.width is None
                                      and layout_panel.frame.dims.height is None):
        new_layout = layout_panel.content
    else:
        frame_dims = layout_panel.frame.dims

        if has_width(frame_dims):
            num_panels = len(layout_panel.content)
            per_panel_width = ((frame_dims.width - 2) // num_panels) - 2
            per_panel_width = max(per_panel_width, 0)
        else:
            per_panel_width = None

        if has_height(frame_dims):
            per_panel_height = frame_dims.height - 2
            per_panel_height = max(per_panel_height, 0)
        else:
            per_panel_height = None

        new_layout = Layout()
        for key, panel in layout_panel.content.items():
            new_layout[key] = dataclasses.replace(
                panel,
                frame=Frame(Dimensions(width=per_panel_width, height=per_panel_height)),
            )

    dimensions_aware_panels = new_layout.render_until_dimensions_aware()
    return ResizedLayoutDraftPanel(
        Layout(**dimensions_aware_panels),
        frame=layout_panel.frame,
        constraints=layout_panel.constraints,
        config=layout_panel.config,
    )
