from enum import Enum
from typing import Generic

from typing_extensions import TypeIs, TypeVar

import omnipy.util._pydantic as pyd

WidthT = TypeVar(
    'WidthT',
    bound=pyd.NonNegativeInt | None,
    default=pyd.NonNegativeInt | None,
    covariant=True,
)

HeightT = TypeVar(
    'HeightT',
    bound=pyd.NonNegativeInt | None,
    default=pyd.NonNegativeInt | None,
    covariant=True,
)


@pyd.dataclass(frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True))
class Dimensions(Generic[WidthT, HeightT]):
    width: WidthT
    height: HeightT


UndefinedDimensions = Dimensions[None, None]
GeneralDimensions = Dimensions[pyd.NonNegativeInt | None, pyd.NonNegativeInt | None]
DimensionsWithWidth = Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt | None]
DimensionsWithHeight = Dimensions[pyd.NonNegativeInt | None, pyd.NonNegativeInt]
DimensionsWithWidthAndHeight = Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]
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
    def width(self) -> bool | None:
        return self._width

    @property
    def height(self) -> bool | None:
        return self._height

    @property
    def proportionality(self) -> Proportionally | None:
        return self._proportionality

    @property
    def both(self) -> bool | None:
        if self.width is None or self.height is None:
            return None
        else:
            return self.width and self.height
