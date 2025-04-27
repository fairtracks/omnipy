import dataclasses

from omnipy.data._display.dimensions import Dimensions, has_height, has_width
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import FrameT, panel_is_dimensions_aware
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel


def flow_layout_subpanels_inside_frame(
        layout_panel: DraftPanel[Layout, FrameT]) -> ResizedLayoutDraftPanel[FrameT]:

    if layout_panel.frame is None or (layout_panel.frame.dims.width is None
                                      and layout_panel.frame.dims.height is None):
        new_layout = layout_panel.content
    else:
        frame_dims = layout_panel.frame.dims

        width_unset_panels = {}
        if has_width(frame_dims):
            preset_width = 0
            for key, panel in layout_panel.content.items():
                if panel.frame is not None and panel.frame.dims.width is not None:
                    preset_width += panel.frame.dims.width + 3
                elif panel_is_dimensions_aware(panel) and panel.dims.width is not None:
                    preset_width += panel.dims.width + 3
                else:
                    width_unset_panels[key] = panel

            num_unset_panels = len(width_unset_panels)
            per_panel_width = ((frame_dims.width - preset_width - 1) // num_unset_panels) - 3
            per_panel_width = max(per_panel_width, 0)
        else:
            per_panel_width = None

        if has_height(frame_dims):
            per_panel_height = frame_dims.height - 2
            per_panel_height = max(per_panel_height, 0)
        else:
            per_panel_height = None

        print(f'per_panel_width: {per_panel_width}')
        print(f'per_panel_height: {per_panel_height}')

        new_layout = Layout()
        for key, panel in layout_panel.content.items():
            if key in width_unset_panels:
                new_layout[key] = dataclasses.replace(
                    panel,
                    frame=Frame(
                        Dimensions(width=per_panel_width, height=per_panel_height),
                        fixed_width=False,
                        fixed_height=False,
                    ),
                )
            else:
                new_layout[key] = panel

    return ResizedLayoutDraftPanel(
        Layout(**new_layout),
        frame=layout_panel.frame,
        constraints=layout_panel.constraints,
        config=layout_panel.config,
    )
