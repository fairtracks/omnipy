from pydantic import ConfigDict, Extra, NonNegativeInt, validate_arguments, validator
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(extra=Extra.forbid))
class Dimensions:
    width: NonNegativeInt | None = None
    height: NonNegativeInt | None = None


@dataclass(config=ConfigDict(extra=Extra.forbid))
class DefinedDimensions(Dimensions):
    @validator('width', 'height')
    def no_none_values(cls, value: NonNegativeInt | None):
        if value is None:
            raise ValueError('Dimension value cannot be None')
        return value


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
