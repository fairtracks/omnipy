import dataclasses

from omnipy.data._display.dimensions import Dimensions, has_width
from omnipy.data._display.frame import Frame
from omnipy.data._display.layout import Layout, PanelT
from omnipy.data._display.panel.base import FrameT, panel_is_dimensions_aware
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.layout import ResizedLayoutDraftPanel


def flow_layout_subpanels_inside_frame(
        layout_panel: DraftPanel[Layout[PanelT], FrameT]) -> ResizedLayoutDraftPanel[FrameT]:

    if not has_width(layout_panel.frame.dims):
        new_layout = layout_panel.content
    else:
        frame_dims = layout_panel.frame.dims

        per_panel_width = None

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
            if num_unset_panels > 0:
                per_panel_width = ((frame_dims.width - preset_width - 1) // num_unset_panels) - 3
                per_panel_width = max(per_panel_width, 0)
            else:
                per_panel_width = 0

        # print(f'per_panel_width: {per_panel_width}')

        new_layout = Layout()
        for key, panel in layout_panel.content.items():
            if key in width_unset_panels:
                frame_width: int | None = per_panel_width
                frame_fixed_width: bool | None = False
            else:
                frame_width = panel.frame.dims.width
                frame_fixed_width = panel.frame.fixed_width

            new_layout[key] = dataclasses.replace(
                panel,
                frame=Frame(
                    Dimensions(
                        width=frame_width,
                        height=panel.frame.dims.height,
                    ),
                    fixed_width=frame_fixed_width,
                    fixed_height=panel.frame.fixed_height,
                ),
            )

    return ResizedLayoutDraftPanel(
        Layout(**new_layout),
        title=layout_panel.title,
        frame=layout_panel.frame,
        constraints=layout_panel.constraints,
        config=layout_panel.config,
    )
