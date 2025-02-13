from typing import Generic

from typing_extensions import TypeVar

from omnipy.util._pydantic import (ConfigDict,
                                   dataclass,
                                   Extra,
                                   Field,
                                   NonNegativeInt,
                                   validate_arguments)

NumberT = TypeVar('NumberT', bound=NonNegativeInt | None)


@dataclass(config=ConfigDict(extra=Extra.forbid))
class Dimensions(Generic[NumberT]):
    width: NumberT = Field(default=None)
    height: NumberT = Field(default=None)


@dataclass(config=ConfigDict(extra=Extra.forbid))
class DefinedDimensions(Dimensions[NonNegativeInt]):
    @staticmethod
    def _default_number() -> NonNegativeInt:
        raise TypeError("Attributes 'width' and 'height' must be defined at initialization")

    width: NonNegativeInt = Field(default_factory=_default_number)
    height: NonNegativeInt = Field(default_factory=_default_number)


@dataclass(frozen=True)
class DimensionsFit:
    width: bool | None = None
    height: bool | None = None

    @validate_arguments
    def __init__(self, dims: DefinedDimensions, frame_dims: Dimensions):
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
