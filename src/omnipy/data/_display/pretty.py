import re
from typing import NamedTuple

from devtools import PrettyFormat
from rich.pretty import pretty_repr as rich_pretty_repr

from omnipy.data._display.config import PrettyPrinterLib
from omnipy.data._display.draft import ContentT, DraftMonospacedOutput, DraftOutput, FrameT
from omnipy.data._display.frame import frame_has_width_and_height, FrameWithWidthAndHeight
from omnipy.data.typechecks import is_model_instance

MAX_WIDTH = 2**16 - 1


class ReprMeasures(NamedTuple):
    num_lines: int
    max_line_width: int
    max_container_width: int


def _max_container_width(repr_lines: list[str]) -> int:
    def _max_container_length_in_line(line):
        # Find all containers in the line using regex
        containers = re.findall(r'\{.*\}|\[.*\]|\(.*\)', line)
        # Return the length of the longest container, or 0 if none are found
        return max((len(container) for container in containers), default=0)

    # Calculate the maximum container width across all lines
    return max((_max_container_length_in_line(line) for line in repr_lines), default=0)


def _any_abbrev_containers(repr_str: str) -> bool:
    return bool(re.search(r'\[...\]|\(...\)|\{...\}', repr_str))


def _is_nested_structure(draft: DraftOutput) -> bool:
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
                pf = PrettyFormat(
                    indent_step=draft.config.indent_tab_size,
                    simple_cutoff=max_container_width,
                    width=max_line_width + 1,
                )
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
    mono_draft: DraftMonospacedOutput[FrameWithWidthAndHeight],
) -> DraftMonospacedOutput[FrameT]:
    # assert has_width_and_height(draft.frame.dims)
    prev_max_container_width = None
    width_to_height_ratio = mono_draft.frame.dims.width / mono_draft.frame.dims.height

    while True:
        max_container_width = _max_container_width(mono_draft.content.splitlines())
        if (mono_draft.frame.dims.width >= mono_draft.dims.width
                and mono_draft.dims.height * width_to_height_ratio >= mono_draft.dims.width):
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

    if frame_has_width_and_height(mono_draft.frame):

        if _is_nested_structure(draft) or not mono_draft.within_frame.width:
            mono_draft = _adjusted_multi_line_pretty_repr(
                draft,
                DraftMonospacedOutput(
                    mono_draft.content, frame=mono_draft.frame, config=draft.config),
            )
    return mono_draft
