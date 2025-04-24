from typing import Generic

from typing_extensions import TypeIs

from omnipy.data._display.dimensions import (Dimensions,
                                             has_height,
                                             has_width,
                                             has_width_and_height,
                                             HeightT,
                                             WidthT)
import omnipy.util._pydantic as pyd


@pyd.dataclass(frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True))
class Frame(Generic[WidthT, HeightT]):
    dims: Dimensions[WidthT, HeightT]
    fixed_dims: bool | None = None

    @pyd.validator('dims', pre=True)
    def _copy_dims(cls, dims: Dimensions[WidthT, HeightT]) -> Dimensions[WidthT, HeightT]:
        return Dimensions(dims.width, dims.height)

    @pyd.validator('fixed_dims', pre=True, always=True)
    def _not_fixed_dims_if_empty_frame(cls,
                                       fixed_dims: bool | None,
                                       values: dict[str, Dimensions[WidthT, HeightT]]) -> bool:
        dims = values['dims']
        if dims.width is None and dims.height is None:
            assert fixed_dims is not True, 'Empty frames cannot have fixed dimensions.'
            return False
        return True if fixed_dims is None else fixed_dims


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
