"""Draft panel base classes for monospaced text-based display content."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Generic

from typing_extensions import override

from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.helpers import char_cell_width, only_single_width_chars
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.typedefs import ContentT, FrameT
from omnipy.shared.enums.display import MaxTitleHeight
import omnipy.util.pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True)
)
class MonospacedDraftPanel(
    DimensionsAwareDraftPanel[ContentT, FrameT],
    DraftPanel[ContentT, FrameT],
    Generic[ContentT, FrameT],
    ABC,
):
    """Dimensions-aware draft panel that measures monospaced text content."""

    @cached_property
    @abstractmethod
    def _content_lines(self) -> list[str]: ...

    def _line_width(self, line):
        stats = _calc_line_stats(
            line,
            self.config.tab,
        )
        return stats.line_width

    @cached_property
    def _width(self) -> pyd.NonNegativeInt:
        min_width = self.config.min_panel_width
        return max(
            (max(self._line_width(line), min_width) for line in self._content_lines),
            default=min_width,
        )

    @cached_property
    def _height(self) -> pyd.NonNegativeInt:
        return len(self._content_lines)

    @cached_property
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return Dimensions(width=self._width, height=self._height)

    @cached_property
    @override
    def _max_title_height(self) -> int:
        auto_title_height = super()._max_title_height

        match self.config.max_title_height:
            case MaxTitleHeight.AUTO:
                return auto_title_height
            case _:
                return int(self.config.max_title_height)


@dataclass
class LineStats:
    """Accumulated width, character count, and overflow state for one line."""

    line_width: int = 0
    char_count: int = 0
    overflow: bool = False

    def register_char(self, char_width: int):
        self.line_width += char_width
        self.char_count += 1


@lru_cache(maxsize=4096)
def _calc_line_stats(
    line: str,
    tab_size: int,
    width_limit: int | None = None,
) -> LineStats:
    if only_single_width_chars(line):
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
                char_width = char_cell_width(ch)

            if width_limit is not None:
                if stats.line_width + char_width > width_limit:
                    stats.overflow = True
                    return stats

            stats.register_char(char_width)

        return stats
