from typing import cast

from cachebox import cached, FIFOCache

from omnipy.data._display.dimensions import Proportionally
from omnipy.data._display.frame import frame_has_width, FrameWithWidth
from omnipy.data._display.panel.draft.base import DraftPanel
from omnipy.data._display.panel.draft.text import ReflowedTextDraftPanel
from omnipy.data._display.panel.typedefs import FrameT, OtherFrameT
from omnipy.data._display.text.pretty_printer.base import (PrettyPrinter,
                                                           StatsTighteningPrettyPrinter)


def pretty_repr_of_draft_output(
        in_draft_panel: DraftPanel[object, FrameT]) -> ReflowedTextDraftPanel[FrameT]:

    pretty_printer = PrettyPrinter.get_pretty_printer_for_draft_panel(in_draft_panel)
    orig_draft_content_id = id(in_draft_panel.content)
    draft_panel = pretty_printer.prepare_draft_panel(in_draft_panel)
    formatted_draft_panel = pretty_printer.format_prepared_draft(draft_panel)
    if frame_has_width(formatted_draft_panel.frame):
        reflowed_text_panel = cast(ReflowedTextDraftPanel[FrameWithWidth], formatted_draft_panel)
        if (isinstance(pretty_printer, StatsTighteningPrettyPrinter)
                and _should_reduce_width(reflowed_text_panel)):
            return _iteratively_reduce_width(
                pretty_printer=pretty_printer,
                draft_panel=draft_panel,
                cur_reflowed_text_panel=reflowed_text_panel,
                orig_draft_content_id=orig_draft_content_id,
                should_follow_proportionality=_should_follow_proportionality(reflowed_text_panel),
            )

    return formatted_draft_panel


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


def _iteratively_reduce_width(
    pretty_printer: StatsTighteningPrettyPrinter[object],
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

        draft_for_format = pretty_printer.prepare_draft_for_print_with_tightened_stat_reqs(
            draft_panel,
            cur_reflowed_text_panel,
        )

        if not pretty_printer.stats_tightened_since_last_print(
                draft_for_format,
                cur_reflowed_text_panel,
        ):
            break

        prev_reflowed_text_panel = cur_reflowed_text_panel

        cur_reflowed_text_panel = _format_draft_panel(
            orig_draft_content_id=orig_draft_content_id,
            pretty_printer=pretty_printer,
            draft_for_format=draft_for_format,
            cur_reflowed_text_panel=cur_reflowed_text_panel)

    # Even though FrameT is FrameWithWidth at this point, static type checkers don't know that
    return cast(ReflowedTextDraftPanel[FrameT], cur_reflowed_text_panel)


def _unique_format_params_key_maker(_args, kwargs):
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


@cached(FIFOCache(maxsize=512), key_maker=_unique_format_params_key_maker)
def _format_draft_panel(
    *,
    pretty_printer: StatsTighteningPrettyPrinter,
    orig_draft_content_id: int,  # Only used for generating unique cache keys
    draft_for_format: DraftPanel[object, FrameT],
    cur_reflowed_text_panel: ReflowedTextDraftPanel[OtherFrameT],
) -> ReflowedTextDraftPanel[OtherFrameT]:
    return ReflowedTextDraftPanel.create_from_draft_panel(
        cur_reflowed_text_panel,
        other_content=pretty_printer.print_draft_to_str(draft_for_format),
    )
