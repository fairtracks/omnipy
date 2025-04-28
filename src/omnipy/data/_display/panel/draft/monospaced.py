from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import ClassVar, Generic

from omnipy.data._display.config import HorizontalOverflowMode, OutputConfig
from omnipy.data._display.dimensions import Dimensions, has_width, has_width_and_height
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.helpers import UnicodeCharWidthMap
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT
from omnipy.data._display.panel.draft.base import ContentT, DraftPanel
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class MonospacedDraftPanel(
        DimensionsAwarePanel[FrameT],
        DraftPanel[ContentT, FrameT],
        Generic[ContentT, FrameT],
        ABC,
):
    _char_width_map: ClassVar[UnicodeCharWidthMap] = UnicodeCharWidthMap()

    @cached_property
    @abstractmethod
    def _content_lines(self) -> list[str]:
        ...

    def _line_width(self, line):
        stats = _calc_line_stats(
            line,
            self.config.tab_size,
            self._char_width_map,
        )
        return stats.line_width

    @cached_property
    def _width(self) -> pyd.NonNegativeInt:
        return max((self._line_width(line) for line in self._content_lines), default=0)

    @cached_property
    def _height(self) -> pyd.NonNegativeInt:
        return max(0, len(self._content_lines))

    @cached_property
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return Dimensions(width=self._width, height=self._height)


@dataclass
class LineStats:
    line_width: pyd.NonNegativeInt = 0
    char_count: pyd.NonNegativeInt = 0
    overflow: bool = False

    def register_char(self, char_width: pyd.NonNegativeInt):
        self.line_width += char_width
        self.char_count += 1


@lru_cache(maxsize=4096)
def _calc_line_stats(
    line: str,
    tab_size: int,
    char_width_map: UnicodeCharWidthMap,
    width_limit: pyd.NonNegativeInt | None = None,
) -> LineStats:
    if char_width_map.only_single_width_chars(line):
        return LineStats(
            line_width=len(line),
            char_count=len(line),
        )
    else:
        stats = LineStats()
        for ch in line:
            if ch == '\t':
                char_width = tab_size - (stats.line_width % tab_size)
            else:
                char_width = char_width_map[ch]

            if width_limit is not None:
                if stats.line_width + char_width > width_limit:
                    stats.overflow = True
                    return stats

            stats.register_char(char_width)

        return stats


def crop_content_lines_for_resizing(
    all_content_lines: list[str],
    frame: AnyFrame,
) -> list[str]:
    # If both frame dimensions are specified, the frame height is less
    # than the number of lines, the frame width is defined as
    # flexible (False), AND the frame height is defined as fixed,
    # then we need to crop the content to fit the frame so that the width of
    # the panel can be reduced to fit only what is in the frame. Otherwise
    # (and the default) is that the panel is wide enough to support the
    # maximum width over all lines, also those out of frame.
    #
    # TODO: Add support for scrolling of text content, not just
    #       cropping from bottom

    if has_width_and_height(frame.dims) \
            and frame.fixed_width is False \
            and frame.fixed_height is True \
            and frame.dims.width > 0 \
            and frame.dims.height < len(all_content_lines):
        return all_content_lines[:frame.dims.height]

    return all_content_lines


def crop_content_with_extra_wide_chars(
    all_content_lines: list[str],
    frame: AnyFrame,
    config: OutputConfig,
    char_width_map: UnicodeCharWidthMap,
) -> list[str]:
    if has_width(frame.dims) \
            and frame.fixed_width is False \
            and frame.dims.width > 0:

        ellipsis_if_overflow = config.horizontal_overflow_mode == HorizontalOverflowMode.ELLIPSIS

        for i, line in enumerate(all_content_lines):
            stats = _calc_line_stats(
                line,
                config.tab_size,
                char_width_map,
                width_limit=frame.dims.width,
            )

            cropped_line = line[:stats.char_count]

            if stats.overflow and ellipsis_if_overflow:
                if stats.line_width == frame.dims.width > 0:
                    # Exactly at the limit, must remove the last character
                    # to have space for the ellipsis
                    cropped_line = cropped_line[:-1]
                cropped_line += '…'

            cropped_line = cropped_line.rstrip('\t')

            all_content_lines[i] = cropped_line

    return all_content_lines
