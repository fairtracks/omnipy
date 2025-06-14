from abc import ABC, abstractmethod
from functools import cached_property
from typing import cast, Generic

from typing_extensions import override, TypeIs, TypeVar

from omnipy.data._display.dimensions import (Dimensions,
                                             DimensionsFit,
                                             DimensionsWithWidthAndHeight,
                                             has_height)
from omnipy.data._display.frame import AnyFrame, empty_frame, Frame
from omnipy.data._display.helpers import soft_wrap_words
import omnipy.util._pydantic as pyd

FrameT = TypeVar('FrameT', bound=AnyFrame, default=AnyFrame, covariant=True)
FrameInvT = TypeVar('FrameInvT', bound=AnyFrame, default=AnyFrame)


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

    def __init__(self, title: str = '', frame: FrameT | None = None):
        object.__setattr__(self, 'title', title)
        object.__setattr__(self, 'frame', frame or cast(FrameT, empty_frame()))

    @pyd.validator('frame')
    def _copy_frame(cls, frame: Frame) -> Frame:
        return Frame(
            dims=frame.dims,
            fixed_width=frame.fixed_width,
            fixed_height=frame.fixed_height,
        )

    @abstractmethod
    def render_next_stage(self) -> 'Panel[FrameT]':
        ...


def panel_is_dimensions_aware(panel: 'Panel') -> TypeIs['DimensionsAwarePanel']:
    return isinstance(panel, DimensionsAwarePanel)


def panel_is_fully_rendered(panel: 'Panel') -> TypeIs['FullyRenderedPanel']:
    return isinstance(panel, FullyRenderedPanel)


class DimensionsAwarePanel(Panel[FrameT], Generic[FrameT]):
    TITLE_BLANK_LINES = 1
    DOUBLE_LINE_TITLE_HEIGHT = TITLE_BLANK_LINES + 2
    SINGLE_LINE_TITLE_HEIGHT = TITLE_BLANK_LINES + 1

    MIN_PANEL_LINES_SHOWN_TO_ALLOW_DOUBLE_LINE_TITLE = 8
    MIN_PANEL_LINES_SHOWN_TO_ALLOW_SINGLE_LINE_TITLE = 3

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
    def within_frame(self) -> DimensionsFit:
        return DimensionsFit(self.dims, self.frame.dims)

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
        if self._available_height_for_title >= self.DOUBLE_LINE_TITLE_HEIGHT:
            # Enough space for both single- or double-line titles
            return 2
        elif self._available_height_for_title == self.SINGLE_LINE_TITLE_HEIGHT:
            # Enough space for single-line title
            return 1
        else:  # title needs to make use of panel space
            if (self.frame.dims.height - self.DOUBLE_LINE_TITLE_HEIGHT
                    >= self.MIN_PANEL_LINES_SHOWN_TO_ALLOW_DOUBLE_LINE_TITLE):
                # Enough content shown for double-line title
                return 2
            elif (self.frame.dims.height - self.SINGLE_LINE_TITLE_HEIGHT
                  >= self.MIN_PANEL_LINES_SHOWN_TO_ALLOW_SINGLE_LINE_TITLE):
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
        return self._available_height_for_title < self.SINGLE_LINE_TITLE_HEIGHT

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
        return self.title_height + self.TITLE_BLANK_LINES if self.title_height > 0 else 0


class FullyRenderedPanel(DimensionsAwarePanel[FrameT], Generic[FrameT]):
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
