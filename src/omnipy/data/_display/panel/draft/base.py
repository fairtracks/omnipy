from abc import ABC
from typing import Any, cast, Generic, overload

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

    @overload
    def create_modified_copy(
        self,
        content: ContentInvT,
        frame: FrameInvT,
        *args,
        **kwargs,
    ) -> 'DraftPanel[ContentInvT, FrameInvT]':
        ...

    @overload
    def create_modified_copy(
        self,
        content: ContentInvT,
        frame: None = None,
        *args,
        **kwargs,
    ) -> 'DraftPanel[ContentInvT, FrameT]':
        ...

    def create_modified_copy(
        self,
        content: ContentInvT,
        frame: FrameInvT | None = None,
        title: str | None = None,
        constraints: Constraints | None = None,
        config: OutputConfig | None = None,
    ) -> 'DraftPanel[ContentInvT, FrameT | FrameInvT]':
        return DraftPanel(
            content,
            title=title or self.title,
            frame=frame or self.frame,
            constraints=constraints or self.constraints,
            config=config or self.config,
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
                                Generic[ContentT, FrameT],
                                ABC):
    ...


class FullyRenderedDraftPanel(FullyRenderedPanel[FrameT],
                              DimensionsAwareDraftPanel[ContentT, FrameT],
                              Generic[ContentT, FrameT],
                              ABC):
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
