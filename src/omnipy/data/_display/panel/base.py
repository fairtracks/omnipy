from abc import ABC, abstractmethod
from dataclasses import asdict
from functools import cached_property
from typing import cast, Generic

from typing_extensions import override, TypeIs

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsFit,
                                             DimensionsWithWidthAndHeight,
                                             has_height)
from omnipy.data._display.frame import empty_frame, Frame
from omnipy.data._display.helpers import soft_wrap_words
from omnipy.data._display.panel.typedefs import FrameT
from omnipy.shared.constants import (DOUBLE_LINE_TITLE_HEIGHT,
                                     MIN_PANEL_LINES_SHOWN_TO_ALLOW_DOUBLE_LINE_TITLE,
                                     MIN_PANEL_LINES_SHOWN_TO_ALLOW_SINGLE_LINE_TITLE,
                                     SINGLE_LINE_TITLE_HEIGHT,
                                     TITLE_BLANK_LINES)
import omnipy.util._pydantic as pyd


class OutputVariant(ABC):
    @cached_property
    @abstractmethod
    def terminal(self) -> str:
        """
        Returns the terminal representation of the output, encoded according
        to the current console color system.
        """

    @cached_property
    @abstractmethod
    def html_tag(self) -> str:
        """
        Returns a representation of the output as an HTML tag for inclusion
        in a web page.
        """

    @cached_property
    @abstractmethod
    def html_page(self) -> str:
        """
        Returns a representation of the output as an independent HTML page,
        for viewing in a web browser.
        """


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class Panel(Generic[FrameT]):
    """Base panel class that contains frame and title"""
    title: str
    frame: FrameT
    constraints: Constraints
    config: OutputConfig

    def __init__(self,
                 title: str = '',
                 frame: FrameT | None = None,
                 constraints: Constraints | None = None,
                 config: OutputConfig | None = None):
        object.__setattr__(self, 'title', title)
        object.__setattr__(self, 'frame', frame or cast(FrameT, empty_frame()))
        object.__setattr__(self, 'constraints', constraints or Constraints())
        object.__setattr__(self, 'config', config or OutputConfig())

    @pyd.validator('frame')
    def _copy_frame(cls, frame: Frame) -> Frame:
        return Frame(
            dims=frame.dims,
            fixed_width=frame.fixed_width,
            fixed_height=frame.fixed_height,
        )

    @pyd.validator('constraints')
    def _copy_constraints(cls, constraints: Constraints) -> Constraints:
        return Constraints(**asdict(constraints))

    @pyd.validator('config')
    def _copy_config(cls, config: OutputConfig) -> OutputConfig:
        return OutputConfig(**asdict(config))

    @abstractmethod
    def render_next_stage(self) -> 'DimensionsAwarePanel[FrameT] | FullyRenderedPanel[FrameT]':
        ...


def panel_is_dimensions_aware(panel: 'Panel') -> TypeIs['DimensionsAwarePanel']:
    return isinstance(panel, DimensionsAwarePanel)


def panel_is_fully_rendered(panel: 'Panel') -> TypeIs['FullyRenderedPanel']:
    return isinstance(panel, FullyRenderedPanel)


class DimensionsAwarePanel(Panel[FrameT], Generic[FrameT], ABC):
    @cached_property
    @abstractmethod
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        ...

    @cached_property
    def cropped_dims(self,) -> DimensionsWithWidthAndHeight:
        """
        Returns the dimensions of the panel, cropped to fit within the
        frame dimensions.
        """
        return self.frame.crop_dims(self.dims)

    @cached_property
    def outer_dims(self) -> DimensionsWithWidthAndHeight:
        """
        Returns the outer dimensions of the panel, which includes the title
        height if applicable, and the width of the cropped dimensions or
        the title width, whichever is larger.
        """
        if self.title_height > 0:
            dims_width = max(self.cropped_dims.width, self.title_width)
        else:
            dims_width = self.cropped_dims.width

        dims_height_with_title = self.cropped_dims.height + self.title_height_with_blank_lines
        dims_height = self.frame.crop_height(dims_height_with_title, ignore_fixed_dims=True)

        return Dimensions(width=dims_width, height=dims_height)

    @cached_property
    def inner_frame(self) -> FrameT:
        """
        Returns the inner panel frame, which is the same as
        the outer panel frame, but adjusted for the title height if
        applicable.
        """
        if has_height(self.frame.dims) and self.title_height > 0:
            return cast(
                FrameT,
                self.frame.modified_copy(
                    height=self.frame.dims.height - self.title_height_with_blank_lines,))
        else:
            return self.frame

    @cached_property
    def within_frame(self) -> DimensionsFit:
        """
        Returns a summary of how well the panel's content fit within the
        frame's dimensions (minus the title height, if any).
        """
        return DimensionsFit(
            self.dims,
            self.inner_frame.dims,
            proportional_freedom=self.config.freedom,
        )

    def overly_cropped(self) -> bool:
        """
        Returns True if the panel width has been overly cropped, according
        to the `min_crop_width` defined in the config.
        """
        width_cropped = self.dims.width > self.cropped_dims.width
        width_less_than_min_crop = self.cropped_dims.width < self.config.min_crop_width
        overly_cropped = width_cropped and width_less_than_min_crop
        return overly_cropped

    def width_missing_to_not_be_overly_cropped(self) -> pyd.NonNegativeInt:
        """
        Calculates the width that needs to be added to the panel frame in
        order for the panel to be considered overly_cropped according to
        the `min_crop_width` defined in the config. If the panel is not
        currently considered overly cropped, this function returns 0.
        """
        if not self.overly_cropped():
            return 0
        return max(self.config.min_crop_width - self.cropped_dims.width, 0)

    @cached_property
    def _available_height_for_title(self) -> int | None:
        if has_height(self.frame.dims):
            return max(self.frame.dims.height - self.cropped_dims.height, 0)
        else:
            return None

    @cached_property
    def _max_title_height(self) -> int:
        if self.frame.dims.height is None:
            # No table cell height restrictions, so space for both single-
            # and double-line titles
            return 2

        assert self._available_height_for_title is not None
        if self._available_height_for_title >= DOUBLE_LINE_TITLE_HEIGHT:
            # Enough space for both single- or double-line titles
            return 2
        elif self._available_height_for_title == SINGLE_LINE_TITLE_HEIGHT:
            # Enough space for single-line title
            return 1
        else:  # title needs to make use of panel space
            if (self.frame.dims.height - DOUBLE_LINE_TITLE_HEIGHT
                    >= MIN_PANEL_LINES_SHOWN_TO_ALLOW_DOUBLE_LINE_TITLE):
                # Enough content shown for double-line title
                return 2
            elif (self.frame.dims.height - SINGLE_LINE_TITLE_HEIGHT
                  >= MIN_PANEL_LINES_SHOWN_TO_ALLOW_SINGLE_LINE_TITLE):
                # Enough content shown for single-line title
                return 1
            else:
                # Not enough space for title
                return 0

    @cached_property
    def title_overlaps_panel(self) -> bool:
        """
        Returns True if the title overlaps with the panel content.
        """
        if self._available_height_for_title is None:
            return False
        return self._available_height_for_title < SINGLE_LINE_TITLE_HEIGHT

    @cached_property
    def resized_title(self) -> list[str]:
        if self.title == '':
            return []
        else:
            title_width = self.frame.crop_width(self.dims.width, ignore_fixed_dims=True)

            title_words = self.title.split()
            while True:
                title_lines = soft_wrap_words(title_words, title_width)
                if 1 <= len(title_lines) <= max(self._max_title_height, 1):
                    break
                title_width += 1

            return title_lines

    @cached_property
    def title_width(self) -> int:
        return max((len(line) for line in self.resized_title), default=0)

    @cached_property
    def title_height(self) -> int:
        return min(self._max_title_height, len(self.resized_title))

    @cached_property
    def title_height_with_blank_lines(self) -> int:
        return self.title_height + TITLE_BLANK_LINES if self.title_height > 0 else 0

    @abstractmethod
    @override
    def render_next_stage(self) -> 'FullyRenderedPanel[FrameT]':
        ...


class FullyRenderedPanel(DimensionsAwarePanel[FrameT], Generic[FrameT], ABC):
    @override
    def render_next_stage(self) -> 'FullyRenderedPanel[FrameT]':
        raise NotImplementedError('This panel is fully rendered.')

    @cached_property
    @abstractmethod
    def plain(self) -> OutputVariant:
        """
        Returns an OutputVariant object serving plain text representations
        of the output, without any styling or color. The output is also
        cropped to fit the frame dimensions.
        """

    @cached_property
    @abstractmethod
    def bw_stylized(self) -> OutputVariant:
        """
        Returns an OutputVariant object serving a black-and-white stylized
        representation of the output, allowing formatting such as bold or
        italic, but with no color. The output is also cropped to fit the
        frame dimensions.
        """

    @cached_property
    @abstractmethod
    def colorized(self) -> OutputVariant:
        """
        Returns an OutputVariant object serving a colorized representation
        of the output, with color and styling. The output is also cropped
        to fit the frame dimensions.
        """
