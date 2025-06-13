from functools import cached_property
import re
from typing import Generic

from typing_extensions import override

from omnipy.data._display.constraints import ConstraintsSatisfaction
from omnipy.data._display.panel.base import FrameT, FullyRenderedPanel
from omnipy.data._display.panel.cropping import (crop_content_lines_vertically_for_resizing,
                                                 crop_content_with_extra_wide_chars)
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import split_all_content_to_lines, strip_newlines


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ReflowedTextDraftPanel(
        MonospacedDraftPanel[str, FrameT],
        Generic[FrameT],
):
    @cached_property
    def _content_lines(self) -> list[str]:
        content_lines = split_all_content_to_lines(self.content)
        content_lines = crop_content_lines_vertically_for_resizing(
            content_lines,
            self.frame,
            self.config.vertical_overflow_mode,
        )
        content_lines = crop_content_with_extra_wide_chars(
            content_lines,
            self.frame,
            self.config,
            self._char_width_map,
        )
        return strip_newlines(content_lines)

    @cached_property
    def max_container_width_across_lines(self) -> int:
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

    @override
    def render_next_stage(self) -> 'FullyRenderedPanel[FrameT]':
        from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
        panel: SyntaxStylizedTextPanel[FrameT] = SyntaxStylizedTextPanel(self)
        return panel
