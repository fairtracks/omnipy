from dataclasses import asdict
from typing import Generic

from typing_extensions import TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints, ConstraintsSatisfaction
from omnipy.data._display.panel.base import FrameT, Panel
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

    def __init__(self, content: ContentT, frame=None, constraints=None, config=None):
        object.__setattr__(self, 'content', content)
        object.__setattr__(self, 'constraints', constraints or Constraints())
        object.__setattr__(self, 'config', config or OutputConfig())
        super().__init__(frame=frame)

    @pyd.validator('constraints')
    def _copy_constraints(cls, constraints: Constraints) -> Constraints:
        return Constraints(**asdict(constraints))

    @pyd.validator('config')
    def _copy_config(cls, config: OutputConfig) -> OutputConfig:
        return OutputConfig(**asdict(config))

    @property
    def satisfies(self) -> ConstraintsSatisfaction:
        return ConstraintsSatisfaction(self.constraints)
