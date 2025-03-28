from functools import cached_property
import re
from typing import ClassVar, Generic

from omnipy.data._display.constraints import ConstraintsSatisfaction
from omnipy.data._display.dimensions import Dimensions
from omnipy.data._display.helpers import UnicodeCharWidthMap
from omnipy.data._display.panel.base import DimensionsAwarePanel, FrameT
from omnipy.data._display.panel.draft.base import DraftPanel
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ReflowedTextDraftPanel(DimensionsAwarePanel[FrameT], DraftPanel[str, FrameT],
                             Generic[FrameT]):
    _char_width_map: ClassVar[UnicodeCharWidthMap] = UnicodeCharWidthMap()

    @cached_property
    def _content_lines(self) -> list[str]:
        return self.content.splitlines()

    @cached_property
    def _width(self) -> pyd.NonNegativeInt:
        def _line_len(line: str) -> int:
            return sum(self._char_width_map[c] for c in line)

        return max((_line_len(line) for line in self._content_lines), default=0)

    @cached_property
    def _height(self) -> pyd.NonNegativeInt:
        return len(self._content_lines)

    @cached_property
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        return Dimensions(width=self._width, height=self._height)

    @cached_property
    def max_container_width_across_lines(self) -> pyd.NonNegativeInt:
        def _max_container_width_in_line(line):
            # Find all containers in the line using regex
            containers = re.findall(r'\{.*\}|\[.*\]|\(.*\)', line)
            # Return the length of the longest container, or 0 if none are found
            return max((len(container) for container in containers), default=0)

        # Calculate the maximum container width across all lines
        return max((_max_container_width_in_line(line) for line in self._content_lines), default=0)

    @cached_property
    def satisfies(self) -> ConstraintsSatisfaction:  # pyright: ignore
        return ConstraintsSatisfaction(
            self.constraints,
            max_container_width_across_lines=self.max_container_width_across_lines,
        )
