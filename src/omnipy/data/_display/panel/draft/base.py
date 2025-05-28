from dataclasses import asdict
from typing import Any, cast, Generic

from typing_extensions import TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints, ConstraintsSatisfaction
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT, Panel
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

    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT]':
        from omnipy.data._display.panel.layout import Layout

        if isinstance(self.content, Layout):
            from omnipy.data._display.panel.flow import flow_layout_subpanels_inside_frame
            layout_panel = cast('DraftPanel[Layout, FrameT]', self)
            return flow_layout_subpanels_inside_frame(layout_panel)
        else:
            from omnipy.data._display.panel.pretty import pretty_repr_of_draft_output
            return pretty_repr_of_draft_output(self)


class DimensionsAwareDraftPanel(DimensionsAwarePanel[FrameT],
                                DraftPanel[Any, FrameT],
                                Generic[FrameT]):
    ...
