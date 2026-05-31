"""Draft panel classes for pre-render display content and nested layouts."""

from abc import ABC
from typing import Any, cast, Generic, overload

from typing_extensions import override

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints, ConstraintsSatisfaction
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.layout.base import DimensionsAwarePanelLayoutMixin, Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FullyRenderedPanel, Panel
from omnipy.data._display.panel.typedefs import ContentInvT, ContentT, FrameInvT, FrameT
import omnipy.util.pydantic as pyd


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class DraftPanel(Panel[FrameT], Generic[ContentT, FrameT]):
    """Draft-stage panel holding content before rendering/styling.

    Draft panels are immutable containers for raw content plus frame,
    constraint, and output configuration metadata used by later render stages.
    """

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
        """Create a copy with selected fields replaced.

        Args:
            content: Replacement content value.
            frame: Optional replacement frame.
            title: Optional replacement title.
            constraints: Optional replacement constraints.
            config: Optional replacement output config.

        Returns:
            New draft panel instance with requested modifications.
        """
        return DraftPanel(
            content,
            title=title or self.title,
            frame=frame or self.frame,
            constraints=constraints or self.constraints,
            config=config or self.config,
        )

    @property
    def satisfies(self) -> ConstraintsSatisfaction:
        """Return constraint satisfaction helper for current draft settings.

        Returns:
            ``ConstraintsSatisfaction`` initialized from panel constraints.
        """
        return ConstraintsSatisfaction(self.constraints)

    @override
    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT]':
        """Render draft content to the next stage.

        Layout content is optimized to fit frame constraints, while non-layout
        content is routed through text pretty-printing.

        Returns:
            Dimensions-aware panel ready for subsequent rendering.
        """
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
    """Draft panel whose content has been measured for layout decisions.

    This marker type combines draft content with dimensions-aware behavior.
    """

    ...


class FullyRenderedDraftPanel(FullyRenderedPanel[FrameT],
                              DimensionsAwareDraftPanel[ContentT, FrameT],
                              Generic[ContentT, FrameT],
                              ABC):
    """Draft panel that has completed rendering and can export output variants."""

    @override
    def render_next_stage(self) -> 'FullyRenderedDraftPanel[ContentT, FrameT]':
        """Raise because fully rendered draft panels have no further stage.

        Returns:
            This method does not return; it always raises.

        Raises:
            NotImplementedError: Always, because this panel is already terminal.
        """
        raise NotImplementedError('This panel is fully rendered.')


class DimensionsAwareDraftPanelLayout(
        Layout[DimensionsAwareDraftPanel[Any, AnyFrame]],
        DimensionsAwarePanelLayoutMixin,
):
    """Layout of dimensions-aware draft panels.

    The layout can aggregate panel dimensions and compute composed table bounds.
    """

    ...


class FullyRenderedDraftPanelLayout(
        Layout[FullyRenderedDraftPanel[AnyFrame]],
        DimensionsAwarePanelLayoutMixin,
):
    """Layout of fully rendered draft panels ready for styling composition.

    This layout is typically consumed by layout stylers that combine multiple
    rendered panel outputs into a single table view.
    """

    ...
