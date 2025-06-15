from dataclasses import asdict
from typing import Any, cast, Generic

from typing_extensions import override, TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints, ConstraintsSatisfaction
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.layout.base import DimensionsAwarePanelLayoutMixin, Layout
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT, FullyRenderedPanel, Panel
from omnipy.util import _pydantic as pyd

ContentT = TypeVar('ContentT', bound=object, default=object, covariant=True)


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class DraftPanel(Panel[FrameT], Generic[ContentT, FrameT]):
    content: ContentT
    constraints: Constraints = pyd.Field(default_factory=Constraints)
    config: OutputConfig = pyd.Field(default_factory=OutputConfig)

    def __init__(
        self,
        content: ContentT,
        title: str = '',
        frame: FrameT | None = None,
        constraints: Constraints | None = None,
        config: OutputConfig | None = None,
    ):
        object.__setattr__(self, 'content', content)
        object.__setattr__(self, 'constraints', constraints or Constraints())
        object.__setattr__(self, 'config', config or OutputConfig())
        super().__init__(title=title, frame=frame)

    @pyd.validator('constraints')
    def _copy_constraints(cls, constraints: Constraints) -> Constraints:
        return Constraints(**asdict(constraints))

    @pyd.validator('config')
    def _copy_config(cls, config: OutputConfig) -> OutputConfig:
        return OutputConfig(**asdict(config))

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
