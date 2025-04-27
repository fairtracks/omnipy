from abc import ABC, abstractmethod
from functools import cached_property
from typing import ClassVar, Generic

from omnipy.data._display.dimensions import Dimensions, has_width_and_height
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

    @cached_property
    def _width(self) -> pyd.NonNegativeInt:
        def _line_len(line: str) -> int:
            tab_size = self.config.tab_size
            line_len = 0
            for c in line:
                if c == '\t':
                    line_len += tab_size - (line_len % tab_size)
                else:
                    line_len += self._char_width_map[c]
            return line_len

        return max((_line_len(line) for line in self._content_lines), default=0)

    @cached_property
    def _height(self) -> pyd.NonNegativeInt:
        return max(0, len(self._content_lines))

    @cached_property
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return Dimensions(width=self._width, height=self._height)


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
