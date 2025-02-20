from dataclasses import asdict
from functools import cached_property
import re
from typing import ClassVar, Generic

from typing_extensions import TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints, ConstraintsSatisfaction
from omnipy.data._display.dimensions import Dimensions, DimensionsFit
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.helpers import UnicodeCharWidthMap
from omnipy.util._pydantic import ConfigDict, dataclass, Extra, Field, NonNegativeInt, validator

ContentT = TypeVar('ContentT', bound=object, default=object, covariant=True)
FrameT = TypeVar('FrameT', bound=AnyFrame, default=AnyFrame, covariant=True)


@dataclass(config=ConfigDict(extra=Extra.forbid, validate_assignment=True))
class DraftOutput(Generic[ContentT, FrameT]):
    content: ContentT
    frame: FrameT = Field(default_factory=Frame)
    constraints: Constraints = Field(default_factory=Constraints)
    config: OutputConfig = Field(default_factory=OutputConfig)

    @validator('frame')
    def _copy_frame(cls, frame: Frame) -> Frame:
        return Frame(dims=frame.dims)

    @validator('constraints')
    def _copy_constraints(cls, constraints: Constraints) -> Constraints:
        return Constraints(**asdict(constraints))

    @validator('config')
    def _copy_config(cls, config: OutputConfig) -> OutputConfig:
        return OutputConfig(**asdict(config))

    @property
    def satisfies(self) -> ConstraintsSatisfaction:
        return ConstraintsSatisfaction(self.constraints)


@dataclass(init=False, config=ConfigDict(extra=Extra.forbid, validate_all=True))
class DraftMonospacedOutput(DraftOutput[str, FrameT], Generic[FrameT]):
    _char_width_map: ClassVar[UnicodeCharWidthMap] = UnicodeCharWidthMap()
    content: str

    def __init__(self, content: str, frame=None, constraints=None, config=None):
        object.__setattr__(self, 'content', content)
        object.__setattr__(self, 'frame', frame or Frame())
        object.__setattr__(self, 'constraints', constraints or Constraints())
        object.__setattr__(self, 'config', config or OutputConfig())

    def __setattr__(self, key, value):
        if key in ['content', 'frame', 'constraints', 'config']:
            raise AttributeError(f'Field "{key}" is immutable')
        return super().__setattr__(key, value)

    @cached_property
    def _content_lines(self) -> list[str]:
        return self.content.splitlines()

    @cached_property
    def _width(self) -> NonNegativeInt:
        def _line_len(line: str) -> int:
            return sum(self._char_width_map[c] for c in line)

        return max((_line_len(line) for line in self._content_lines), default=0)

    @cached_property
    def _height(self) -> NonNegativeInt:
        return len(self.content.splitlines())

    @cached_property
    def dims(self) -> Dimensions[NonNegativeInt, NonNegativeInt]:
        return Dimensions(width=self._width, height=self._height)

    @cached_property
    def within_frame(self) -> DimensionsFit:
        return DimensionsFit(self.dims, self.frame.dims)

    @cached_property
    def max_container_width_across_lines(self) -> NonNegativeInt:
        def _max_container_width_in_line(line):
            # Find all containers in the line using regex
            containers = re.findall(r'\{.*\}|\[.*\]|\(.*\)', line)
            # Return the length of the longest container, or 0 if none are found
            return max((len(container) for container in containers), default=0)

        # Calculate the maximum container width across all lines
        return max((_max_container_width_in_line(line) for line in self._content_lines), default=0)

    @cached_property
    def satisfies(self) -> ConstraintsSatisfaction:  # pyright: ignore
        return ConstraintsSatisfaction(
            self.constraints,
            max_container_width_across_lines=self.max_container_width_across_lines,
        )
