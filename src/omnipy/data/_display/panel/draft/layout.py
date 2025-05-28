from functools import cached_property
from typing import cast, Generic

from typing_extensions import override

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.data._display.panel.layout import Layout
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd


class DimensionsAwareDraftPanelLayout(Layout[DimensionsAwareDraftPanel[AnyFrame]]):
    def _total_dims_over_subpanels(self, dims_property: str) -> DimensionsWithWidthAndHeight:
        all_panel_dims = [getattr(panel, dims_property) for panel in self.values()]
        return Dimensions(
            width=sum(panel_dims.width for panel_dims in all_panel_dims),
            height=max((panel_dims.height for panel_dims in all_panel_dims), default=0))

    @property
    def total_subpanel_cropped_dims(self) -> DimensionsWithWidthAndHeight:
        return self._total_dims_over_subpanels('cropped_dims')

    def calc_dims(self, use_outer_dims_for_subpanels: bool = True) -> DimensionsWithWidthAndHeight:
        if len(self) > 0:
            dims_property = 'outer_dims' if use_outer_dims_for_subpanels else 'cropped_dims'
            total_subpanel_dims = self._total_dims_over_subpanels(dims_property)

            return Dimensions(
                width=total_subpanel_dims.width + len(self) * 3 + 1,
                height=total_subpanel_dims.height + 2,
            )
        else:
            return Dimensions(width=0, height=1)


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ResizedLayoutDraftPanel(
        MonospacedDraftPanel[DimensionsAwareDraftPanelLayout, FrameT],
        Generic[FrameT],
):
    def __init__(
        self,
        content: Layout,
        title: str = '',
        frame: FrameT | None = None,
        constraints: Constraints | None = None,
        config: OutputConfig | None = None,
    ):
        super().__init__(
            cast(DimensionsAwareDraftPanelLayout, content),
            title=title,
            frame=frame,
            constraints=constraints,
            config=config)

    @staticmethod
    def create_from_draft_panel(
        draft_panel: DraftPanel[Layout, FrameT],
        new_layout: Layout,
    ) -> 'ResizedLayoutDraftPanel[FrameT]':
        resized_panel: ResizedLayoutDraftPanel[FrameT] = ResizedLayoutDraftPanel(
            DimensionsAwareDraftPanelLayout(**new_layout),
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
    ) -> DimensionsAwareDraftPanelLayout:
        return DimensionsAwareDraftPanelLayout(**content.render_until_dimensions_aware())

    @cached_property
    @override
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return self.content.calc_dims()

    @cached_property
    def _content_lines(self) -> list[str]:
        raise ShouldNotOccurException()

    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT]':
        from omnipy.data._display.panel.styling.layout import StylizedLayoutPanel
        return StylizedLayoutPanel(self)
