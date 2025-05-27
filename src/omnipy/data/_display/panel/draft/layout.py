from functools import cache, cached_property
from typing import Generic

from typing_extensions import override

from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight, has_height
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.layout import Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ResizedLayoutDraftPanel(
        MonospacedDraftPanel[Layout[DimensionsAwareDraftPanel[AnyFrame]], FrameT],
        Generic[FrameT],
):
    @staticmethod
    def create_from_draft_panel(
        draft_panel: DraftPanel[Layout, FrameT],
        new_layout: Layout,
    ) -> 'ResizedLayoutDraftPanel[FrameT]':
        resized_panel: ResizedLayoutDraftPanel[FrameT] = ResizedLayoutDraftPanel(
            Layout(**new_layout),
            title=draft_panel.title,
            frame=draft_panel.frame,
            constraints=draft_panel.constraints,
            config=draft_panel.config,
        )
        return resized_panel

    @pyd.validator('content', pre=True)
    def render_content_until_dimensions_aware(  # noqa: C901
        cls,
        content: Layout[DraftPanel],
    ) -> Layout[DimensionsAwareDraftPanel[AnyFrame]]:
        return Layout(**content.render_until_dimensions_aware())

    @staticmethod
    @cache
    def total_subpanel_dims_if_cropped(
        layout: Layout[DimensionsAwareDraftPanel[AnyFrame]],
        exclude_title: bool,
    ) -> DimensionsWithWidthAndHeight:
        def _panel_dims_if_cropped(
                panel: DimensionsAwarePanel[AnyFrame]) -> DimensionsWithWidthAndHeight:
            if exclude_title:
                return panel.dims_if_cropped
            else:
                if panel.title_height > 0:
                    panel_dims_width = max(panel.dims_if_cropped.width, panel.title_width)
                else:
                    panel_dims_width = panel.dims_if_cropped.width

                panel_dims_height = (
                    panel.dims_if_cropped.height + panel.title_height_with_blank_lines)
                if has_height(panel.frame.dims):
                    panel_dims_height = min(panel.frame.dims.height, panel_dims_height)

                return Dimensions(width=panel_dims_width, height=panel_dims_height)

        all_panel_dims = [_panel_dims_if_cropped(panel) for panel in layout.values()]
        return Dimensions(
            width=sum(panel_dims.width for panel_dims in all_panel_dims),
            height=max((panel_dims.height for panel_dims in all_panel_dims), default=0))

    @classmethod
    def calc_table_layout_dims(
        cls,
        layout: Layout[DimensionsAwareDraftPanel[AnyFrame]],
        exclude_title: bool,
    ) -> DimensionsWithWidthAndHeight:

        if len(layout) > 0:
            total_subpanel_dims = cls.total_subpanel_dims_if_cropped(
                layout,
                exclude_title=exclude_title,
            )
            return Dimensions(
                width=total_subpanel_dims.width + len(layout) * 3 + 1,
                height=total_subpanel_dims.height + 2,
            )
        else:
            return Dimensions(width=0, height=1)

    @cached_property
    @override
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return self.calc_table_layout_dims(self.content, exclude_title=False)

    @cached_property
    def dims_without_title(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return self.calc_table_layout_dims(self.content, exclude_title=True)

    @cached_property
    def _content_lines(self) -> list[str]:
        raise ShouldNotOccurException()

    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT]':
        from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
        return StylizedLayoutPanel(self)
