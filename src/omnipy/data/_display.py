from enum import Enum
import re
from typing import Generic, NamedTuple

from devtools import PrettyFormat
from rich.pretty import pretty_repr as rich_pretty_repr
from typing_extensions import TypeVar

from omnipy.data.typechecks import is_model_instance
from omnipy.util._pydantic import (ConfigDict,
                                   dataclass,
                                   Extra,
                                   Field,
                                   NonNegativeInt,
                                   validate_arguments,
                                   validator)


@dataclass(config=ConfigDict(extra=Extra.forbid))
class Dimensions:
    width: NonNegativeInt | None = None
    height: NonNegativeInt | None = None


@dataclass(config=ConfigDict(extra=Extra.forbid))
class DefinedDimensions(Dimensions):
    # width: NonNegativeInt | None = None
    # height: NonNegativeInt | None = None

    @validator('width', 'height')
    def no_none_values(cls, v):
        if v is None:
            raise ValueError('Dimension value cannot be None')
        return v


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


class PrettyPrinterLib(str, Enum):
    DEVTOOLS = 'devtools'
    RICH = 'rich'


@dataclass(kw_only=True, config=ConfigDict(extra=Extra.forbid))
class OutputConfig:
    indent_tab_size: NonNegativeInt = 2
    debug_mode: bool = False
    pretty_printer: PrettyPrinterLib = PrettyPrinterLib.RICH


@dataclass
class Frame:
    dims: Dimensions = Field(default_factory=Dimensions)


ContentT = TypeVar('ContentT', bound=object)


@dataclass
class DraftOutput(Generic[ContentT]):
    content: ContentT
    frame: Frame = Field(default_factory=Frame)
    config: OutputConfig = Field(default_factory=OutputConfig)


@dataclass
class DraftTextOutput(DraftOutput[str]):
    content: str

    @property
    def _width(self):
        if len(self.content) == 0:
            return 0
        return max(len(line) for line in self.content.splitlines())

    @property
    def _height(self):
        return len(self.content.splitlines())

    @property
    def dims(self) -> DefinedDimensions:
        return DefinedDimensions(width=self._width, height=self._height)

    @property
    def within_frame(self) -> DimensionsFit:
        return DimensionsFit(self.dims, self.frame.dims)


_DEFAULT_INDENT_TAB_SIZE = 2
_DEFAULT_MAX_WIDTH = 80
_DEFAULT_HEIGHT = 24
_DEFAULT_PRETTY_PRINTER: PrettyPrinterLib = PrettyPrinterLib.DEVTOOLS


class ReprMeasures(NamedTuple):
    num_lines: int
    max_line_width: int
    max_container_width: int


def _max_container_width(repr_lines: list[str]) -> int:
    def _max_container_length_in_line(line):
        # Find all containers in the line using regex
        containers = re.findall(r'\{.*\}|\[.*\]|\(.*\)', line)
        # Return the length of the longest container, or 0 if none are found
        return max((len(container) for container in containers), default=0)

    # Calculate the maximum container width across all lines
    return max((_max_container_length_in_line(line) for line in repr_lines), default=0)


def _get_repr_measures(repr_str: str) -> ReprMeasures:
    repr_lines = repr_str.splitlines()
    num_lines = len(repr_lines)
    max_line_width = max(len(line) for line in repr_lines)
    max_container_width = _max_container_width(repr_lines)
    return ReprMeasures(num_lines, max_line_width, max_container_width)


def _any_abbrev_containers(repr_str: str) -> bool:
    return bool(re.search(r'\[...\]|\(...\)|\{...\}', repr_str))


def _is_nested_structure(data, full_repr):
    only_1st_level_repr = rich_pretty_repr(data, max_depth=1)
    if _any_abbrev_containers(only_1st_level_repr):
        return True
    return False


def _basic_pretty_repr(
    data: object,
    indent_tab_size: int = _DEFAULT_INDENT_TAB_SIZE,
    max_line_width: int = _DEFAULT_MAX_WIDTH,
    max_container_width: int = _DEFAULT_MAX_WIDTH,
    pretty_printer: PrettyPrinterLib = _DEFAULT_PRETTY_PRINTER,
) -> str:
    match pretty_printer:
        case PrettyPrinterLib.RICH:
            return rich_pretty_repr(
                data,
                indent_size=indent_tab_size,
                max_width=max_line_width + 1,
            )
        case PrettyPrinterLib.DEVTOOLS:
            pf = PrettyFormat(
                indent_step=indent_tab_size,
                simple_cutoff=max_container_width,
                width=max_line_width + 1,
            )
            return pf(data)


def _get_delta_line_width(pretty_printer: PrettyPrinterLib, measures: ReprMeasures) -> int:
    if measures.num_lines == 1 and pretty_printer == PrettyPrinterLib.RICH:
        return 2
    return 1


def _adjusted_multi_line_pretty_repr(
    data: object,
    repr_str: str,
    indent_tab_size: int,
    max_width: int,
    height: int,
    pretty_printer: PrettyPrinterLib,
):
    prev_max_container_width = None
    width_to_height_ratio = max_width / height

    while True:
        measures = _get_repr_measures(repr_str)
        if (max_width >= measures.max_line_width
                and measures.num_lines * width_to_height_ratio >= measures.max_line_width):
            break

        if (prev_max_container_width is not None
                and prev_max_container_width <= measures.max_container_width):
            break
        else:
            prev_max_container_width = measures.max_container_width

        delta_line_width = _get_delta_line_width(pretty_printer, measures)

        repr_str = _basic_pretty_repr(
            data,
            indent_tab_size=indent_tab_size,
            max_line_width=measures.max_line_width - delta_line_width,
            max_container_width=measures.max_container_width - 1,
            pretty_printer=pretty_printer,
        )

    return repr_str


def pretty_repr(
    data: object,
    indent_tab_size: int = _DEFAULT_INDENT_TAB_SIZE,
    max_width: int = _DEFAULT_MAX_WIDTH,
    height: int = _DEFAULT_HEIGHT,
    pretty_printer: PrettyPrinterLib = _DEFAULT_PRETTY_PRINTER,
    debug_mode: bool = False,
) -> str:
    if is_model_instance(data) and not debug_mode:
        data = data.to_data()

    full_repr = _basic_pretty_repr(
        data,
        indent_tab_size=indent_tab_size,
        max_line_width=max_width,
        max_container_width=max_width,
        pretty_printer=pretty_printer,
    )
    if _is_nested_structure(data, full_repr):
        return _adjusted_multi_line_pretty_repr(
            data,
            repr_str=full_repr,
            indent_tab_size=indent_tab_size,
            max_width=max_width,
            height=height,
            pretty_printer=pretty_printer,
        )
    return full_repr
