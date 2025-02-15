from typing import Generic

from typing_extensions import TypeIs, TypeVar

from omnipy.util._pydantic import (ConfigDict,
                                   dataclass,
                                   Extra,
                                   Field,
                                   NonNegativeInt,
                                   validate_arguments)

WidthT = TypeVar(
    'WidthT',
    bound=NonNegativeInt | None,
    default=NonNegativeInt | None,
    covariant=True,
)

HeightT = TypeVar(
    'HeightT',
    bound=NonNegativeInt | None,
    default=NonNegativeInt | None,
    covariant=True,
)


@dataclass(config=ConfigDict(extra=Extra.forbid, validate_assignment=True))
class Dimensions(Generic[WidthT, HeightT]):
    width: WidthT = Field(default=None)
    height: HeightT = Field(default=None)


UndefinedDimensions = Dimensions[None, None]
GeneralDimensions = Dimensions[NonNegativeInt | None, NonNegativeInt | None]
DimensionsWithWidth = Dimensions[NonNegativeInt, NonNegativeInt | None]
DimensionsWithHeight = Dimensions[NonNegativeInt | None, NonNegativeInt]
DimensionsWithWidthAndHeight = Dimensions[NonNegativeInt, NonNegativeInt]
AnyDimensions = (
    GeneralDimensions | DimensionsWithWidth | DimensionsWithHeight | DimensionsWithWidthAndHeight)


def has_width(dims: AnyDimensions) -> TypeIs[DimensionsWithWidth | DimensionsWithWidthAndHeight]:
    return dims.width is not None


def has_height(dims: AnyDimensions) -> TypeIs[DimensionsWithHeight | DimensionsWithWidthAndHeight]:
    return dims.height is not None


def has_width_and_height(dims: AnyDimensions) -> TypeIs[DimensionsWithWidthAndHeight]:
    return has_width(dims) and has_height(dims)


@dataclass(frozen=True)
class DimensionsFit:
    width: bool | None = None
    height: bool | None = None

    @validate_arguments
    def __init__(self, dims: DimensionsWithWidthAndHeight, frame_dims: Dimensions):
        assert dims.width is not None and dims.height is not None
        if frame_dims.width is not None:
            object.__setattr__(self, 'width', dims.width <= frame_dims.width)
        if dims.height is not None and frame_dims.height is not None:
            object.__setattr__(self, 'height', dims.height <= frame_dims.height)

    # TODO: With Pydantic v2, use @computed_field for DimensionsFit.both
    @property
    def both(self):
        if self.width is None or self.height is None:
            return None
        else:
            return self.width and self.height
