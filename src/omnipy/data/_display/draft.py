from dataclasses import asdict
from typing import ClassVar, Generic

from typing_extensions import TypeVar

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import Dimensions, DimensionsFit
from omnipy.data._display.frame import AnyFrame, Frame
from omnipy.data._display.helpers import UnicodeCharWidthMap
from omnipy.util._pydantic import dataclass, Field, NonNegativeInt, validator

ContentT = TypeVar('ContentT', bound=object, default=object, covariant=True)
FrameT = TypeVar('FrameT', bound=AnyFrame, default=AnyFrame)


@dataclass
class DraftOutput(Generic[ContentT, FrameT]):
    content: ContentT
    frame: FrameT = Field(default_factory=Frame)
    config: OutputConfig = Field(default_factory=OutputConfig)

    @validator('frame', pre=True)
    def _copy_frame(cls, frame: Frame) -> Frame:
        return Frame(dims=frame.dims)

    @validator('config', pre=True)
    def _copy_config(cls, config: OutputConfig) -> OutputConfig:
        return OutputConfig(**asdict(config))


@dataclass
class DraftMonospacedOutput(DraftOutput[str, FrameT], Generic[FrameT]):
    _char_width_map: ClassVar[UnicodeCharWidthMap] = UnicodeCharWidthMap()
    content: str

    @property
    def _width(self) -> NonNegativeInt:
        def _line_len(line: str) -> int:
            return sum(self._char_width_map[c] for c in line)

        return max((_line_len(line) for line in self.content.splitlines()), default=0)

    @property
    def _height(self) -> NonNegativeInt:
        return len(self.content.splitlines())

    @property
    def dims(self) -> Dimensions[NonNegativeInt, NonNegativeInt]:
        return Dimensions(width=self._width, height=self._height)

    @property
    def within_frame(self) -> DimensionsFit:
        return DimensionsFit(self.dims, self.frame.dims)
