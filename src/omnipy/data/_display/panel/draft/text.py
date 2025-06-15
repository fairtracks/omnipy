from functools import cached_property
import re
from typing import Generic, Iterator

from typing_extensions import override

from omnipy.data._display.constraints import ConstraintsSatisfaction
from omnipy.data._display.dimensions import Dimensions, has_height
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.base import FrameInvT, FrameT, FullyRenderedPanel
from omnipy.data._display.panel.cropping import (crop_content_lines_vertically_for_resizing,
                                                 crop_content_with_extra_wide_chars)
from omnipy.data._display.panel.draft.base import DimensionsAwareDraftPanel, DraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import split_all_content_to_lines, strip_newlines


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class TextDraftPanel(
        DraftPanel[str, FrameT],
        Generic[FrameT],
):
    @override
    def render_next_stage(self) -> 'DimensionsAwareDraftPanel[str, FrameT]':
        from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
        return ReflowedTextDraftPanel.create_from_draft_panel(self)


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ReflowedTextDraftPanel(
        MonospacedDraftPanel[str, FrameT],
        Generic[FrameT],
):
    @classmethod
    def create_from_draft_panel(
        cls,
        draft_panel: DraftPanel[str, FrameInvT],
    ) -> 'ReflowedTextDraftPanel[FrameInvT]':
        resized_panel: ReflowedTextDraftPanel[FrameInvT] = ReflowedTextDraftPanel(
            draft_panel.content,
            title=draft_panel.title,
            frame=draft_panel.frame,
            constraints=draft_panel.constraints,
            config=draft_panel.config,
        )
        return resized_panel

    @cached_property
    def _content_lines_generator(self) -> Iterator[list[str]]:
        """
        Helper method to calculate dimensions, where the first calculation
        does not take title height into account, while all subsequent
        calculations do.
        :return: Generator providing content lines
        """
        yield self._split_and_crop_content_lines(self.frame)

        if has_height(self.frame.dims):
            crop_frame = self.frame.modified_copy(
                height=(self.frame.dims.height - self.title_height_with_blank_lines))
        else:
            crop_frame = self.frame
        content_lines = self._split_and_crop_content_lines(crop_frame)

        while True:
            yield content_lines

    @cached_property
    @override
    def _content_lines(self) -> list[str]:
        return next(self._content_lines_generator)

    @cached_property
    @override
    def dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        def _del_attrs_if_defined(*attrs: str):
            for attr in attrs:
                try:
                    object.__delattr__(self, attr)
                except AttributeError:
                    pass

        # Ensure eventual cached values used to calculate dims are deleted
        _del_attrs_if_defined(
            '_content_lines_generator',
            'dims',
            '_width',
            '_height',
            '_content_lines',
        )

        # Calculate dimensions and cache in self.dims
        dims = super().dims
        self.__dict__['dims'] = dims

        # Calculate title_height_with_blank_lines and cache it,
        # making use of the initial content lines that do not
        # take title height into account (otherwise, a circular
        # dependency would occur)
        self.title_height_with_blank_lines

        # Delete cached values, expect for "_content_lines_generator"
        _del_attrs_if_defined(
            'dims',
            '_width',
            '_height',
            '_content_lines',
        )

        # Re-calculate dimensions, now taking the title height into account
        return super().dims

    def _split_and_crop_content_lines(self, frame: AnyFrame):
        content_lines = split_all_content_to_lines(self.content)
        content_lines = crop_content_lines_vertically_for_resizing(
            content_lines,
            frame,
            self.config.vertical_overflow_mode,
        )
        content_lines = crop_content_with_extra_wide_chars(
            content_lines,
            frame,
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
