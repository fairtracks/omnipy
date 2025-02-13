from typing import ClassVar, Generic

from typing_extensions import TypeVar

from omnipy.data._display.dimensions import DefinedDimensions, Dimensions, DimensionsFit
from omnipy.data._display.enum import PrettyPrinterLib
from omnipy.data._display.helpers import UnicodeCharWidthMap
from omnipy.util._pydantic import ConfigDict, dataclass, Extra, Field, NonNegativeInt

DimensionsT = TypeVar('DimensionsT', bound=Dimensions)
ContentT = TypeVar('ContentT', bound=object)
FrameT = TypeVar('FrameT', bound='Frame')


@dataclass(kw_only=True, config=ConfigDict(extra=Extra.forbid))
class OutputConfig:
    indent_tab_size: NonNegativeInt = 2
    debug_mode: bool = False
    pretty_printer: PrettyPrinterLib = PrettyPrinterLib.RICH


@dataclass
class Frame(Generic[DimensionsT]):
    dims: DimensionsT = Field(default_factory=Dimensions)


@dataclass
class DefinedFrame(Frame[DefinedDimensions]):
    @staticmethod
    def _default_dims() -> DefinedDimensions:
        raise TypeError("Attribute 'dims' must be defined at initialization")

    dims: DefinedDimensions = Field(default_factory=_default_dims)

    @classmethod
    def from_frame(cls, frame: Frame[Dimensions]) -> 'DefinedFrame':
        return DefinedFrame(
            dims=DefinedDimensions(
                width=frame.dims.width,
                height=frame.dims.height,
            ))


@dataclass
class DraftOutput(Generic[ContentT, FrameT]):
    content: ContentT
    frame: FrameT = Field(default_factory=Frame)
    config: OutputConfig = Field(default_factory=OutputConfig)


@dataclass
class FramedDraftOutput(DraftOutput[ContentT, DefinedFrame], Generic[ContentT]):
    frame: DefinedFrame = Field(default_factory=DefinedFrame)


@dataclass
class DraftMonospacedOutput(DraftOutput[str, Frame]):
    _char_width_map: ClassVar[UnicodeCharWidthMap] = UnicodeCharWidthMap()
    content: str

    @property
    def _width(self):
        def _line_len(line: str) -> int:
            return sum(self._char_width_map[c] for c in line)

        return max((_line_len(line) for line in self.content.splitlines()), default=0)

    @property
    def _height(self):
        return len(self.content.splitlines())

    @property
    def dims(self) -> DefinedDimensions:
        return DefinedDimensions(width=self._width, height=self._height)

    @property
    def within_frame(self) -> DimensionsFit:
        return DimensionsFit(self.dims, self.frame.dims)
