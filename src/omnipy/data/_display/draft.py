from dataclasses import asdict
from typing import ClassVar, Generic, TypeAlias

from typing_extensions import TypeIs, TypeVar

from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsFit,
                                             has_height,
                                             has_width,
                                             has_width_and_height,
                                             HeightT,
                                             WidthT)
from omnipy.data._display.enum import PrettyPrinterLib
from omnipy.data._display.helpers import UnicodeCharWidthMap
from omnipy.util._pydantic import ConfigDict, dataclass, Extra, Field, NonNegativeInt, validator

ContentT = TypeVar('ContentT', bound=object, default=object, covariant=True)
FrameT = TypeVar('FrameT', bound='AnyFrame', default='AnyFrame')


@dataclass(kw_only=True, config=ConfigDict(extra=Extra.forbid))
class OutputConfig:
    indent_tab_size: NonNegativeInt = 2
    debug_mode: bool = False
    pretty_printer: PrettyPrinterLib = PrettyPrinterLib.RICH


@dataclass
class Frame(Generic[WidthT, HeightT]):
    dims: Dimensions[WidthT, HeightT] = Field(default_factory=Dimensions)

    @validator('dims', pre=True)
    def _copy_dims(cls, dims: Dimensions[WidthT, HeightT]) -> Dimensions[WidthT, HeightT]:
        return Dimensions(dims.width, dims.height)


GeneralFrame: TypeAlias = Frame[NonNegativeInt | None, NonNegativeInt | None]
UndefinedFrame: TypeAlias = Frame[None, None]
FrameWithWidth: TypeAlias = Frame[NonNegativeInt, NonNegativeInt | None]
FrameWithHeight: TypeAlias = Frame[NonNegativeInt | None, NonNegativeInt]
FrameWithWidthAndHeight: TypeAlias = Frame[NonNegativeInt, NonNegativeInt]
AnyFrame: TypeAlias = GeneralFrame | FrameWithWidth | FrameWithHeight | FrameWithWidthAndHeight


def frame_has_width(frame: AnyFrame) -> TypeIs[FrameWithWidth | FrameWithWidthAndHeight]:
    return has_width(frame.dims)


def frame_has_height(frame: AnyFrame) -> TypeIs[FrameWithHeight | FrameWithWidthAndHeight]:
    return has_height(frame.dims)


def frame_has_width_and_height(frame: AnyFrame) -> TypeIs[FrameWithWidthAndHeight]:
    return has_width_and_height(frame.dims)


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
