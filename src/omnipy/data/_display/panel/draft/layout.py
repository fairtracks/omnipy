from collections import defaultdict
from functools import cache, cached_property
from typing import Any, cast, Generic

from typing_extensions import override

from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsWithWidthAndHeight,
                                             has_height,
                                             has_width)
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ResizedLayoutDraftPanel(
        MonospacedDraftPanel[Layout[DimensionsAwarePanel], FrameT],
        Generic[FrameT],
):
    @pyd.validator('content', pre=True)
    def resize_panels_to_fit_frame(  # noqa: C901
        cls,
        content: Layout[DraftPanel],
        values: dict[str, Any],
    ) -> Layout[DimensionsAwarePanel]:
        dim_aware_panels: dict[
            str, DimensionsAwarePanel[AnyFrame]] = content.render_until_dimensions_aware()
        dim_aware_layout: Layout[DimensionsAwarePanel]
        prev_layout_dims: DimensionsWithWidthAndHeight | None = None

        while True:
            dim_aware_layout = Layout(**dim_aware_panels)
            layout_dims = cls._calc_table_layout_dims(dim_aware_layout)
            if prev_layout_dims is not None and layout_dims == prev_layout_dims:
                break
            prev_layout_dims = layout_dims

            frame_dims = cast(Frame, values['frame']).dims
            delta_width = max(layout_dims.width - frame_dims.width, 0) \
                if has_width(frame_dims) else None
            delta_height = max(layout_dims.height - frame_dims.height, 0) \
                if has_height(frame_dims) else None

            if not (delta_width or delta_height):
                break

            height_sorted_panel_keys: defaultdict[int, list[str]] = defaultdict(list)
            for key, dim_aware_panel in reversed(dim_aware_panels.items()):
                height_sorted_panel_keys[dim_aware_panel.dims.height].append(key)

            height_sorted_panel_keys = defaultdict(list, sorted(height_sorted_panel_keys.items()))
            for height, keys_of_height in height_sorted_panel_keys.items():
                for key in keys_of_height:
                    frame_width = dim_aware_panels[key].frame.dims.width
                    frame_height = dim_aware_panels[key].frame.dims.height

                    if delta_width:
                        frame_width = cls._panel_dims_if_cropped(dim_aware_panels[key]).width
                        frame_width_delta = -1
                        if frame_width >= -frame_width_delta:
                            frame_width += frame_width_delta

                    if delta_height:
                        frame_height = cls._panel_dims_if_cropped(dim_aware_panels[key]).height
                        frame_height_delta = -delta_height
                        if frame_height >= -frame_height_delta:
                            frame_height += frame_height_delta

                    new_panel_frame = Frame(
                        dims=Dimensions(width=frame_width, height=frame_height),)
                    draft_panel = content[key]
                    if new_panel_frame != draft_panel.frame:
                        new_draft_panel = draft_panel.__class__(
                            content=draft_panel.content,
                            frame=new_panel_frame,
                            constraints=draft_panel.constraints,
                            config=draft_panel.config,
                        )
                        dim_aware_panels[key] = new_draft_panel.render_next_stage()
                    break
                break

        dim_aware_layout |= dim_aware_panels
        return dim_aware_layout

    @staticmethod
    @cache
    def _panel_dims_if_cropped(
            panel: DimensionsAwarePanel[AnyFrame]) -> DimensionsWithWidthAndHeight:

        if has_width(panel.frame.dims):
            cropped_width = min(panel.frame.dims.width, panel.dims.width)
        else:
            cropped_width = panel.dims.width

        if has_height(panel.frame.dims):
            cropped_height = min(panel.frame.dims.height, panel.dims.height)
        else:
            cropped_height = panel.dims.height

        return Dimensions(width=cropped_width, height=cropped_height)

    @classmethod
    def _calc_table_layout_dims(
            cls, layout: Layout[DimensionsAwarePanel]) -> DimensionsWithWidthAndHeight:
        if len(layout) > 0:
            return Dimensions(
                width=(sum(cls._panel_dims_if_cropped(panel).width for panel in layout.values())
                       + len(layout) * 3 + 1),
                height=max(cls._panel_dims_if_cropped(panel).height for panel in layout.values())
                + 2,
            )
        else:
            return Dimensions(width=0, height=1)

    @cached_property
    @override
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return self._calc_table_layout_dims(self.content)

    @cached_property
    def _content_lines(self) -> list[str]:
        raise ShouldNotOccurException()

    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT]':
        from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
        return StylizedLayoutPanel(self)
