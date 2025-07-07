from typing import Generic, Literal

from typing_extensions import TypeIs, TypeVar

import omnipy.util._pydantic as pyd
from omnipy.util.literal_enum import LiteralEnum

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
DimensionsWithWidthOrHeight = DimensionsWithWidth | DimensionsWithHeight
AnyDimensions = (
    GeneralDimensions | DimensionsWithWidth | DimensionsWithHeight | DimensionsWithWidthAndHeight)


def has_width(dims: AnyDimensions) -> TypeIs[DimensionsWithWidth | DimensionsWithWidthAndHeight]:
    return dims.width is not None


def has_height(dims: AnyDimensions) -> TypeIs[DimensionsWithHeight | DimensionsWithWidthAndHeight]:
    return dims.height is not None


def has_width_and_height(dims: AnyDimensions) -> TypeIs[DimensionsWithWidthAndHeight]:
    return has_width(dims) and has_height(dims)


def has_width_or_height(dims: AnyDimensions) -> TypeIs[DimensionsWithWidthOrHeight]:
    return has_width(dims) or has_height(dims)


class Proportionally(LiteralEnum):
    Literals = Literal['thinner', 'same', 'wider']
    THINNER: Literal['thinner'] = 'thinner'
    SAME: Literal['same'] = 'same'
    WIDER: Literal['wider'] = 'wider'


class DimensionsFit:
    def __init__(self, dims: DimensionsWithWidthAndHeight, frame_dims: Dimensions):
        assert has_width_and_height(dims)

        self._width: bool | None = None
        self._height: bool | None = None
        self._proportionality: Proportionally.Literals | None = None

        if frame_dims.width is not None:
            self._width = dims.width <= frame_dims.width

        if frame_dims.height is not None:
            self._height = dims.height <= frame_dims.height

        if frame_dims.width not in [None, 0] and frame_dims.height not in [None, 0]:
            self._proportionality = self._calculate_proportionality(dims, frame_dims)

    @staticmethod
    def _calculate_proportionality(dims, frame_dims) -> Proportionally.Literals:
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
    def proportionality(self) -> Proportionally.Literals | None:
        return self._proportionality

    @property
    def both(self) -> bool | None:
        if self.width is None or self.height is None:
            return None
        else:
            return self.width and self.height

    def __repr__(self) -> str:
        # Format proportionality properly - None without quotes, strings with quotes
        prop_str = f"'{self.proportionality}'" if self.proportionality is not None else 'None'

        return (f'DimensionsFit('
                f'width={self.width}, '
                f'height={self.height}, '
                f'both={self.both}, '
                f'proportionality={prop_str})')
