import re
from typing import NamedTuple

from devtools import PrettyFormat
from rich.pretty import pretty_repr as rich_pretty_repr

from omnipy.data._display.config import PrettyPrinterLib
from omnipy.data._display.draft import ContentT, DraftMonospacedOutput, DraftOutput, FrameT
from omnipy.data._display.frame import frame_has_width, frame_has_width_and_height, FrameWithWidth
from omnipy.data.typechecks import is_model_instance

MAX_WIDTH = 2**16 - 1


class ReprMeasures(NamedTuple):
    num_lines: int
    max_line_width: int
    max_container_width: int


def _any_abbrev_containers(repr_str: str) -> bool:
    return bool(re.search(r'\[...\]|\(...\)|\{...\}', repr_str))


def _is_nested_structure(draft: DraftOutput[ContentT, FrameT]) -> bool:
    only_1st_level_repr = rich_pretty_repr(draft.content, max_depth=1)
    if _any_abbrev_containers(only_1st_level_repr):
        return True
    return False


def _basic_pretty_repr(
    draft: DraftOutput[ContentT, FrameT],
    max_line_width: int | None,
    max_container_width: int | None,
) -> DraftMonospacedOutput[FrameT]:
    match draft.config.pretty_printer:
        case PrettyPrinterLib.RICH:
            if max_line_width is None:
                repr_str = rich_pretty_repr(
                    draft.content,
                    indent_size=draft.config.indent_tab_size,
                )
            else:
                repr_str = rich_pretty_repr(
                    draft.content,
                    indent_size=draft.config.indent_tab_size,
                    max_width=max_line_width + 1,
                )
        case PrettyPrinterLib.DEVTOOLS:
            if max_line_width is not None and max_container_width is not None:
                while True:
                    pf = PrettyFormat(
                        indent_step=draft.config.indent_tab_size,
                        simple_cutoff=max_container_width,
                        width=max_line_width + 1,
                    )
                    try:
                        repr_str = pf(draft.content)
                    except ValueError as e:
                        text_match = re.search(r'invalid width (-?\d+)', str(e))
                        if text_match:
                            internal_width = int(text_match.group(1))
                            delta_width = -internal_width + 1
                            max_line_width += delta_width
                            max_container_width += delta_width
                            continue
                        if re.search(r'range\(\) arg 3 must not be zero', str(e)):
                            max_line_width += 1
                            max_container_width += 1
                            continue
                        raise
                    break
            else:
                pf = PrettyFormat(
                    indent_step=draft.config.indent_tab_size,
                    simple_cutoff=MAX_WIDTH,
                    width=MAX_WIDTH,
                )
                repr_str = pf(draft.content)

    return DraftMonospacedOutput(
        repr_str,
        frame=draft.frame,
        config=draft.config,
    )


def _get_reflow_delta_line_width(pretty_printer: PrettyPrinterLib, height: int) -> int:
    """
    Return the number of characters to subtract from the max_line_width in order to trigger a reflow
    of the pretty_repr output with smaller width.
    """
    if height == 1 and pretty_printer == PrettyPrinterLib.RICH:
        return 2
    return 1


def _adjusted_multi_line_pretty_repr(
    draft: DraftOutput[ContentT, FrameT],
    mono_draft: DraftMonospacedOutput[FrameWithWidth],
) -> DraftMonospacedOutput[FrameT]:
    # assert has_width_and_height(draft.frame.dims)
    prev_max_container_width = None
    if frame_has_width_and_height(mono_draft.frame):
        width_to_height_ratio = mono_draft.frame.dims.width / mono_draft.frame.dims.height
    else:
        width_to_height_ratio = None

    while True:
        max_container_width = mono_draft.max_container_width
        if mono_draft.frame.dims.width >= mono_draft.dims.width:
            if width_to_height_ratio is not None:
                if mono_draft.dims.height * width_to_height_ratio >= mono_draft.dims.width:
                    break
            else:
                break

        if (prev_max_container_width is not None
                and prev_max_container_width <= max_container_width):
            break
        else:
            prev_max_container_width = max_container_width

        reflow_delta_line_width = _get_reflow_delta_line_width(draft.config.pretty_printer,
                                                               mono_draft.dims.height)
        mono_draft = _basic_pretty_repr(
            DraftOutput(draft.content, frame=mono_draft.frame, config=draft.config),
            max_line_width=mono_draft.dims.width - reflow_delta_line_width,
            max_container_width=max_container_width - 1,
        )

    return DraftMonospacedOutput(mono_draft.content, frame=draft.frame, config=draft.config)


def pretty_repr_of_draft_output(
        in_draft: DraftOutput[ContentT, FrameT]) -> DraftMonospacedOutput[FrameT]:
    if is_model_instance(in_draft.content) and not in_draft.config.debug_mode:
        data = in_draft.content.to_data()
    else:
        data = in_draft.content

    draft = DraftOutput(data, frame=in_draft.frame, config=in_draft.config)

    mono_draft = _basic_pretty_repr(
        draft,
        max_line_width=draft.frame.dims.width,
        max_container_width=draft.frame.dims.width,
    )

    if frame_has_width(mono_draft.frame):
        if (_is_nested_structure(draft)
                or not mono_draft.within_frame.width) \
                and mono_draft.within_frame.height in (True, None):
            mono_draft = _adjusted_multi_line_pretty_repr(
                draft,
                DraftMonospacedOutput(
                    mono_draft.content, frame=mono_draft.frame, config=draft.config),
            )
    return mono_draft
