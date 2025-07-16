from abc import ABC, abstractmethod
import dataclasses
import re
from typing import cast

from cachebox import cached, FIFOCache
import compact_json
import rich.pretty
from typing_extensions import override

from omnipy.data._display.constraints import Constraints
from omnipy.data._display.dimensions import DimensionsWithWidth, has_width, Proportionally
from omnipy.data._display.frame import frame_has_width, FrameWithWidth
from omnipy.data._display.panel.base import FrameT, OtherFrameT
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data.typechecks import is_model_instance
from omnipy.shared.constants import MAX_TERMINAL_SIZE, TERMINAL_DEFAULT_WIDTH
from omnipy.shared.enums.display import PrettyPrinterLib, SyntaxLanguage
import omnipy.util._pydantic as pyd


class PrettyPrinter(ABC):
    def __init__(self) -> None:
        self._prev_frame_width: pyd.NonNegativeInt | None = None
        self._prev_constraints: Constraints | None = None
        self._prev_reflowed_text_panel_width: pyd.NonNegativeInt | None = None

    def __hash__(self) -> int:
        _hash = hash((self.__class__,
                      self._prev_frame_width,
                      self._prev_constraints,
                      self._prev_reflowed_text_panel_width))
        return _hash

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
                reflowed_text_panel.orig_dims.width < self._prev_reflowed_text_panel_width)

        self._prev_frame_width = draft_for_print.frame.dims.width
        self._prev_reflowed_text_panel_width = reflowed_text_panel.orig_dims.width

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
        new_frame_width = self._calc_reduced_frame_width(reflowed_text_panel.orig_dims)
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

    def format_draft(
        self,
        draft_panel: DraftPanel[object, FrameT],
    ) -> ReflowedTextDraftPanel[FrameT]:
        return ReflowedTextDraftPanel.create_from_draft_panel(
            draft_panel,
            other_content=self.print_draft_to_str(draft_panel),
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
                or self._prev_constraints.max_inline_container_width_incl is None):
            return True
        else:
            return (reflowed_text_panel.max_inline_container_width_incl
                    < self._prev_constraints.max_inline_container_width_incl)

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
        new_max_inline_container_width_incl = max(
            reflowed_text_panel.max_inline_container_width_incl - 1, 0)

        return dataclasses.replace(
            reflowed_text_panel.constraints,
            max_inline_container_width_incl=new_max_inline_container_width_incl,
        )

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        from devtools import PrettyFormat

        if draft_panel.constraints.max_inline_container_width_incl is not None:
            simple_cutoff = draft_panel.constraints.max_inline_container_width_incl
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


class CompactJsonPrettyPrinter(PrettyPrinter):
    @override
    def _constraints_tightened_since_last_print(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> bool:
        if (self._prev_constraints is None
                or self._prev_constraints.max_inline_list_or_dict_width_excl is None):
            return True
        else:
            return (reflowed_text_panel.max_inline_list_or_dict_width_excl
                    < self._prev_constraints.max_inline_list_or_dict_width_excl)

    @override
    def _calc_reduced_frame_width(
        self,
        cropped_panel_dims: DimensionsWithWidth,
    ) -> pyd.NonNegativeInt:
        # Not really used, but just in case
        return cropped_panel_dims.width

    @override
    def _calc_tightened_constraints(
        self,
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    ) -> Constraints:
        new_max_inline_list_or_dict_width_excl = max(
            reflowed_text_panel.max_inline_list_or_dict_width_excl - 1, 0)

        return dataclasses.replace(
            reflowed_text_panel.constraints,
            max_inline_list_or_dict_width_excl=new_max_inline_list_or_dict_width_excl,
        )

    @override
    def print_draft_to_str(self, draft_panel: DraftPanel[object, FrameT]) -> str:
        max_inline_list_or_dict_width_excl = \
            draft_panel.constraints.max_inline_list_or_dict_width_excl
        if max_inline_list_or_dict_width_excl is not None:
            max_inline_length = max_inline_list_or_dict_width_excl
        elif has_width(draft_panel.frame.dims):
            max_inline_length = draft_panel.frame.dims.width
        else:
            max_inline_length = TERMINAL_DEFAULT_WIDTH

        json_formatter = compact_json.Formatter(
            max_inline_length=max_inline_length,
            max_inline_complexity=2,
            max_compact_list_complexity=2,
            simple_bracket_padding=True,
            indent_spaces=draft_panel.config.indent_tab_size,
            table_dict_minimum_similarity=90,
            table_list_minimum_similarity=90,
            dont_justify_numbers=True,
            ensure_ascii=False,
            east_asian_string_widths=True,
            multiline_compact_dict=False,
            omit_trailing_whitespace=True,
        )
        return json_formatter.serialize(draft_panel.content)  # pyright: ignore [reportArgumentType]


def _iteratively_reduce_width(
    pretty_printer: PrettyPrinter,
    draft_panel: DraftPanel[object, FrameT],
    cur_reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],
    orig_draft_content_id: int,
    should_follow_proportionality: bool,
) -> ReflowedTextDraftPanel[FrameT]:
    prev_reflowed_text_panel = None

    while True:
        fit = cur_reflowed_text_panel.within_frame

        # TODO: Refactor pretty printer loop exit logic into separate class or function
        if fit.width:
            if should_follow_proportionality:
                if fit.proportionality and fit.proportionality <= Proportionally.WIDER:
                    if (not fit.height and prev_reflowed_text_panel
                            and prev_reflowed_text_panel.within_frame.both):
                        cur_reflowed_text_panel = prev_reflowed_text_panel
                    break

            else:
                break

        draft_for_format: DraftPanel[object, FrameWithWidth] = \
            pretty_printer.prepare_draft_for_print_with_reduced_width_requirements(
                draft_panel,
                cur_reflowed_text_panel,
        )

        if not (pretty_printer.width_reduced_since_last_print(
                draft_for_format,
                cur_reflowed_text_panel,
        ) or pretty_printer.constraints_tightened_since_last_print(
                draft_for_format,
                cur_reflowed_text_panel,
        )):
            break

        prev_reflowed_text_panel = cur_reflowed_text_panel

        cur_reflowed_text_panel = _format_draft_panel(
            orig_draft_content_id=orig_draft_content_id,
            pretty_printer=pretty_printer,
            draft_for_format=draft_for_format,
            cur_reflowed_text_panel=cur_reflowed_text_panel)

    # Even though FrameT is FrameWithWidth at this point, static type checkers don't know that
    return cast(ReflowedTextDraftPanel[FrameT], cur_reflowed_text_panel)


def unique_format_params_key_maker(_args, kwargs):
    """A key maker for unique format parameters."""
    return hash((
        kwargs['pretty_printer'],
        kwargs['orig_draft_content_id'],
        kwargs['draft_for_format'].title,
        kwargs['draft_for_format'].frame,
        kwargs['draft_for_format'].constraints,
        kwargs['draft_for_format'].config,
        kwargs['cur_reflowed_text_panel'],
    ))


@cached(FIFOCache(maxsize=512), key_maker=unique_format_params_key_maker)
def _format_draft_panel(
    *,
    pretty_printer: PrettyPrinter,
    orig_draft_content_id: int,  # Only used for generating unique cache keys
    draft_for_format: DraftPanel[object, FrameT],
    cur_reflowed_text_panel: ReflowedTextDraftPanel[OtherFrameT],
) -> ReflowedTextDraftPanel[OtherFrameT]:
    return ReflowedTextDraftPanel.create_from_draft_panel(
        cur_reflowed_text_panel,
        other_content=pretty_printer.print_draft_to_str(draft_for_format),
    )


def _get_pretty_printer(draft_panel: DraftPanel[object, FrameT]) -> PrettyPrinter:
    match draft_panel.config.language:
        case SyntaxLanguage.JSON:
            return CompactJsonPrettyPrinter()
        case SyntaxLanguage.PYTHON:
            match draft_panel.config.pretty_printer:
                case PrettyPrinterLib.RICH:
                    return RichPrettyPrinter()
                case PrettyPrinterLib.DEVTOOLS:
                    return DevtoolsPrettyPrinter()
    raise ValueError(f'No pretty printer matching configured syntax language exist: '
                     f'{draft_panel.config.language}')


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


def _should_follow_proportionality(
        reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth]) -> bool:
    if reflowed_text_panel.frame.fixed_width:
        return False

    fit = reflowed_text_panel.within_frame

    return fit.proportionality is not None and fit.proportionality > Proportionally.WIDER


def _should_reduce_width(reflowed_text_panel: ReflowedTextDraftPanel[FrameWithWidth],) -> bool:
    fit = reflowed_text_panel.within_frame

    if fit.width is False:
        return True

    return _should_follow_proportionality(reflowed_text_panel)


def pretty_repr_of_draft_output(
        in_draft_panel: DraftPanel[object, FrameT]) -> ReflowedTextDraftPanel[FrameT]:

    pretty_printer = _get_pretty_printer(in_draft_panel)
    orig_draft_content_id = id(in_draft_panel.content)
    draft_panel = _prepare_content(in_draft_panel)
    formatted_draft_panel = pretty_printer.format_draft(draft_panel)

    if frame_has_width(formatted_draft_panel.frame):
        reflowed_text_panel = cast(ReflowedTextDraftPanel[FrameWithWidth], formatted_draft_panel)
        if _should_reduce_width(reflowed_text_panel):
            return _iteratively_reduce_width(
                pretty_printer=pretty_printer,
                draft_panel=draft_panel,
                cur_reflowed_text_panel=reflowed_text_panel,
                orig_draft_content_id=orig_draft_content_id,
                should_follow_proportionality=_should_follow_proportionality(reflowed_text_panel),
            )

    return formatted_draft_panel
