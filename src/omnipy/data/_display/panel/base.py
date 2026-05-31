"""Panel base classes defining the staged display rendering pipeline."""

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
import omnipy.util.pydantic as pyd


class OutputVariant(ABC):
    """Container for exporting one rendered panel in multiple output formats.

    Implementations provide plain terminal text plus HTML fragments/pages for
    the same rendered panel content.
    """

    @cached_property
    @abstractmethod
    def terminal(self) -> str:
        """Return terminal representation of the rendered output.

        Returns:
            Terminal text encoded for the active console color system.
        """

    @cached_property
    @abstractmethod
    def html_tag(self) -> str:
        """Return rendered output as embeddable HTML markup.

        Returns:
            HTML snippet suitable for embedding in a larger page.
        """

    @cached_property
    @abstractmethod
    def html_page(self) -> str:
        """Return rendered output as a standalone HTML page.

        Returns:
            Complete HTML document suitable for direct browser viewing.
        """


@pyd.dataclass(
    init=False,
    frozen=True,
    config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_assignment=True),
)
class Panel(Generic[FrameT]):
    """Base panel carrying title, frame, constraints, and output config.

    Panels move through rendering stages, where each stage refines content from
    draft form to dimensions-aware and eventually fully rendered output.
    """
    title: str
    frame: FrameT
    constraints: Constraints
    config: OutputConfig

    def __init__(self,
                 title: str = '',
                 frame: FrameT | None = None,
                 constraints: Constraints | None = None,
                 config: OutputConfig | None = None):
        """Initialize a panel with optional title, frame, constraints, and output config."""
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
        """Render this panel to the next stage in the pipeline.

        Returns:
            A dimensions-aware panel or fully rendered panel, depending on the
            current stage and panel type.
        """
        ...


def panel_is_dimensions_aware(panel: 'Panel') -> TypeIs['DimensionsAwarePanel']:
    """Return whether the panel has reached the dimensions-aware stage.

    Args:
        panel: Panel instance to check.

    Returns:
        ``True`` when the panel is a :class:`DimensionsAwarePanel`.
    """

    return isinstance(panel, DimensionsAwarePanel)


def panel_is_fully_rendered(panel: 'Panel') -> TypeIs['FullyRenderedPanel']:
    """Return whether the panel has reached the fully rendered stage.

    Args:
        panel: Panel instance to check.

    Returns:
        ``True`` when the panel is a :class:`FullyRenderedPanel`.
    """

    return isinstance(panel, FullyRenderedPanel)


class DimensionsAwarePanel(Panel[FrameT], Generic[FrameT], ABC):
    """Panel stage that knows its measured dimensions within a frame.

    This stage can evaluate cropping, title placement, and frame fitness before
    final style-specific output is produced.
    """

    @cached_property
    @abstractmethod
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        """Return measured panel dimensions before frame cropping.

        Returns:
            Width and height of the panel's content at this stage.
        """
        ...

    @cached_property
    def cropped_dims(self,) -> DimensionsWithWidthAndHeight:
        """Return panel dimensions cropped to the frame limits.

        Returns:
            Cropped width and height according to frame constraints.
        """
        return self.frame.crop_dims(self.dims)

    @cached_property
    def outer_dims(self) -> DimensionsWithWidthAndHeight:
        """Return outer dimensions including title contribution.

        Returns:
            Width/height after combining cropped content and visible title
            lines, then applying frame height cropping rules.
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
        """Return frame available to panel content after title reservation.

        Returns:
            Frame with reduced height when title lines consume vertical space.
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
        """Return fitness summary of content dimensions vs. frame limits.

        Returns:
            ``DimensionsFit`` describing fit/cropping relationship.
        """
        return DimensionsFit(
            self.dims,
            self.inner_frame.dims,
            proportional_freedom=self.config.freedom,
        )

    def overly_cropped(self) -> bool:
        """Return whether width cropping violates configured minimum width.

        Returns:
            ``True`` when width is cropped below ``config.min_crop_width``.
        """
        width_cropped = self.dims.width > self.cropped_dims.width
        width_less_than_min_crop = self.cropped_dims.width < self.config.min_crop_width
        overly_cropped = width_cropped and width_less_than_min_crop
        return overly_cropped

    def width_missing_to_not_be_overly_cropped(self) -> pyd.NonNegativeInt:
        """Return additional width needed to avoid being overly cropped.

        Returns:
            Missing width to reach minimum crop width, or ``0`` when already
            acceptable.
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
        """Return whether title lines consume content area in the frame.

        Returns:
            ``True`` when available title space is less than one full title
            line.
        """
        if self._available_height_for_title is None:
            return False
        return self._available_height_for_title < SINGLE_LINE_TITLE_HEIGHT

    @cached_property
    def resized_title(self) -> list[str]:
        """Return title lines wrapped to fit frame/content constraints.

        Returns:
            Wrapped title lines respecting maximum visible title height.
        """
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
        """Return width of the widest visible title line.

        Returns:
            Maximum title-line width in characters.
        """
        return max((len(line) for line in self.resized_title), default=0)

    @cached_property
    def title_height(self) -> int:
        """Return number of visible title lines.

        Returns:
            Title line count capped by available title space.
        """
        return min(self._max_title_height, len(self.resized_title))

    @cached_property
    def title_height_with_blank_lines(self) -> int:
        """Return title height including configured blank spacer lines.

        Returns:
            Visible title height plus blank separator lines, or ``0`` when no
            title is shown.
        """
        return self.title_height + TITLE_BLANK_LINES if self.title_height > 0 else 0

    @abstractmethod
    @override
    def render_next_stage(self) -> 'FullyRenderedPanel[FrameT]':
        """Render this dimensions-aware panel to fully rendered stage.

        Returns:
            Fully rendered panel that can export output variants.
        """
        ...


class FullyRenderedPanel(DimensionsAwarePanel[FrameT], Generic[FrameT], ABC):
    """Panel stage that can export terminal and HTML output variants."""

    @override
    def render_next_stage(self) -> 'FullyRenderedPanel[FrameT]':
        """Raise because fully rendered panels are terminal in the pipeline.

        Returns:
            This method does not return; it always raises.

        Raises:
            NotImplementedError: Always, because no further render stage exists.
        """
        raise NotImplementedError('This panel is fully rendered.')

    @cached_property
    @abstractmethod
    def plain(self) -> OutputVariant:
        """Return plain-text output variant.

        Returns:
            Output variant without styling or color, cropped to frame bounds.
        """

    @cached_property
    @abstractmethod
    def bw_stylized(self) -> OutputVariant:
        """Return black-and-white stylized output variant.

        Returns:
            Output variant with text styling but no color, cropped to frame
            bounds.
        """

    @cached_property
    @abstractmethod
    def colorized(self) -> OutputVariant:
        """Return full-color stylized output variant.

        Returns:
            Output variant with color and style, cropped to frame bounds.
        """
