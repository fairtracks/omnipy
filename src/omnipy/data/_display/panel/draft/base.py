from typing import Any, cast, Generic

from typing_extensions import override

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints, ConstraintsSatisfaction
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.layout.base import DimensionsAwarePanelLayoutMixin, Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FullyRenderedPanel, Panel
from omnipy.data._display.panel.typedefs import ContentInvT, ContentT, FrameInvT, FrameT
from omnipy.util import _pydantic as pyd


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class DraftPanel(Panel[FrameT], Generic[ContentT, FrameT]):
    content: ContentT

    def __init__(
        self,
        content: ContentT,
        title: str = '',
        frame: FrameT | None = None,
        constraints: Constraints | None = None,
        config: OutputConfig | None = None,
    ):
        object.__setattr__(self, 'content', content)
        super().__init__(title=title, frame=frame, constraints=constraints, config=config)

    @classmethod
    def create_copy_with_other_content(
        cls,
        draft_panel: 'DraftPanel[object, FrameInvT]',
        other_content: ContentInvT,
    ) -> 'DraftPanel[ContentInvT, FrameInvT]':
        return DraftPanel(
            other_content,
            title=draft_panel.title,
            frame=draft_panel.frame,
            constraints=draft_panel.constraints,
            config=draft_panel.config,
        )

    @property
    def satisfies(self) -> ConstraintsSatisfaction:
        return ConstraintsSatisfaction(self.constraints)

    @override
    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT]':
        if isinstance(self.content, Layout):
            from omnipy.data._display.layout.flow.base import optimize_layout_to_fit_frame
            layout_panel = cast('DraftPanel[Layout[DraftPanel], FrameT]', self)
            return optimize_layout_to_fit_frame(layout_panel)
        else:
            from omnipy.data._display.text.pretty import pretty_repr_of_draft_output
            return pretty_repr_of_draft_output(self)


class DimensionsAwareDraftPanel(DimensionsAwarePanel[FrameT],
                                DraftPanel[ContentT, FrameT],
                                Generic[ContentT, FrameT]):
    ...


class FullyRenderedDraftPanel(FullyRenderedPanel[FrameT],
                              DimensionsAwareDraftPanel[ContentT, FrameT],
                              Generic[ContentT, FrameT]):
    @override
    def render_next_stage(self) -> 'FullyRenderedDraftPanel[ContentT, FrameT]':
        raise NotImplementedError('This panel is fully rendered.')


class DimensionsAwareDraftPanelLayout(
        Layout[DimensionsAwareDraftPanel[Any, AnyFrame]],
        DimensionsAwarePanelLayoutMixin,
):
    ...


class FullyRenderedDraftPanelLayout(
        Layout[FullyRenderedDraftPanel[AnyFrame]],
        DimensionsAwarePanelLayoutMixin,
):
    ...
