from enum import Enum
from typing import Generic

from typing_extensions import TypeIs, TypeVar

from omnipy.util._pydantic import ConfigDict, dataclass, Extra, Field, NonNegativeInt

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


class Proportionally(str, Enum):
    THINNER = 'thinner'
    SAME = 'same'
    WIDER = 'wider'


class DimensionsFit:
    def __init__(self, dims: DimensionsWithWidthAndHeight, frame_dims: Dimensions):
        assert has_width_and_height(dims)

        self._width: bool | None = None
        self._height: bool | None = None
        self._proportionality: Proportionally | None = None

        if frame_dims.width is not None:
            self._width = dims.width <= frame_dims.width

        if frame_dims.height is not None:
            self._height = dims.height <= frame_dims.height

        if frame_dims.width not in [None, 0] and frame_dims.height not in [None, 0]:
            self._proportionality = self._calculate_proportionality(dims, frame_dims)

    def _calculate_proportionality(self, dims, frame_dims) -> Proportionally:
        frame_width_height_ratio = frame_dims.width / frame_dims.height
        proportional_width = dims.height * frame_width_height_ratio

        if proportional_width < dims.width:
            return Proportionally.WIDER
        elif proportional_width == dims.width:
            return Proportionally.SAME
        else:
            return Proportionally.THINNER

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def proportionality(self):
        return self._proportionality

    @property
    def both(self):
        if self.width is None or self.height is None:
            return None
        else:
            return self.width and self.height
