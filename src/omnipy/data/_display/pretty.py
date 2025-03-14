from abc import ABC, abstractmethod
from dataclasses import asdict
import re
from typing import cast

from devtools import PrettyFormat
from rich.pretty import pretty_repr as rich_pretty_repr

from omnipy.data._display.config import MAX_TERMINAL_SIZE, PrettyPrinterLib
from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import Dimensions, Proportionally
from omnipy.data._display.frame import Frame, frame_has_width, FrameWithWidth
from omnipy.data._display.panel import DraftMonospacedOutput, DraftOutput, FrameT
from omnipy.data.typechecks import is_model_instance
from omnipy.util._pydantic import NonNegativeInt


class PrettyPrinter(ABC):
    @abstractmethod
    def no_width_change_since_last_print(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> bool:
        pass

    def prepare_draft_for_print_with_reduced_width_requirements(
        self,
        draft: DraftOutput[object, FrameT],
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> DraftOutput[object, FrameWithWidth]:
        new_frame = self._calculate_frame_with_reduced_width(mono_draft)
        new_constraints = self._calculate_constraints_with_reduced_width(mono_draft)
        return DraftOutput(
            draft.content,
            frame=new_frame,
            constraints=new_constraints,
            config=draft.config,
        )

    @abstractmethod
    def _calculate_frame_with_reduced_width(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> FrameWithWidth:
        pass

    @abstractmethod
    def _calculate_constraints_with_reduced_width(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> Constraints:
        pass

    def print_draft(
        self,
        draft: DraftOutput[object, FrameT],
    ) -> DraftMonospacedOutput[FrameT]:
        return DraftMonospacedOutput(
            self.print_draft_to_str(draft),
            frame=draft.frame,
            constraints=draft.constraints,
            config=draft.config,
        )

    @abstractmethod
    def print_draft_to_str(self, draft: DraftOutput[object, FrameT]) -> str:
        pass


class RichPrettyPrinter(PrettyPrinter):
    def __init__(self) -> None:
        self._prev_mono_draft_width: NonNegativeInt | None = None

    def no_width_change_since_last_print(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> bool:
        if self._prev_mono_draft_width is None:
            return False
        else:
            return self._prev_mono_draft_width <= mono_draft.dims.width

    def _calculate_frame_with_reduced_width(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> FrameWithWidth:
        self._prev_mono_draft_width = mono_draft.dims.width

        if mono_draft.dims.height == 1:
            frame_width = mono_draft.dims.width - 2
        else:
            frame_width = mono_draft.dims.width - 1

        return Frame(Dimensions(width=frame_width, height=mono_draft.frame.dims.height))

    def _calculate_constraints_with_reduced_width(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> Constraints:
        return mono_draft.constraints

    def print_draft_to_str(self, draft: DraftOutput[object, FrameT]) -> str:
        if draft.frame.dims.width is not None:
            max_width = draft.frame.dims.width + 1
        else:
            max_width = MAX_TERMINAL_SIZE

        return rich_pretty_repr(
            draft.content,
            indent_size=draft.config.indent_tab_size,
            max_width=max_width,
        )


class DevtoolsPrettyPrinter(PrettyPrinter):
    def __init__(self) -> None:
        self._prev_mono_draft_width: NonNegativeInt | None = None
        self._prev_max_container_width: NonNegativeInt | None = None

    def no_width_change_since_last_print(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> bool:
        if self._prev_mono_draft_width is None or self._prev_max_container_width is None:
            return False
        else:
            # Sanity check
            assert self._prev_mono_draft_width is not None
            assert self._prev_max_container_width is not None

            return self._prev_mono_draft_width <= mono_draft.dims.width \
                and self._prev_max_container_width <= mono_draft.max_container_width_across_lines

    def _calculate_frame_with_reduced_width(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> FrameWithWidth:
        self._prev_mono_draft_width = mono_draft.dims.width

        return Frame(
            Dimensions(
                width=mono_draft.dims.width - 1,
                height=mono_draft.frame.dims.height,
            ))

    def _calculate_constraints_with_reduced_width(
        self,
        mono_draft: DraftMonospacedOutput[FrameWithWidth],
    ) -> Constraints:
        self._prev_max_container_width = mono_draft.max_container_width_across_lines

        prev_constraints_kwargs = asdict(mono_draft.constraints)
        prev_constraints_kwargs['container_width_per_line_limit'] = \
            max(mono_draft.max_container_width_across_lines - 1, 0)
        return Constraints(**prev_constraints_kwargs)

    def print_draft_to_str(self, draft: DraftOutput[object, FrameT]) -> str:
        if draft.constraints.container_width_per_line_limit is not None:
            simple_cutoff = draft.constraints.container_width_per_line_limit
        else:
            simple_cutoff = MAX_TERMINAL_SIZE

        if draft.frame.dims.width is not None:
            width = draft.frame.dims.width + 1
        else:
            width = MAX_TERMINAL_SIZE

        while True:
            pf = PrettyFormat(
                indent_step=draft.config.indent_tab_size,
                simple_cutoff=simple_cutoff,
                width=width,
            )

            try:
                return pf(draft.content)
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
    draft: DraftOutput[object, FrameT],
    cur_mono_draft: DraftMonospacedOutput[FrameWithWidth],
) -> DraftMonospacedOutput[FrameT]:

    while True:
        fit = cur_mono_draft.within_frame
        if fit.width and fit.proportionality is not Proportionally.WIDER:
            break

        if pretty_printer.no_width_change_since_last_print(cur_mono_draft):
            break

        draft_for_print: DraftOutput[object, FrameWithWidth] = \
            pretty_printer.prepare_draft_for_print_with_reduced_width_requirements(
                draft,
                cur_mono_draft,
        )

        # To maintain original frame and constraints
        cur_mono_draft = DraftMonospacedOutput(
            pretty_printer.print_draft_to_str(draft_for_print),
            frame=cur_mono_draft.frame,
            constraints=cur_mono_draft.constraints,
            config=cur_mono_draft.config,
        )

    # Even though FrameT is FrameWithWidth at this point, static type checkers don't know that
    return cast(DraftMonospacedOutput[FrameT], cur_mono_draft)


def _get_pretty_printer(draft: DraftOutput[object, FrameT]) -> PrettyPrinter:
    match draft.config.pretty_printer:
        case PrettyPrinterLib.RICH:
            return RichPrettyPrinter()
        case PrettyPrinterLib.DEVTOOLS:
            return DevtoolsPrettyPrinter()


def _prepare_content(in_draft: DraftOutput[object, FrameT]) -> DraftOutput[object, FrameT]:
    if is_model_instance(in_draft.content) and not in_draft.config.debug_mode:
        data = in_draft.content.to_data()
    else:
        data = in_draft.content
    draft = DraftOutput(data, frame=in_draft.frame, config=in_draft.config)
    return draft


def _should_adjust(
    draft: DraftOutput[object, FrameT],
    mono_draft: DraftMonospacedOutput[FrameWithWidth],
) -> bool:
    if mono_draft.within_frame.height is False:
        return False
    return not mono_draft.within_frame.width or _is_nested_structure(draft)


def _is_nested_structure(draft: DraftOutput[object, FrameT]) -> bool:
    def _any_abbrev_containers(repr_str: str) -> bool:
        return bool(re.search(r'\[...\]|\(...\)|\{...\}', repr_str))

    only_1st_level_repr = rich_pretty_repr(draft.content, max_depth=1)
    if _any_abbrev_containers(only_1st_level_repr):
        return True
    return False


def pretty_repr_of_draft_output(
        in_draft: DraftOutput[object, FrameT]) -> DraftMonospacedOutput[FrameT]:

    pretty_printer = _get_pretty_printer(in_draft)
    draft = _prepare_content(in_draft)
    printed_draft = pretty_printer.print_draft(draft)

    if frame_has_width(printed_draft.frame):
        mono_draft = cast(DraftMonospacedOutput[FrameWithWidth], printed_draft)
        if _should_adjust(draft, mono_draft):
            return _reduce_width_until_proportional_with_frame(pretty_printer, draft, mono_draft)

    return printed_draft
