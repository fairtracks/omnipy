from typing import Generic

from pydantic import ConfigDict, Extra, Field, NonNegativeInt
from pydantic.dataclasses import dataclass
from typing_extensions import TypeVar

from omnipy.data._display.dimensions import DefinedDimensions, Dimensions, DimensionsFit
from omnipy.data._display.enum import PrettyPrinterLib


@dataclass(kw_only=True, config=ConfigDict(extra=Extra.forbid))
class OutputConfig:
    indent_tab_size: NonNegativeInt = 2
    debug_mode: bool = False
    pretty_printer: PrettyPrinterLib = PrettyPrinterLib.RICH


@dataclass
class Frame:
    dims: Dimensions = Field(default_factory=Dimensions)


ContentT = TypeVar('ContentT', bound=object)


@dataclass
class DraftOutput(Generic[ContentT]):
    content: ContentT
    frame: Frame = Field(default_factory=Frame)
    config: OutputConfig = Field(default_factory=OutputConfig)


@dataclass
class DraftMonospacedOutput(DraftOutput[str]):
    content: str

    @property
    def _width(self):
        if len(self.content) == 0:
            return 0
        return max(len(line) for line in self.content.splitlines())

    @property
    def _height(self):
        return len(self.content.splitlines())

    @property
    def dims(self) -> DefinedDimensions:
        return DefinedDimensions(width=self._width, height=self._height)

    @property
    def within_frame(self) -> DimensionsFit:
        return DimensionsFit(self.dims, self.frame.dims)
