from abc import ABC, abstractmethod
from functools import cached_property
from typing import ClassVar, Generic

from omnipy.data._display.dimensions import Dimensions
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
