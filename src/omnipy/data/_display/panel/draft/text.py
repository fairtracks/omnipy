from functools import cached_property
import re
from typing import Generic, Iterator, overload

from typing_extensions import override

from omnipy.data._display.constraints import ConstraintsSatisfaction
from omnipy.data._display.dimensions import Dimensions, DimensionsFit, has_height
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.panel.base import FullyRenderedPanel
from omnipy.data._display.panel.cropping import (crop_content_lines_vertically_for_resizing,
                                                 crop_content_with_extra_wide_chars)
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.monospaced import MonospacedDraftPanel
from omnipy.data._display.panel.typedefs import FrameInvT, FrameT
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import split_all_content_to_lines, strip_newlines

_INNER_DICT_OR_LIST_REGEXP = re.compile(r'(\{[^\{\}\[\]]*\}|\[[^\{\}\[\]]*\])')


@pyd.dataclass(
    init=False, frozen=True, config=pyd.ConfigDict(extra=pyd.Extra.forbid, validate_all=True))
class ReflowedTextDraftPanel(
        MonospacedDraftPanel[str, FrameT],
        Generic[FrameT],
):
    @classmethod
    @overload
    def create_from_draft_panel(
        cls,
        draft_panel: DraftPanel[str, FrameInvT],
        other_content: None = None,
    ) -> 'ReflowedTextDraftPanel[FrameInvT]':
        ...

    @classmethod
    @overload
    def create_from_draft_panel(
        cls,
        draft_panel: DraftPanel[object, FrameInvT],
        other_content: str,
    ) -> 'ReflowedTextDraftPanel[FrameInvT]':
        ...

    @classmethod
    def create_from_draft_panel(
        cls,
        draft_panel: DraftPanel[str | object, FrameInvT],
        other_content: str | None = None,
    ) -> 'ReflowedTextDraftPanel[FrameInvT]':
        content = (draft_panel.content if other_content is None else other_content)
        return ReflowedTextDraftPanel(
            content,  # type: ignore[arg-type]
            title=draft_panel.title,
            frame=draft_panel.frame,
            constraints=draft_panel.constraints,
            config=draft_panel.config,
        )

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
            'cropped_dims',
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
            'cropped_dims',
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
            self.config.v_overflow,
        )
        content_lines = crop_content_with_extra_wide_chars(
            content_lines,
            frame,
            self.config,
            self._char_width_map,
        )
        return strip_newlines(content_lines)

    @cached_property
    def orig_dims(self) -> Dimensions[pyd.NonNegativeInt, pyd.NonNegativeInt]:
        """
        Original dimensions of the panel, without any cropping applied.
        This is used to determine the original size of the content before
        any transformations or cropping.
        """
        orig_content_lines = strip_newlines(split_all_content_to_lines(self.content))
        orig_width = max((self._line_width(line) for line in orig_content_lines), default=0)
        orig_height = len(orig_content_lines)
        return Dimensions(width=orig_width, height=orig_height)

    @cached_property
    @override
    def within_frame(self) -> DimensionsFit:
        """
        Returns a summary of how well the panel's content fit within the
        frame's dimensions (minus the title height, if any).

        Overrides the base class method to ensure that the fitness is
        calculated based on the dimensions of the original, non-cropped
        content.
        """
        return DimensionsFit(
            self.orig_dims,
            self.inner_frame.dims,
            proportional_freedom=self.config.freedom,
        )

    @cached_property
    def max_inline_container_width_incl(self) -> int:
        def _max_inline_container_width_incl_for_line(line):
            # Find all containers in the line using regex
            containers = re.findall(r'\{.*\}|\[.*\]|\(.*\)', line)
            # Return the length of the longest container, or 0 if none are found
            return max((len(container) for container in containers), default=0)

        # Calculate the maximum (inclusive) inline container width across all lines
        return max(
            (_max_inline_container_width_incl_for_line(line) for line in self._content_lines),
            default=0)

    @cached_property
    def max_inline_list_or_dict_width_excl(self) -> int:  # noqa: C901
        inline_list_or_dict_widths = []
        line_iter = iter(self._content_lines)

        try:
            end_of_multiline_char = ''
            while True:
                line = next(line_iter).strip()

                if line.endswith('['):
                    # Start of a multiline list, wait for the closing bracket
                    end_of_multiline_char = ']'
                elif line.endswith('{'):
                    # Start of a multiline dict, wait for the closing brace
                    end_of_multiline_char = '}'
                elif end_of_multiline_char:
                    # We are in a multiline context

                    if line.startswith('"'):
                        line_copy = line
                        while True:
                            inner_dict_or_lists = re.findall(_INNER_DICT_OR_LIST_REGEXP, line_copy)
                            if not inner_dict_or_lists:
                                # No more inner dicts or lists found, break the loop
                                break
                            for inner_dict_or_list in inner_dict_or_lists:
                                line_copy = line_copy.replace(inner_dict_or_list, '')

                        if line_copy.count(':') == 1:
                            # Single dict element in a multiline context
                            # Only consider the width of the value part
                            value_part = line.split(':', 1)[-1].strip()
                            inline_list_or_dict_widths.append(len(value_part.rstrip(',')))
                            continue
                    if line.startswith(end_of_multiline_char):
                        # End character found, reset end_of_multiline_char
                        # to signal that we are no longer in a multiline
                        # context
                        end_of_multiline_char = ''
                        # However, we still need to check the line for
                        # potential start of a new inline list or dict
                    else:
                        # If we are still in a multiline context, we
                        # add the length of the full line to the widths
                        inline_list_or_dict_widths.append(len(line.rstrip(',')))
                        continue
                elif ((line.startswith('{') and line.endswith('}'))
                      or (line.startswith('[') and line.endswith(']'))):
                    # If the line is a dict or list, we add the width of the
                    # line, excluding the outer braces/brackets
                    inline_list_or_dict_widths.append(len(line[1:-1].strip()))
                    continue
                else:
                    # Check skipped lines if algorithm does not work
                    # End of multiline contexts will also end up here, so
                    # look for other things
                    pass

        except StopIteration:
            pass

        return max(inline_list_or_dict_widths, default=0)

    @cached_property
    def satisfies(self) -> ConstraintsSatisfaction:  # pyright: ignore
        return ConstraintsSatisfaction(
            self.constraints,
            max_inline_container_width_incl=self.max_inline_container_width_incl,
            max_inline_list_or_dict_width_excl=self.max_inline_list_or_dict_width_excl,
        )

    @override
    def render_next_stage(self) -> 'FullyRenderedPanel[FrameT]':
        from omnipy.data._display.panel.styling.text import SyntaxStylizedTextPanel
        panel: SyntaxStylizedTextPanel[FrameT] = SyntaxStylizedTextPanel(self)
        return panel
