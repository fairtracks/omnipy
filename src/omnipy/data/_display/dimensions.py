"""Dimension value objects and fit checks for rendered display content.

Type Aliases:
    WidthT: Width type parameter for dimension-aware objects.
    HeightT: Height type parameter for dimension-aware objects.
    UndefinedDimensions: Dimensions with neither width nor height set.
    GeneralDimensions: Dimensions with optional width and height.
    DimensionsWithWidth: Dimensions with known width.
    DimensionsWithHeight: Dimensions with known height.
    DimensionsWithWidthAndHeight: Dimensions with both axes known.
    DimensionsWithWidthOrHeight: Dimensions with at least one known axis.
    AnyDimensions: Union of supported public dimension shapes.
"""

from typing import Generic, Literal

from typing_extensions import TypeIs, TypeVar

from omnipy.util.literal_enum import LiteralEnum
import omnipy.util.pydantic as pyd

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
    """Immutable width and height pair used across the display pipeline."""

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
    """Return whether the dimensions object has a concrete width."""

    return dims.width is not None


def has_height(dims: AnyDimensions) -> TypeIs[DimensionsWithHeight | DimensionsWithWidthAndHeight]:
    """Return whether the dimensions object has a concrete height."""

    return dims.height is not None


def has_width_and_height(dims: AnyDimensions) -> TypeIs[DimensionsWithWidthAndHeight]:
    """Return whether both width and height are concrete."""

    return has_width(dims) and has_height(dims)


def has_width_or_height(dims: AnyDimensions) -> TypeIs[DimensionsWithWidthOrHeight]:
    """Return whether at least one dimension is concrete."""

    return has_width(dims) or has_height(dims)


class Proportionally(LiteralEnum[int]):
    """Relative shape comparison between content and its containing frame."""

    Literals = Literal[-2, -1, 0, 1, 2]

    MUCH_THINNER: Literal[-2] = -2
    THINNER: Literal[-1] = -1
    SAME: Literal[0] = 0
    WIDER: Literal[1] = 1
    MUCH_WIDER: Literal[2] = 2


class DimensionsFit:
    """Summarize whether rendered dimensions fit a target frame."""

    def __init__(self,
                 dims: DimensionsWithWidthAndHeight,
                 frame_dims: Dimensions,
                 proportional_freedom: pyd.NonNegativeFloat | None = 2.5):
        assert has_width_and_height(dims)

        self._width: bool | None = None
        self._height: bool | None = None
        self._proportionality: Proportionally.Literals | None = None
        self._proportional_freedom: pyd.NonNegativeFloat | None = proportional_freedom

        if self._proportional_freedom is None:
            self._proportionality
        else:
            if frame_dims.width is not None:
                self._width = dims.width <= frame_dims.width

            if frame_dims.height is not None:
                self._height = dims.height <= frame_dims.height

            if (dims.width > 0 and dims.height > 0 and frame_dims.width not in [None, 0]
                    and frame_dims.height not in [None, 0]):
                assert has_width_and_height(frame_dims)
                self._proportionality = self._calculate_proportionality(dims, frame_dims)

    def _calculate_proportionality(
        self,
        dims: DimensionsWithWidthAndHeight,
        frame_dims: DimensionsWithWidthAndHeight,
    ) -> Proportionally.Literals:
        assert self._proportional_freedom is not None

        frame_width_height_ratio = frame_dims.width / frame_dims.height
        proportional_width = dims.height * frame_width_height_ratio
        proportional_height = dims.width / frame_width_height_ratio

        proportional_width_freedom_multiplier = max(
            1 + self._proportional_freedom * frame_dims.width / dims.width,
            1,
        )
        proportional_height_freedom_multiplier = max(
            1 + self._proportional_freedom * frame_dims.height / dims.height,
            1,
        )

        if proportional_width * proportional_width_freedom_multiplier < dims.width:
            return Proportionally.MUCH_WIDER
        elif proportional_width < dims.width:
            return Proportionally.WIDER
        elif proportional_width == dims.width:
            return Proportionally.SAME
        elif proportional_height * proportional_height_freedom_multiplier < dims.height:
            return Proportionally.MUCH_THINNER
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
        prop_str = f'Proportionally.{Proportionally.name_for_value(self.proportionality)}' \
            if self.proportionality is not None else 'None'

        return (f'DimensionsFit('
                f'width={self.width}, '
                f'height={self.height}, '
                f'both={self.both}, '
                f'proportionality={prop_str})')
