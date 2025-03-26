from abc import ABC, abstractmethod
from dataclasses import asdict
import re
from typing import cast

from devtools import PrettyFormat
import rich.pretty

from omnipy.data._display.config import MAX_TERMINAL_SIZE, PrettyPrinterLib
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions, Proportionally
from omnipy.data._display.frame import Frame, frame_has_width, FrameWithWidth
from omnipy.data._display.panel.base import FrameT
from omnipy.data._display.panel.draft import DraftPanel, ReflowedTextDraftPanel
from omnipy.data.typechecks import is_model_instance
import omnipy.util._pydantic as pyd


class PrettyPrinter(ABC):
    @abstractmethod
    def no_width_change_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        pass

    def prepare_draft_for_print_with_reduced_width_requirements(
        self,
        draft_panel: DraftPanel[object, FrameT],
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> DraftPanel[object, FrameWithWidth]:
        new_frame = self._calculate_frame_with_reduced_width(reflowed_text_panel)
        new_constraints = self._calculate_constraints_with_reduced_width(reflowed_text_panel)
        return DraftPanel(
            draft_panel.content,
            frame=new_frame,
            constraints=new_constraints,
            config=draft_panel.config,
        )

    @abstractmethod
    def _calculate_frame_with_reduced_width(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> FrameWithWidth:
        pass

    @abstractmethod
    def _calculate_constraints_with_reduced_width(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        pass

    def print_draft(
        self,
        draft_panel: DraftPanel[object, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel(
            self.print_draft_to_str(draft_panel),
            frame=draft_panel.frame,
            constraints=draft_panel.constraints,
            config=draft_panel.config,
        )

    @abstractmethod
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        pass


class RichPrettyPrinter(PrettyPrinter):
    def __init__(self) -> None:
        self._prev_reflowed_text_panel_width: pyd.NonNegativeInt | None = None

    def no_width_change_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        if self._prev_reflowed_text_panel_width is None:
            return False
        else:
            return self._prev_reflowed_text_panel_width <= reflowed_text_panel.dims.width

    def _calculate_frame_with_reduced_width(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> FrameWithWidth:
        self._prev_reflowed_text_panel_width = reflowed_text_panel.dims.width

        if reflowed_text_panel.dims.height == 1:
            frame_width = reflowed_text_panel.dims.width - 2
        else:
            frame_width = reflowed_text_panel.dims.width - 1

        return Frame(Dimensions(width=frame_width, height=reflowed_text_panel.frame.dims.height))

    def _calculate_constraints_with_reduced_width(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        return reflowed_text_panel.constraints

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
    def __init__(self) -> None:
        self._prev_reflowed_text_panel_width: pyd.NonNegativeInt | None = None
        self._prev_max_container_width: pyd.NonNegativeInt | None = None

    def no_width_change_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        if self._prev_reflowed_text_panel_width is None or self._prev_max_container_width is None:
            return False
        else:
            # Sanity check
            assert self._prev_reflowed_text_panel_width is not None
            assert self._prev_max_container_width is not None

            return ((self._prev_reflowed_text_panel_width <= reflowed_text_panel.dims.width)
                    and (self._prev_max_container_width
                         <= reflowed_text_panel.max_container_width_across_lines))

    def _calculate_frame_with_reduced_width(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> FrameWithWidth:
        self._prev_reflowed_text_panel_width = reflowed_text_panel.dims.width

        return Frame(
            Dimensions(
                width=reflowed_text_panel.dims.width - 1,
                height=reflowed_text_panel.frame.dims.height,
            ))

    def _calculate_constraints_with_reduced_width(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        self._prev_max_container_width = reflowed_text_panel.max_container_width_across_lines

        prev_constraints_kwargs = asdict(reflowed_text_panel.constraints)
        prev_constraints_kwargs['container_width_per_line_limit'] = \
            max(reflowed_text_panel.max_container_width_across_lines - 1, 0)
        return Constraints(**prev_constraints_kwargs)

    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
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

        if pretty_printer.no_width_change_since_last_print(cur_reflowed_text_panel):
            break

        draft_for_print: DraftPanel[object, FrameWithWidth] = \
            pretty_printer.prepare_draft_for_print_with_reduced_width_requirements(
                draft_panel,
                cur_reflowed_text_panel,
        )

        # To maintain original frame and constraints
        cur_reflowed_text_panel = ReflowedTextDraftPanel(
            pretty_printer.print_draft_to_str(draft_for_print),
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
        data, frame=in_draft.frame, config=in_draft.config)
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
