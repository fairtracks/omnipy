from typing import cast, Generic

from typing_extensions import TypeIs

from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsWithWidthAndHeight,
                                             has_height,
                                             has_width,
                                             has_width_and_height,
                                             HeightT,
                                             WidthT)
import omnipy.util._pydantic as pyd


@pyd.dataclass(frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True))
class Frame(Generic[WidthT, HeightT]):
    dims: Dimensions[WidthT, HeightT]
    fixed_width: bool | None = None
    fixed_height: bool | None = None

    @pyd.validator('dims', pre=True)
    def _copy_dims(cls, dims: Dimensions[WidthT, HeightT]) -> Dimensions[WidthT, HeightT]:
        return Dimensions(dims.width, dims.height)

    @staticmethod
    def _not_fixed_if_empty(
        dims_attr: str,
        fixed_value: bool | None,
        dims: Dimensions,
        raise_if_incorrect: bool = True,
    ) -> bool:
        dim_value = getattr(dims, dims_attr)
        if dim_value is None:
            if raise_if_incorrect:
                assert fixed_value is not True, \
                    f'Cannot fix {dims_attr} of frame with {dims_attr}=None'
            return False
        return True if fixed_value is None else fixed_value

    @pyd.validator('fixed_width', pre=True, always=True)
    def _not_fixed_width_if_empty_frame(
        cls,
        fixed_width: bool | None,
        values: dict[str, Dimensions[WidthT, HeightT]],
    ) -> bool:
        return cls._not_fixed_if_empty('width', fixed_width, values['dims'])

    @pyd.validator('fixed_height', pre=True, always=True)
    def _not_fixed_height_if_empty_frame(
        cls,
        fixed_height: bool | None,
        values: dict[str, Dimensions[WidthT, HeightT]],
    ) -> bool:
        return cls._not_fixed_if_empty('height', fixed_height, values['dims'])

    def modified_copy(
        self,
        width: pyd.NonNegativeInt | None | pyd.UndefinedType = pyd.Undefined,
        height: pyd.NonNegativeInt | None | pyd.UndefinedType = pyd.Undefined,
        fixed_width: bool | None | pyd.UndefinedType = pyd.Undefined,
        fixed_height: bool | None | pyd.UndefinedType = pyd.Undefined,
    ) -> 'Frame':
        """
        Create a modified copy of the frame with specified changes.

        Parameters that are Undefined will use the current frame's values.
        """
        if isinstance(width, pyd.UndefinedType):
            width = self.dims.width

        if isinstance(height, pyd.UndefinedType):
            height = self.dims.height

        # Create new dimensions
        new_dims = Dimensions(width=width, height=height)

        if isinstance(fixed_width, pyd.UndefinedType):
            fixed_width = self._not_fixed_if_empty(
                'width',
                self.fixed_width,
                new_dims,
                raise_if_incorrect=False,
            )

        if isinstance(fixed_height, pyd.UndefinedType):
            fixed_height = self._not_fixed_if_empty(
                'height',
                self.fixed_height,
                new_dims,
                raise_if_incorrect=False,
            )

        # Create new frame with updated values
        return Frame(dims=new_dims, fixed_width=fixed_width, fixed_height=fixed_height)

    def _crop_dims(
        self,
        value: pyd.NonNegativeInt,
        dim_attr: str,
        fixed_dim_attr: str,
        ignore_fixed_dims: bool,
    ) -> pyd.NonNegativeInt:
        frame_dim = cast(pyd.NonNegativeInt | None, getattr(self.dims, dim_attr))
        fixed_dim = cast(bool, getattr(self, fixed_dim_attr))

        if frame_dim is not None:
            if fixed_dim and not ignore_fixed_dims:
                return frame_dim
            else:
                return min(frame_dim, value)
        else:
            return value

    def crop_width(
        self,
        width: pyd.NonNegativeInt,
        ignore_fixed_dims=False,
    ) -> pyd.NonNegativeInt:
        """Crop the frame's width to the specified value."""
        return self._crop_dims(width, 'width', 'fixed_width', ignore_fixed_dims)

    def crop_height(
        self,
        height: pyd.NonNegativeInt,
        ignore_fixed_dims=False,
    ) -> pyd.NonNegativeInt:
        """Crop the frame's width to the specified value."""
        return self._crop_dims(height, 'height', 'fixed_height', ignore_fixed_dims)

    def crop_dims(
        self,
        dims: DimensionsWithWidthAndHeight,
        ignore_fixed_dims=False,
    ) -> DimensionsWithWidthAndHeight:
        """Crop the frame's dimensions to the specified values."""
        return Dimensions(
            width=self.crop_width(dims.width, ignore_fixed_dims),
            height=self.crop_height(dims.height, ignore_fixed_dims),
        )


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
