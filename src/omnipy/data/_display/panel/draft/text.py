from functools import cached_property
import re
from typing import Generic

from typing_extensions import override

from omnipy.data._display.constraints import ConstraintsSatisfaction
from omnipy.data._display.panel.base import FrameT, FullyRenderedPanel
from omnipy.data._display.panel.draft.monospaced import (crop_content_lines_for_resizing,
                                                         crop_content_with_extra_wide_chars,
                                                         MonospacedDraftPanel)
import omnipy.util._pydantic as pyd


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ReflowedTextDraftPanel(
        MonospacedDraftPanel[str, FrameT],
        Generic[FrameT],
):
    @cached_property
    def _content_lines(self) -> list[str]:
        # Typical repr output should not end with newline. Hence, a regular split on newline is
        # correct behaviour. An empty string is the split into a list of one element. If
        # splitlines() had been used, the list would be empty.
        all_content_lines = self.content.split('\n')

        all_content_lines = crop_content_lines_for_resizing(
            all_content_lines,
            self.frame,
        )

        all_content_lines = crop_content_with_extra_wide_chars(
            all_content_lines,
            self.frame,
            self.config,
            self._char_width_map,
        )

        return all_content_lines

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
