from abc import ABC, abstractmethod
import dataclasses
import re
from typing import cast

import rich.pretty
from typing_extensions import override

from omnipy.data._display.config import MAX_TERMINAL_SIZE
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import DimensionsWithWidth, Proportionally
from omnipy.data._display.frame import frame_has_width, FrameWithWidth
from omnipy.data._display.panel.base import FrameT
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.enums import PrettyPrinterLib
import omnipy.util._pydantic as pyd


class PrettyPrinter(ABC):
    def __init__(self) -> None:
        self._prev_frame_width: pyd.NonNegativeInt | None = None
        self._prev_constraints: Constraints | None = None
        self._prev_reflowed_text_panel_width: pyd.NonNegativeInt | None = None

    def width_reduced_since_last_print(
        self,
        draft_for_print: DraftPanel[object, FrameWithWidth],
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:

        if self._prev_frame_width is None:
            frame_width_reduced = True
        else:
            frame_width_reduced = (draft_for_print.frame.dims.width < self._prev_frame_width)

        if self._prev_reflowed_text_panel_width is None:
            dims_width_reduced = True
        else:
            dims_width_reduced = (
                reflowed_text_panel.dims.width < self._prev_reflowed_text_panel_width)

        self._prev_frame_width = draft_for_print.frame.dims.width
        self._prev_reflowed_text_panel_width = reflowed_text_panel.dims.width

        return frame_width_reduced and dims_width_reduced

    def constraints_tightened_since_last_print(
        self,
        draft_for_print: DraftPanel[object, FrameWithWidth],
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        reduced_constraints = self._constraints_tightened_since_last_print(reflowed_text_panel)

        self._prev_constraints = draft_for_print.constraints

        return reduced_constraints

    def _constraints_tightened_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        return False

    def prepare_draft_for_print_with_reduced_width_requirements(
        self,
        draft_panel: DraftPanel[object, FrameT],
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> DraftPanel[object, FrameWithWidth]:
        # For initial iteration, compare with frame of
        # cur_reflowed_text_panel provided as input
        if self._prev_frame_width is None:
            self._prev_frame_width = reflowed_text_panel.frame.dims.width

        new_frame = self._calc_frame_with_reduced_width(reflowed_text_panel)
        new_constraints = self._calc_tightened_constraints(reflowed_text_panel)
        return DraftPanel(
            draft_panel.content,
            title=draft_panel.title,
            frame=new_frame,
            constraints=new_constraints,
            config=draft_panel.config,
        )

    def _calc_frame_with_reduced_width(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> FrameWithWidth:
        new_frame_width = self._calc_reduced_frame_width(reflowed_text_panel.dims)
        return cast(FrameWithWidth, reflowed_text_panel.frame.modified_copy(width=new_frame_width))

    @abstractmethod
    def _calc_reduced_frame_width(
        self,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        pass

    def _calc_tightened_constraints(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        return reflowed_text_panel.constraints

    def print_draft(
        self,
        draft_panel: DraftPanel[object, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel(
            self.print_draft_to_str(draft_panel),
            title=draft_panel.title,
            frame=draft_panel.frame,
            constraints=draft_panel.constraints,
            config=draft_panel.config,
        )

    @abstractmethod
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        pass


class RichPrettyPrinter(PrettyPrinter):
    @override
    def _calc_reduced_frame_width(
        self,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        if cropped_panel_dims.height == 1:
            return cropped_panel_dims.width - 2
        else:
            return cropped_panel_dims.width - 1

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        if draft_panel.frame.dims.width is not None:
            max_width = draft_panel.frame.dims.width + 1
        else:
            max_width = MAX_TERMINAL_SIZE

        return rich.pretty.pretty_repr(
            draft_panel.content,
            indent_size=draft_panel.config.indent_tab_size,
            max_width=max_width,
        )


class DevtoolsPrettyPrinter(PrettyPrinter):
    @override
    def _constraints_tightened_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        if (self._prev_constraints is None
                or self._prev_constraints.container_width_per_line_limit is None):
            return True
        else:
            return (reflowed_text_panel.max_container_width_across_lines
                    < self._prev_constraints.container_width_per_line_limit)

    @override
    def _calc_reduced_frame_width(
        self,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        return cropped_panel_dims.width - 1

    @override
    def _calc_tightened_constraints(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        new_container_width_per_line_limit = max(
            reflowed_text_panel.max_container_width_across_lines - 1, 0)

        return dataclasses.replace(
            reflowed_text_panel.constraints,
            container_width_per_line_limit=new_container_width_per_line_limit,
        )

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        from devtools import PrettyFormat

        if draft_panel.constraints.container_width_per_line_limit is not None:
            simple_cutoff = draft_panel.constraints.container_width_per_line_limit
        else:
            simple_cutoff = MAX_TERMINAL_SIZE

        if draft_panel.frame.dims.width is not None:
            width = draft_panel.frame.dims.width + 1
        else:
            width = MAX_TERMINAL_SIZE

        while True:
            pf = PrettyFormat(
                indent_step=draft_panel.config.indent_tab_size,
                simple_cutoff=simple_cutoff,
                width=width,
            )

            try:
                return pf(draft_panel.content)
            except ValueError as e:
                text_match = re.search(r'invalid width (-?\d+)', str(e))

                if text_match:
                    internal_width = int(text_match.group(1))
                    delta_width = -internal_width + 1
                    simple_cutoff += delta_width
                    width += delta_width
                    continue

                if re.search(r'range\(\) arg 3 must not be zero', str(e)):
                    simple_cutoff += 1
                    width += 1
                    continue
                raise


def _reduce_width_until_proportional_with_frame(
    pretty_printer: PrettyPrinter,
    draft_panel: DraftPanel[object, FrameT],
    cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
) -> ReflowedTextDraftPanel[FrameT]:

    while True:
        fit = cur_reflowed_text_panel.within_frame
        if fit.width and fit.proportionality is not Proportionally.WIDER:
            break

        draft_for_print: DraftPanel[object, FrameWithWidth] = \
            pretty_printer.prepare_draft_for_print_with_reduced_width_requirements(
                draft_panel,
                cur_reflowed_text_panel,
        )

        if not (pretty_printer.width_reduced_since_last_print(
                draft_for_print,
                cur_reflowed_text_panel,
        ) or pretty_printer.constraints_tightened_since_last_print(
                draft_for_print,
                cur_reflowed_text_panel,
        )):
            break

        # To maintain original frame and constraints
        cur_reflowed_text_panel = ReflowedTextDraftPanel(
            pretty_printer.print_draft_to_str(draft_for_print),
            title=cur_reflowed_text_panel.title,
            frame=cur_reflowed_text_panel.frame,
            constraints=cur_reflowed_text_panel.constraints,
            config=cur_reflowed_text_panel.config,
        )

    # Even though FrameT is FrameWithWidth at this point, static type checkers don't know that
    return cast(ReflowedTextDraftPanel[FrameT], cur_reflowed_text_panel)


def _get_pretty_printer(draft_panel: DraftPanel[object, FrameT]) -> PrettyPrinter:
    match draft_panel.config.pretty_printer:
        case PrettyPrinterLib.RICH:
            return RichPrettyPrinter()
        case PrettyPrinterLib.DEVTOOLS:
            return DevtoolsPrettyPrinter()


def _prepare_content(in_draft: DraftPanel[object, FrameT]) -> DraftPanel[object, FrameT]:
    if is_model_instance(in_draft.content) and not in_draft.config.debug_mode:
        data = in_draft.content.to_data()
    else:
        data = in_draft.content
    draft_panel: DraftPanel[object, FrameT] = DraftPanel(
        data,
        title=in_draft.title,
        frame=in_draft.frame,
        constraints=in_draft.constraints,
        config=in_draft.config,
    )
    return draft_panel


def _should_adjust(
    draft_panel: DraftPanel[object, FrameT],
    reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
) -> bool:
    if reflowed_text_panel.within_frame.height is False:
        return False
    return not reflowed_text_panel.within_frame.width or _is_nested_structure(draft_panel)


def _is_nested_structure(draft_panel: DraftPanel[object, FrameT]) -> bool:
    def _any_abbrev_containers(repr_str: str) -> bool:
        return bool(re.search(r'\[...\]|\(...\)|\{...\}', repr_str))

    only_1st_level_repr = rich.pretty.pretty_repr(draft_panel.content, max_depth=1)
    if _any_abbrev_containers(only_1st_level_repr):
        return True
    return False


def pretty_repr_of_draft_output(
        in_draft_panel: DraftPanel[object, FrameT]) -> ReflowedTextDraftPanel[FrameT]:

    pretty_printer = _get_pretty_printer(in_draft_panel)
    draft_panel = _prepare_content(in_draft_panel)
    printed_draft_panel = pretty_printer.print_draft(draft_panel)

    if frame_has_width(printed_draft_panel.frame):
        reflowed_text_panel = cast(ReflowedTextDraftPanel[FrameWithWidth], printed_draft_panel)
        if _should_adjust(draft_panel, reflowed_text_panel):
            return _reduce_width_until_proportional_with_frame(pretty_printer,
                                                               draft_panel,
                                                               reflowed_text_panel)

    return printed_draft_panel
