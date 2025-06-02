from functools import cached_property
from typing import cast, Generic

from typing_extensions import override

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.layout.base import DimensionsAwarePanelLayoutMixin, Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.shared.exceptions import ShouldNotOccurException
import omnipy.util._pydantic as pyd


class DimensionsAwareDraftPanelLayout(
        Layout[DimensionsAwareDraftPanel[AnyFrame]],
        DimensionsAwarePanelLayoutMixin,
):
    ...


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ResizedLayoutDraftPanel(
        MonospacedDraftPanel[DimensionsAwareDraftPanelLayout, FrameT],
        Generic[FrameT],
):
    """
    A draft panel containing a layout that has been resized to fit its
    frame.

    This class represents the result of the layout optimization process,
    where all contained panels have been adjusted to fit within frame
    constraints.

    The layout has undergone width distribution, height adjustment, and various
    optimization steps to ensure panels display their content effectively.
    """
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
