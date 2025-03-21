from typing import Generic

from typing_extensions import TypeIs

from omnipy.data._display.dimensions import (Dimensions,
                                             has_height,
                                             has_width,
                                             has_width_and_height,
                                             HeightT,
                                             WidthT)
import omnipy.util._pydantic as pyd


@pyd.dataclass(config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True))
class Frame(Generic[WidthT, HeightT]):
    dims: Dimensions[WidthT, HeightT]

    @pyd.validator('dims', pre=True)
    def _copy_dims(cls, dims: Dimensions[WidthT, HeightT]) -> Dimensions[WidthT, HeightT]:
        return Dimensions(dims.width, dims.height)


def empty_frame() -> Frame[None, None]:
    return Frame(Dimensions(width=None, height=None))


GeneralFrame = Frame[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]
UndefinedFrame = Frame[None, None]
FrameWithWidth = Frame[pyd.NonNegativeInt, pyd.NonNegativeInt | None]
FrameWithHeight = Frame[pyd.NonNegativeInt | None, pyd.NonNegativeInt]
FrameWithWidthAndHeight = Frame[pyd.NonNegativeInt, pyd.NonNegativeInt]
AnyFrame = GeneralFrame | FrameWithWidth | FrameWithHeight | FrameWithWidthAndHeight


def frame_has_width(frame: AnyFrame) -> TypeIs[FrameWithWidth | FrameWithWidthAndHeight]:
    return has_width(frame.dims)


def frame_has_height(frame: AnyFrame) -> TypeIs[FrameWithHeight | FrameWithWidthAndHeight]:
    return has_height(frame.dims)


def frame_has_width_and_height(frame: AnyFrame) -> TypeIs[FrameWithWidthAndHeight]:
    return has_width_and_height(frame.dims)
