from typing import Generic

from typing_extensions import TypeIs

from omnipy.data._display.dimensions import (Dimensions,
                                             has_height,
                                             has_width,
                                             has_width_and_height,
                                             HeightT,
                                             WidthT)
from omnipy.util._pydantic import ConfigDict, dataclass, Extra, NonNegativeInt, validator


@dataclass(config=ConfigDict(extra=Extra.forbid, validate_assignment=True))
class Frame(Generic[WidthT, HeightT]):
    dims: Dimensions[WidthT, HeightT]

    @validator('dims', pre=True)
    def _copy_dims(cls, dims: Dimensions[WidthT, HeightT]) -> Dimensions[WidthT, HeightT]:
        return Dimensions(dims.width, dims.height)


def empty_frame() -> Frame[None, None]:
    return Frame(Dimensions(width=None, height=None))


GeneralFrame = Frame[NonNegativeInt | None, NonNegativeInt | None]
UndefinedFrame = Frame[None, None]
FrameWithWidth = Frame[NonNegativeInt, NonNegativeInt | None]
FrameWithHeight = Frame[NonNegativeInt | None, NonNegativeInt]
FrameWithWidthAndHeight = Frame[NonNegativeInt, NonNegativeInt]
AnyFrame = GeneralFrame | FrameWithWidth | FrameWithHeight | FrameWithWidthAndHeight


def frame_has_width(frame: AnyFrame) -> TypeIs[FrameWithWidth | FrameWithWidthAndHeight]:
    return has_width(frame.dims)


def frame_has_height(frame: AnyFrame) -> TypeIs[FrameWithHeight | FrameWithWidthAndHeight]:
    return has_height(frame.dims)


def frame_has_width_and_height(frame: AnyFrame) -> TypeIs[FrameWithWidthAndHeight]:
    return has_width_and_height(frame.dims)
