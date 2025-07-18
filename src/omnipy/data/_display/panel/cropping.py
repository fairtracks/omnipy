import rich.console

from omnipy.data._display.config import OutputConfig
from omnipy.data._display.dimensions import has_width
from omnipy.data._display.frame import AnyFrame
from omnipy.data._display.helpers import UnicodeCharWidthMap
from omnipy.data._display.panel.draft.monospaced import _calc_line_stats
from omnipy.shared.enums.display import HorizontalOverflowMode, VerticalOverflowMode
import omnipy.util._pydantic as pyd
from omnipy.util.helpers import strip_and_split_newline


def rich_overflow_method(
    horizontal_overflow_mode: HorizontalOverflowMode.Literals
) -> rich.console.OverflowMethod | None:
    match horizontal_overflow_mode:
        case HorizontalOverflowMode.ELLIPSIS:
            return 'ellipsis'
        case HorizontalOverflowMode.CROP:
            return 'crop'
        case HorizontalOverflowMode.WORD_WRAP:
            return None


def crop_content_lines_vertically_for_resizing(
    content_lines: list[str],
    frame: AnyFrame,
    vertical_overflow_mode: VerticalOverflowMode.Literals,
) -> list[str]:
    """
    Crop content lines vertically to allow width resizing. No cropping will
    take place if the panel frame width is fixed or equal to 0.

    :param content_lines: All content lines as a list, including newlines
    :param frame: Inner panel frame
    :param vertical_overflow_mode: Configured vertical overflow mode,
                                   specifying e.g. type of cropping
                                   (ellipsis or plain).
    :return: The cropped content lines
    """
    # If both frame dimensions are specified, the frame height is less
    # than the number of lines, and the frame width is defined as flexible
    # (fixed_width=False), then we need to crop the content to fit the frame
    # so that the width of the panel can be reduced to fit only what is in
    # the frame. Otherwise (and the default) is that the panel is wide
    # enough to support the maximum width over all lines, also those out of
    # frame.
    #
    # TODO: Add support for scrolling of text content, not just
    #       cropping from bottom

    if has_width(frame.dims) and frame.dims.width == 0 or frame.fixed_width is True:
        return content_lines

    return crop_content_lines_vertically(
        content_lines,
        frame.dims.height,
        vertical_overflow_mode,
    )


def crop_content_lines_vertically(
    lines: list[str],
    crop_height: pyd.NonNegativeInt | None,
    vertical_overflow_mode: VerticalOverflowMode.Literals,
) -> list[str]:
    """
    Crop content lines vertically according to frame height and configured
    vertical overflow mode.

    :param lines: All content lines as a list, including newlines
    :param crop_height: Max height of the resulting cropped content
    :param vertical_overflow_mode: Configured vertical overflow mode,
                                   specifying e.g. type of cropping
                                   (ellipsis or plain).
    :return: The cropped content lines as a list.
    """
    cropped_lines, ellipsis_line_indices = crop_content_lines_vertically2(
        lines,
        crop_height,
        vertical_overflow_mode,
    )
    replace_ellipsis_lines_with_ellipses(cropped_lines, ellipsis_line_indices)

    return cropped_lines


def replace_ellipsis_lines_with_ellipses(
    cropped_lines: list[str],
    ellipsis_line_indices: set[int],
) -> list[str]:
    for line_idx in ellipsis_line_indices:
        stripped_line, newline = strip_and_split_newline(cropped_lines[line_idx])
        if len(stripped_line) > 0:
            cropped_lines[line_idx] = '…' + newline
    return cropped_lines


def crop_content_lines_vertically2(
    lines: list[str],
    crop_height: pyd.NonNegativeInt | None,
    vertical_overflow_mode: VerticalOverflowMode.Literals,
) -> tuple[list[str], set[int]]:
    """
    Crop content lines vertically according to frame height and configured
    vertical overflow mode.

    :param lines: All content lines as a list, including newlines
    :param crop_height: Max height of the resulting cropped content
    :param vertical_overflow_mode: Configured vertical overflow mode,
                                   specifying e.g. type of cropping
                                   (ellipsis or plain).
    :return: A tuple. The first item is the cropped content lines as a list
             and the second item is the set of indices (line numbers) of the
             lines that have been horizontally cropped, i.e. where
             characters have been removed (due to ellipsis cropping etc.).
    """
    if crop_height is None or len(lines) <= crop_height:
        return lines, set()

    if crop_height == 0:
        return [], set()

    match vertical_overflow_mode:
        case VerticalOverflowMode.CROP_BOTTOM:
            return lines[:crop_height], set()

        case VerticalOverflowMode.CROP_TOP:
            return lines[-crop_height:], set()

        case VerticalOverflowMode.ELLIPSIS_BOTTOM:
            ellipsis_line_idx = crop_height - 1
            uncropped_lines = lines[:ellipsis_line_idx + 1]
            return uncropped_lines, {ellipsis_line_idx}

        case VerticalOverflowMode.ELLIPSIS_TOP:
            ellipsis_line_idx = len(lines) - crop_height - 1
            uncropped_lines = lines[ellipsis_line_idx + 1:]
            return uncropped_lines, {0}

        case _:
            raise ValueError(f'Unknown vertical overflow mode: {vertical_overflow_mode}')


def crop_content_line_horizontally(
    content_line: str,
    frame_width: pyd.NonNegativeInt | None,
    horizontal_overflow_mode: HorizontalOverflowMode.Literals,
) -> str:
    if frame_width is None or len(content_line) <= frame_width:
        return content_line

    match horizontal_overflow_mode:
        case HorizontalOverflowMode.ELLIPSIS:
            if frame_width > 1:
                return content_line[:frame_width - 1] + '…'
            else:
                return '…'
        case HorizontalOverflowMode.CROP:
            return content_line[:frame_width]
        case HorizontalOverflowMode.WORD_WRAP:
            return content_line
        case _:
            raise ValueError(f'Unknown horizontal overflow mode: {horizontal_overflow_mode}')


def crop_content_with_extra_wide_chars(
    all_content_lines: list[str],
    frame: AnyFrame,
    config: OutputConfig,
    char_width_map: UnicodeCharWidthMap,
) -> list[str]:
    if has_width(frame.dims) \
            and frame.fixed_width is False \
            and frame.dims.width > 0:

        ellipsis_if_overflow = config.h_overflow == HorizontalOverflowMode.ELLIPSIS

        for i, (line, newline) in enumerate(strip_and_split_newline(_) for _ in all_content_lines):

            stats = _calc_line_stats(
                line,
                config.tab,
                char_width_map,
                width_limit=frame.dims.width,
            )

            cropped_line = line[:stats.char_count]

            if stats.overflow and ellipsis_if_overflow:
                if stats.line_width == frame.dims.width > 0:
                    # Exactly at the limit, must remove the last character
                    # to have space for the ellipsis
                    cropped_line = cropped_line[:-1]
                cropped_line += '…'

            cropped_line = cropped_line.rstrip('\t')

            all_content_lines[i] = cropped_line + newline

    return all_content_lines
