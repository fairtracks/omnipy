from dataclasses import dataclass
from functools import cached_property
from typing import cast, Generic

from typing_extensions import override

from omnipy.data._display.config import LayoutDesign, OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions, DimensionsWithWidthAndHeight
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.data._display.panel.layout import Layout
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd


@dataclass
class LayoutDesignDims:
    horizontal_chars_per_panel: int
    horizontal_end_chars: int
    vertical_chars_per_panel: int
    vertical_end_chars: int

    @staticmethod
    def _extra_chars(chars_per_panel: int, end_chars: int, num_panels: int) -> int:
        return num_panels * chars_per_panel + end_chars

    def extra_horizontal_chars(self, num_horizontal_panels: int) -> int:
        return self._extra_chars(
            self.horizontal_chars_per_panel,
            self.horizontal_end_chars,
            num_horizontal_panels,
        )

    def extra_vertical_chars(self, num_vertical_panels: int) -> int:
        return self._extra_chars(
            self.vertical_chars_per_panel,
            self.vertical_end_chars,
            num_vertical_panels,
        )


class DimensionsAwarePanelLayoutMixin:
    @classmethod
    def get_layout_design_dims(
        cls,
        layout_design: LayoutDesign = LayoutDesign.TABLE_GRID,
    ) -> LayoutDesignDims:
        if layout_design == LayoutDesign.TABLE_GRID:
            return LayoutDesignDims(
                horizontal_chars_per_panel=3,
                horizontal_end_chars=1,
                vertical_chars_per_panel=1,
                vertical_end_chars=1,
            )
        else:
            raise ValueError(f'Unsupported layout design: {layout_design}')

    def _total_dims_over_subpanels(self, dims_property: str) -> DimensionsWithWidthAndHeight:
        self_as_layout = cast(Layout, self)

        all_panel_dims = [getattr(panel, dims_property) for panel in self_as_layout.values()]
        return Dimensions(
            width=sum(panel_dims.width for panel_dims in all_panel_dims),
            height=max((panel_dims.height for panel_dims in all_panel_dims), default=0))

    @property
    def total_subpanel_cropped_dims(self) -> DimensionsWithWidthAndHeight:
        return self._total_dims_over_subpanels('cropped_dims')

    @property
    def total_subpanel_outer_dims(self) -> DimensionsWithWidthAndHeight:
        return self._total_dims_over_subpanels('outer_dims')

    def calc_dims(
        self,
        layout_design: LayoutDesign = LayoutDesign.TABLE_GRID,
        use_outer_dims_for_subpanels: bool = True,
    ) -> DimensionsWithWidthAndHeight:
        self_as_layout = cast(Layout, self)

        if len(self_as_layout) > 0:
            if use_outer_dims_for_subpanels:
                total_subpanel_dims = self.total_subpanel_outer_dims
            else:
                total_subpanel_dims = self.total_subpanel_cropped_dims

            layout_design_dims = self.get_layout_design_dims(layout_design)

            num_horizontal_panels = len(self_as_layout)
            num_vertical_panels = 1  # Assuming a single row layout for simplicity
            return Dimensions(
                width=(total_subpanel_dims.width
                       + layout_design_dims.extra_horizontal_chars(num_horizontal_panels)),
                height=(total_subpanel_dims.height
                        + layout_design_dims.extra_vertical_chars(num_vertical_panels)),
            )
        else:
            return Dimensions(width=0, height=1)


class DimensionsAwareDraftPanelLayout(
        Layout[DimensionsAwareDraftPanel[AnyFrame]],
        DimensionsAwarePanelLayoutMixin,
):
    """A layout that contains draft panels with dimensions awareness."""


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
